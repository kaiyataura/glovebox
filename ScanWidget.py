from pyqtgraph import LayoutWidget
from PyQt5.QtWidgets import QLabel, QDoubleSpinBox, QPushButton, QCheckBox, QComboBox
from PyQt5.QtCore import pyqtSignal
import numpy as np
import cv2 as cv
import pickle, time, datetime, os, threading
from computer_info import computer

class ScanWidget(LayoutWidget):
    scanProgressSignal = pyqtSignal()
    scanFinishedSignal = pyqtSignal()
    def __init__(self, main):
        super().__init__()
        from GloveboxWindow import GloveboxWindow # for autocomplete
        self.main:GloveboxWindow = main
        self.stage = self.main.devices.stage
        self.camera = self.main.devices.camera
        self.controller = self.main.devices.controller
        self.objective = self.main.devices.objective

    def createGUI(self):
        self.addWidget(QLabel('X step size: '), 0, 0)
        self.xStepSizeSpinbox = QDoubleSpinBox()
        self.xStepSizeSpinbox.setValue(self.main.oldGUIState['xStepSize'] if 'xStepSize' in self.main.oldGUIState else 0.3)
        self.addWidget(self.xStepSizeSpinbox, 0, 1)
        
        self.addWidget(QLabel('Y step size: '), 1 , 0)
        self.yStepSizeSpinbox = QDoubleSpinBox()
        self.yStepSizeSpinbox.setValue(self.main.oldGUIState['yStepSize'] if 'yStepSize' in self.main.oldGUIState else 0.3)
        self.addWidget(self.yStepSizeSpinbox, 1, 1)

        self.corners = self.main.oldGUIState['corners'] if 'corners' in self.main.oldGUIState else [None] * 3
        
        def addCornerButton(i):
            btn = QPushButton(f'Set Corner {i}' + ('' if self.corners[i] is None else ' [SET]'))
            def addCorner():
                self.main.StageControlWidget.lockMCMCheckbox.setChecked(True)
                btn.setText(f'Set Corner {i} [SET]')
                self.corners[i] = self.stage.getPosition()
                self.main.PositionListWidget.saveCorner(i)
                self.updatePlane()
                btn.clicked.disconnect(addCorner)
                btn.clicked.connect(resetCorner)
            def resetCorner():
                btn.setText(f'Set Corner {i}')
                self.corners[i] = None
                self.updatePlane()
                btn.clicked.disconnect(resetCorner)
                btn.clicked.connect(addCorner)
            btn.clicked.connect(addCorner if self.corners[i] is None else resetCorner)
            self.objective.zChangedSignal.connect(resetCorner)
            self.addWidget(btn, 2 + i, 0, 1, 1)
            return btn
        self.cornerButtons = []
        for i in range(len(self.corners)): self.cornerButtons.append(addCornerButton(i))
        
        self.setBlankButton = QPushButton('Set Blank Image')
        self.addWidget(self.setBlankButton, 2, 1, 1, 1)
        self.setBlankButton.clicked.connect(self.setBlankImage)
        self.blank = None
        
        self.ROICheckbox = QCheckBox('Show ROI')
        self.ROICheckbox.stateChanged.connect(self.main.ImageWidget.setROIVisible)
        self.addWidget(self.ROICheckbox, 3, 1, 1, 1)

        self.imageProcessingCheckbox = QCheckBox('Do Image Processing')
        self.imageProcessingCheckbox.stateChanged.connect(self.main.ImageProcessingWidget.setImageProcessingEnabled)
        self.addWidget(self.imageProcessingCheckbox, 4, 1, 1, 1)

        self.startScanButton = QPushButton('Start Scan')
        self.startScanButton.clicked.connect(lambda: self.startScan(self.scanTypeComboBox.currentData()))
        self.addWidget(self.startScanButton, 6, 0, 1, 1)
        self.scanProgressSignal.connect(self.updateProgress)
        self.scanFinishedSignal.connect(self.finishScan)

        self.cancelScanButton = QPushButton('Cancel Scan')
        self.cancelScanButton.clicked.connect(self.cancelScan)
        self.cancelScanButton.hide()
        self.addWidget(self.cancelScanButton, 7, 0, 1, 1)
        self.cancelled = False

        self.scanTypeComboBox = QComboBox()
        self.scanTypeComboBox.addItem('PL (Save Interesting)', 'PL')
        self.scanTypeComboBox.addItem('WL (Save All)', 'WL')
        self.scanTypeComboBox.addItem('PL -> WL', 'Both')
        self.scanTypeComboBox.currentIndexChanged.connect(lambda index: self.setPLScanSettingsVisible(index != 1))
        self.PLScanSettingsVisible = True
        self.addWidget(self.scanTypeComboBox, 6, 1, 1, 1)

        self.pauseScanButton = QPushButton('Pause Scan')
        self.pauseScanButton.clicked.connect(lambda: self.pauseScan(not self.paused))
        self.pauseScanButton.hide()
        self.addWidget(self.pauseScanButton, 7, 1, 1, 1)
        self.paused = False

        self.timingLabel = QLabel('[No Scan Running]')
        self.addWidget(self.timingLabel, 8, 0, 1, 2)
        
    def setBlankImage(self):
        if self.camera.getSlider() != 'PL': return
        if computer == 'glovebox': self.blank = self.camera.getPLImage()
        else: self.blank = np.random.randint(10, size=(3092, 5120, 1), dtype='uint8')
        self.setBlankButton.setText('Blank [SET]')
        self.main.ImageProcessingWidget.updateBlankHist()
        self.setBlankButton.clicked.disconnect(self.setBlankImage)
        self.setBlankButton.clicked.connect(self.unsetBlankImage)

    def unsetBlankImage(self):
        self.blank = None
        self.setBlankButton.setText('Set Blank Image')
        self.main.ImageProcessingWidget.updateBlankHist()
        self.setBlankButton.clicked.disconnect(self.unsetBlankImage)
        self.setBlankButton.clicked.connect(self.setBlankImage)

    def setPLScanSettingsVisible(self, show:bool):
        if self.PLScanSettingsVisible == show: return
        self.PLScanSettingsVisible = show
        self.setBlankButton.setVisible(show)
        self.setBlankButton.setVisible(show)
        self.ROICheckbox.setVisible(show)
        self.ROICheckbox.setChecked(False)
        self.imageProcessingCheckbox.setVisible(show)
        self.imageProcessingCheckbox.setChecked(False)

    def updatePlane(self):
        self.plane = None if any(corner is None for corner in self.corners) else self.calcPlane(self.corners)

    def calcPlane(self, ps): # returns list [a, b, c, d] for plane equation ax + by + cz = d
        ap1 = np.array(ps[0]) # position vector
        p1p2 = np.array(ps[1]) - ap1 # vector p1 -> p2
        p1p3 = np.array(ps[2]) - ap1 # vector p1 -> p3
        abcd = np.cross(p1p2, p1p3).tolist() # plane normal vector = coefficeints a,b,c for plane eq
        abcd.append(np.dot(abcd, ap1)) # d = ax + by + cz = (a,b,c) • (x0,y0,z0)
        return abcd
    
    def calcZ(self, x, y, p): # p = (a, b, c, d) for plane equation ax + by + cz = d
        return (p[3] - p[0] * x - p[1] * y) / p[2] # z = (d - ax - by) / c

    def setSettingsEnabled(self, enable:bool):
        self.main.setSettingsEnabled(enable)
        self.setEnabled(True)
        self.xStepSizeSpinbox.setEnabled(enable)
        self.yStepSizeSpinbox.setEnabled(enable)
        for btn in self.cornerButtons:
            btn.setEnabled(enable)
        self.setBlankButton.setEnabled(enable)
        self.imageProcessingCheckbox.setEnabled(enable)

    def startScan(self, scanType:str): # scanType = 'PL', 'WL', or 'Both'
        self.scanType = scanType
        self.currentScanType = 'PL' if scanType == 'Both' else scanType

        if any(corner is None for corner in self.corners): return self.timingLabel.setText('[No Scan Running] - Select 3 Corners')
        if self.currentScanType == 'PL':
            if self.blank is None: return self.timingLabel.setText('[No Scan Running] - Set Blank Image')
            self.imageProcessingCheckbox.setChecked(True)
            self.main.ImageProcessingWidget.setImageProcessingEnabled(True)

        self.setSettingsEnabled(False)
        self.startScanButton.hide()
        self.scanTypeComboBox.hide()
        self.cancelScanButton.show()
        self.pauseScanButton.show()

        self.cancelled = False
        self.paused = False

        self.scanThread = threading.Thread(target=lambda: self.runScan(self.currentScanType))
        self.scanThread.start()

    def pauseScan(self, paused:bool):
        self.pauseScanButton.setText('Unpause Scan' if paused else 'Pause Scan')
        self.paused = paused

    def cancelScan(self):
        self.cancelled = True

    def updateProgress(self):
        self.timingLabel.setText(f'{self.currentScanType} Scan: {self.count}/{self.total} ({self.count / self.total:.2%})\n - Elapsed: {self.elapsedTime / 60:.2f} min - End: {self.finalTime}')

    def finishScan(self):
        self.controller.setControllerEnabled(True, True)
        self.setSettingsEnabled(True)
        self.pauseScanButton.hide()
        self.cancelScanButton.hide()
        self.startScanButton.show()
        self.scanTypeComboBox.show()
        self.timingLabel.setText(f'[No Scan Running] - {self.currentScanType} Scan Finished')
        
        if self.scanType == 'Both': self.startScan('WL')

    def runScan(self, type:str):
        self.objective.setMCMLocked(True)
        self.controller.setControllerEnabled(False, True)
        self.camera.setSlider(type)

        startPosition = self.stage.getPosition()
        startTime = time.time()
        startTimeFull = datetime.datetime.now()
        path = 'ScanImages/' + startTimeFull.strftime('%Y-%m-%d_%H-%M-%S')
        try: os.mkdir(path)
        except OSError: 
            self.scanFinishedSignal.emit()
            return print(f'Creation of directory {path} failed')
        path = path + '/'
       
        cornerData = {}
        cornerData['corners'] = self.corners
        with open(path + 'scanCorners.pickle', 'wb') as f:
            pickle.dump(cornerData, f)

        cornerXY = np.array(self.corners)[:,0:2]
        xMin, yMin = np.amin(cornerXY, axis=0)
        xMax, yMax = np.amax(cornerXY, axis=0)
        xStep, yStep = self.xStepSizeSpinbox.value(), self.yStepSizeSpinbox.value()
        xs = np.arange(xMin, xMax + xStep, xStep)
        ys = np.arange(yMin, yMax + yStep, yStep)
        plane = self.calcPlane(self.corners)
        self.total, self.count = len(ys) * len(xs), 0
            
        forward = True
        for y in ys:
            if self.cancelled: break
            for x in xs if forward else reversed(xs): # scans back and forth
                while self.paused and not self.cancelled: time.sleep(0.2)
                if self.cancelled: break
                z = self.calcZ(x, y, plane)
                self.stage.setPosition(x, y, z)
                self.camera.waitExposure() # sleep
                self.count += 1
                if type == 'WL' or self.main.ImageProcessingWidget.isInteresting():
                    number = self.main.PositionListWidget.savePoint()
                    filename = path + f'Position_{number}_X{self.stage.getX()}_Y{self.stage.getY()}_Z{self.stage.getZ()}.jpg'
                    cv.imwrite(filename, self.camera.getImage())
                self.elapsedTime = time.time() - startTime
                self.finalTime = (startTimeFull + datetime.timedelta(seconds=self.total * self.elapsedTime / self.count)).replace(microsecond=0) 
                self.scanProgressSignal.emit()
            forward = not forward # reverse direction

        self.stage.setPosition(*startPosition)
        self.scanFinishedSignal.emit()

if __name__ == '__main__': import Glovebox