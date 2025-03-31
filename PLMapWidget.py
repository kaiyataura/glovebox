from pyqtgraph import LayoutWidget, CircleROI, PolyLineROI, Point
from PyQt5.QtWidgets import QLabel, QDoubleSpinBox, QPushButton, QCheckBox, QGraphicsEllipseItem
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPen
import numpy as np
import datetime
import threading, multiprocessing
import sys
from computer_info import computer
if computer == 'glovebox': sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\PLMapGUI')
else: sys.path.append('Scripts/PLMapGUI')
from PLMapGUI import PLMapGUI
import time

class PLMapWidget(LayoutWidget):
    PLMapFinishedSignal = pyqtSignal()
    signal = pyqtSignal(float, float)
    def __init__(self, main):
        super().__init__()
        from GloveboxWindow import GloveboxWindow # for autocomplete
        self.main:GloveboxWindow = main
        self.camera = self.main.devices.camera
        self.objective = self.main.devices.objective
        self.controller = self.main.devices.controller
        self.shutter = self.main.devices.shutter
        self.stage = self.main.devices.stage

    def createGUI(self):
        self.addWidget(QLabel('Map Width:'), 0, 0,)
        self.mapWidthLabel = QLabel('-- µm')
        self.addWidget(self.mapWidthLabel, 0, 1)

        self.addWidget(QLabel(u'Map Height:'), 1, 0)
        self.mapHeightLabel = QLabel('-- µm')
        self.addWidget(self.mapHeightLabel, 1, 1)
        
        self.startPLMapButton = QPushButton('Start PL Map')
        self.startPLMapButton.clicked.connect(self.startPLMap)
        self.addWidget(self.startPLMapButton, 2, 0, 1, 4)
        self.PLMapFinishedSignal.connect(self.finishPLMap)

        self.cancelPLMapButton = QPushButton('Cancel PL Map')
        self.cancelPLMapButton.clicked.connect(self.cancelPLMap)
        self.cancelPLMapButton.hide()
        self.addWidget(self.cancelPLMapButton, 3, 0, 1, 4)

        self.polylineROI = PolyLineROI([(50,50), (50,100), (100,100), (100,50)], closed=True)
        self.polylineROI.sigRegionChanged.connect(self.updateMapSizeLabels)
        self.objective.scale
        self.polylineROI.hide()
        self.main.ImageWidget.addItem(self.polylineROI)
        
        self.laserCircleROI = CircleROI((10e-6, 10e-6), radius=10e-6)
        self.laserCircleROI.hide()
        self.main.ImageWidget.addItem(self.laserCircleROI)

        self.showROIsCheckBox = QCheckBox('Show Helper Tools')
        self.showROIsCheckBox.stateChanged.connect(self.polylineROI.setVisible)
        self.showROIsCheckBox.stateChanged.connect(self.laserCircleROI.setVisible)
        self.addWidget(self.showROIsCheckBox, 4, 0, 1, 2)
        
        self.addWidget(QLabel('Step Size (µm):'), 5, 0, 1, 2)
        self.stepSizeSpinBox = QDoubleSpinBox()
        self.stepSizeSpinBox.setRange(0.1, 5)
        self.stepSizeSpinBox.setValue(0.5)
        self.addWidget(self.stepSizeSpinBox, 5, 3, 1, 2)
        
        self.signal.connect(lambda x,y: self.main.PositionListWidget.savePoint(pos=(x, y, 0))) # temporary

    def updateMapSizeLabels(self):
        rect = self.polylineROI.boundingRect()
        self.mapWidthLabel.setText(f'{rect.width():.1f} µm')
        self.mapHeightLabel.setText(f'{rect.height():.1f} µm')
    
    def cancelPLMap(self):
        self.cancelled = True

    def startPLMap(self):
        if self.main.SpectrometerWidget.SpectrometerWidget == None: return print("Spectrometer not connected! Abort scan!")

        if self.main.SpectrometerWidget.SpectrometerWidget.ContinousMode:
            self.main.SpectrometerWidget.SpectrometerWidget.ContinousModeEnabledCheckbox.setChecked(False)
            self.main.SpectrometerWidget.SpectrometerWidget.ContinousMode = False
            
        self.controller.setControllerEnabled(False, True)
        self.shutter.setOpen(True)
        
        self.cancelPLMapButton.show()
        self.startPLMapButton.hide()

        self.cancelled = False
        
        # TODO: disable app settings

        self.queue = multiprocessing.Queue() # this queue system comes from the original GloveBoxSetupGUI code
        self.window = PLMapGUI(self.queue)
        self.window.show()

        self.scanThread = threading.Thread(target=self.runPLMap)
        self.scanThread.start()

    def runPLMap(self):
        savePosition = self.stage.getPosition()

        stepSize = self.stepSizeSpinBox.value()
        polygon = self.polylineROI.shape().toFillPolygon()
        boundingBox = self.polylineROI.boundingRect()
        xOffsets = np.arange(0, boundingBox.width() + stepSize, stepSize)
        yOffsets = np.arange(0, boundingBox.height() + stepSize, stepSize)

        shift = self.laserCircleROI.pos() + self.laserCircleROI.size() / 2 - boundingBox.topLeft() - self.polylineROI.pos()
        startX = savePosition[0] - shift.x()
        startY = savePosition[1] + shift.y()

        wl = self.main.SpectrometerWidget.SpectrometerWidget.wl_calibration
        data = np.zeros((len(xOffsets) * len(yOffsets) + 1, len(wl) + 2))
        data[0, 2:] = wl

        # send sizes to the subprocess
        self.queue.put(['SxSy', len(xOffsets) * len(yOffsets), len(wl)])
        self.queue.put(['wl', wl])
        self.queue.put(['Ux', startX + xOffsets])
        self.queue.put(['Uy', startY + yOffsets])

        count = 0
        for yOffset in yOffsets:
            if self.cancelled: break
            for xOffset in xOffsets:
                if self.cancelled: break 
                count += 1
                x = startX + xOffset
                y = startY + yOffset

                if polygon.containsPoint(Point(boundingBox.left() + xOffset, boundingBox.top() + yOffset), Qt.FillRule.WindingFill):
                    self.stage.setX(x)
                    self.stage.setY(y)
                    self.signal.emit(x, y)
                    spec = self.main.SpectrometerWidget.SpectrometerWidget.takeSpectrum()     
                else:
                    spec = np.zeros(len(wl))

                data[count, 0] = x
                data[count, 1] = y
                data[count, 2:] = spec
                self.queue.put(['spec', x, y, count - 1, spec])

        if computer == 'glovebox': path = r'C:\Users\GloveBox\Documents\Python Scripts\PLMapGUI\SavedPLMapData/'
        else: path = 'PLMapData/'
        currentTimeFull = datetime.datetime.now()
        path = path + currentTimeFull.strftime('%Y-%m-%d_%H-%M-%S')        
        np.savetxt(path, data, delimiter='\t')
        
        self.stage.setPosition(*savePosition)
            
        self.PLMapFinishedSignal.emit()
        
    def finishPLMap(self):
        self.controller.setControllerEnabled(True, useSave=True)
        self.shutter.setOpen(False)
        self.cancelPLMapButton.hide()
        self.startPLMapButton.show()

if __name__ == '__main__': import Glovebox