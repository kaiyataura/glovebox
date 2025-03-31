from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon
from pyqtgraph.dockarea import DockArea, Dock
import DeviceController, ImageWidget, StageLocationWidget, SpectrometerWidget, SpectrumWidget, StageControlWidget, ImageProcessingWidget, ScanWidget, PLMapWidget, HWPScanWidget, PositionListWidget, CameraSettingsWidget, MiscWidget, ControllerWidget, ArduinoControlWidget
import threading, time, pickle
from computer_info import computer

class GloveboxWindow(QMainWindow):
    def __init__(self):      
        super().__init__()
        self.createGUI()
        self.startEventLoop()
        self.startImageEventLoop()

    def createGUI(self):
        if computer == 'glovebox': self.showFullScreen()
        else: self.resize(1500, 1000)

        self.setWindowTitle('Glovebox')
        self.setWindowIcon(QIcon('GloveboxData/microscope.png'))

        self.oldGUIState = {}
        with open('GloveboxData/GUIState.pickle', 'rb') as f:
            self.oldGUIState = pickle.load(f)

        area = DockArea()
        self.setCentralWidget(area)

        self.devices = DeviceController.DeviceController(self)
        
        self.StageLocationWidget = StageLocationWidget.StageLocationWidget(self)
        self.SpectrumWidget = SpectrumWidget.SpectrumWidget(self)                           # TODO
        self.CameraSettingsWidget = CameraSettingsWidget.CameraSettingsWidget(self)         # TODO
        self.StageControlWidget = StageControlWidget.StageControlWidget(self)
        self.SpectrometerWidget = SpectrometerWidget.SpectrometerWidget(self)               # TODO
        self.ImageProcessingWidget = ImageProcessingWidget.ImageProcessingWidget(self)      # TODO
        self.PositionListWidget = PositionListWidget.PositionListWidget(self)               # TODO
        self.MiscWidget = MiscWidget.MiscWidget(self)                                       # TODO
        self.ImageWidget = ImageWidget.ImageWidget(self)                                    # TODO
        self.ScanWidget = ScanWidget.ScanWidget(self)                                       # TODO
        self.PLMapWidget = PLMapWidget.PLMapWidget(self)                                    # TODO
        self.HWPScanWidget = HWPScanWidget.HWPScanWidget(self)                              # TODO
        self.ArduinoControlWidget = ArduinoControlWidget.ArduinoControlWidget(self)
        self.ControllerWidget = ControllerWidget.ControllerWidget(self)                     # TODO

        self.StageLocationWidget.createGUI()
        self.SpectrumWidget.createGUI()
        self.CameraSettingsWidget.createGUI()
        self.StageControlWidget.createGUI()
        self.SpectrometerWidget.createGUI()
        self.ImageProcessingWidget.createGUI()
        self.PositionListWidget.createGUI()
        self.MiscWidget.createGUI()
        self.ImageWidget.createGUI()
        self.ScanWidget.createGUI()
        self.PLMapWidget.createGUI()
        self.HWPScanWidget.createGUI()
        self.ArduinoControlWidget.createGUI()
        self.ControllerWidget.createGUI()
  
        self.StageLocationDock = Dock('Stage Location', widget=self.StageLocationWidget) #, size=(1000,1500))
        self.SpectrumDock = Dock('Spectrum', widget=self.SpectrumWidget)
        self.StageControlDock = Dock('Stage Control', widget=self.StageControlWidget)
        self.SpectrometerDock = Dock('Spectrometer', widget=self.SpectrometerWidget) #, size=(1000,1500))
        self.ImageProcessingDock = Dock('Image Processing', widget=self.ImageProcessingWidget)
        self.ScanDock = Dock('Scan', widget=self.ScanWidget)
        self.PLMapDock = Dock('PL Map', widget=self.PLMapWidget)
        self.HWPScanDock = Dock('HWP Scan', widget=self.HWPScanWidget)
        self.PositionListDock = Dock('Position List', widget=self.PositionListWidget)
        self.CameraSettingsDock = Dock('Camera Settings', widget=self.CameraSettingsWidget)
        self.MiscDock = Dock('Misc', widget=self.MiscWidget)
        self.ControllerDock = Dock('Controller', widget=self.ControllerWidget)
        self.ImageDock = Dock('Image', widget=self.ImageWidget, size=(100,20)) #, size=(1000,1500))
        self.ArduinoControlDock = Dock('Arduino Control', widget=self.ArduinoControlWidget)

        area.addDock(self.ImageDock, 'left')
        area.addDock(self.ArduinoControlDock, 'right', self.ImageDock)
        area.addDock(self.StageControlDock, 'above', self.ArduinoControlDock)
        area.addDock(self.SpectrometerDock, 'right', self.StageControlDock)
        area.addDock(self.ImageProcessingDock, 'right', self.SpectrometerDock)
        area.addDock(self.PLMapDock, 'bottom', self.StageControlDock)
        area.addDock(self.HWPScanDock, 'above', self.PLMapDock)
        area.addDock(self.ScanDock, 'above', self.HWPScanDock)
        
        area.addDock(self.CameraSettingsDock, 'bottom', self.ScanDock)
        area.addDock(self.PositionListDock, 'bottom', self.SpectrometerDock)
        area.addDock(self.MiscDock, 'bottom', self.PositionListDock)
        area.addDock(self.ControllerDock, 'above', self.MiscDock)
        area.addDock(self.SpectrumDock, 'bottom', self.ImageDock)
        area.addDock(self.StageLocationDock, 'above', self.SpectrumDock)
        
        self.ImageProcessingDock.hide()

    def setSettingsEnabled(self, enabled:bool):
        self.StageLocationWidget.setEnabled(enabled)
        self.CameraSettingsWidget.setEnabled(enabled)
        self.StageControlWidget.setEnabled(enabled)
        self.SpectrometerWidget.setEnabled(enabled)
        self.ImageProcessingWidget.setEnabled(enabled)
        self.ControllerWidget.setEnabled(enabled)
        self.ScanWidget.setEnabled(enabled)
        self.PLMapWidget.setEnabled(enabled)
        self.ArduinoControlWidget.setEnabled(enabled)

    def startEventLoop(self):
        self.prevTime = 0
        self.timer = QTimer()
        self.timer.setInterval(40) # 0.040 seconds per tick (25 tps)
        self.timer.timeout.connect(self.eventLoop)
        self.timer.start()

    def startImageEventLoop(self):
        self.runImageEventLoop = True
        def run():
            while self.runImageEventLoop:
                t1 = time.perf_counter()
                self.imageEventLoop()
                t2 = time.perf_counter()
                wait = 0.1 - (t2 - t1) # max 0.1 seconds per frame (10 fps)
                if wait > 0: time.sleep(wait)
        self.eventLoopThread = threading.Thread(target=run)
        self.eventLoopThread.start()
    
    def eventLoop(self):
        t = time.perf_counter()
        self.secPerTick = t - self.prevTime
        self.prevTime = t
        self.ControllerWidget.eventLoop()
        self.StageLocationWidget.eventLoop()
        self.StageControlWidget.eventLoop()

    def imageEventLoop(self):
        self.devices.camera.updateImage()
        self.ImageProcessingWidget.eventLoop()
        self.ImageWidget.eventLoop()
 
    def saveGUIState(self):
        newGUIState = {}
        newGUIState['positions'] = [[self.PositionListWidget.positionsList.item(x).text(), self.PositionListWidget.positionsList.item(x).data(Qt.ItemDataRole.UserRole)] for x in range(self.PositionListWidget.positionsList.count())]
        newGUIState['corners'] = self.ScanWidget.corners

        newGUIState['xStepSize'] = self.ScanWidget.xStepSizeSpinbox.value()
        newGUIState['yStepSize'] = self.ScanWidget.yStepSizeSpinbox.value()
        
        newGUIState['ROIPosition'] = self.ImageWidget.ROI.pos()
        newGUIState['ROISize'] = self.ImageWidget.ROI.size()
        
        newGUIState['lockAnalyzer'] = self.devices.polarizer.getLocked()
        newGUIState['rotationOffset'] = self.devices.polarizer.getOffset()
        
        newGUIState['grayThreshold'] = self.ImageProcessingWidget.grayScaleThresholdLine.pos()
        newGUIState['interestingnessThreshold'] = self.ImageProcessingWidget.interestingnessThresholdLine.pos()
        with open('GloveboxData/GUIState.pickle', 'wb') as f:
            pickle.dump(newGUIState, f)       

    def closeEvent(self, event):
        self.saveGUIState()
        self.timer.stop()
        self.runImageEventLoop = False
        self.ScanWidget.cancelScan()
        self.PLMapWidget.cancelPLMap()
        self.HWPScanWidget.cancelHWPScan()
        self.SpectrometerWidget.close() # close spectrometer in case it is left open
        self.devices.closeDevices()
        return super().closeEvent(event)

if __name__ == '__main__': import Glovebox