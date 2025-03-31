from pyqtgraph import LayoutWidget
from PyQt5.QtWidgets import QSlider, QLabel, QDoubleSpinBox, QPushButton, QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class StageControlWidget(LayoutWidget):
    def __init__(self, main):
        super().__init__()
        from GloveboxWindow import GloveboxWindow # for autocomplete
        self.main:GloveboxWindow = main
        self.stage = self.main.devices.stage
        self.objective = self.main.devices.objective
        self.controller = self.main.devices.controller
        self.polarizer = self.main.devices.polarizer
        self.cameraSettings = self.main.CameraSettingsWidget

    def createGUI(self):
        self.addWidget(QLabel('XY Speed: '), 0, 0)
        xySpeedSlider = QSlider(Qt.Orientation.Horizontal)
        xySpeedSlider.setRange(1, 100)
        xySpeedSlider.setTickInterval(10)
        xySpeedSlider.setTickPosition(QSlider.TickPosition.TicksAbove)
        xySpeedSlider.setValue(int(self.stage.getXYSpeed()))
        xySpeedSlider.sliderMoved.connect(lambda: self.stage.setXYSpeed(xySpeedSlider.value()))
        self.stage.xySpeedChangedSignal.connect(xySpeedSlider.setValue)
        self.addWidget(xySpeedSlider, 0, 1, 1, 3)
        
        self.addWidget(QLabel('Z Speed: '), 1, 0)
        zSpeedSlider = QSlider(Qt.Orientation.Horizontal)
        zSpeedSlider.setRange(1, 100)
        zSpeedSlider.setTickInterval(10)
        zSpeedSlider.setTickPosition(QSlider.TickPosition.TicksAbove)
        zSpeedSlider.setValue(int(self.stage.getZSpeed()))
        zSpeedSlider.sliderMoved.connect(lambda: self.stage.setZSpeed(zSpeedSlider.value()))
        self.stage.zSpeedChangedSignal.connect(zSpeedSlider.setValue)
        self.addWidget(zSpeedSlider, 1, 1, 1, 3)
        
        self.xPositionLabel = QLabel('--')
        self.yPositionLabel = QLabel('--')
        self.zPositionLabel = QLabel('--')
        self.objectivePositionLabel = QLabel('--')
        self.linPolLabel = QLabel('--')
        self.HWPLabel = QLabel('--')
        
        moveXToSpinBox = QDoubleSpinBox()
        moveXToSpinBox.setRange(0, 110)
        moveXToSpinBox.lineEdit().returnPressed.connect(lambda: self.stage.setX(moveXToSpinBox.value()))
        moveXToSpinBox.installEventFilter(self)
        self.addWidget(moveXToSpinBox, 2, 2)
        
        moveYToSpinBox = QDoubleSpinBox()  
        moveYToSpinBox.setRange(0, 75)
        moveYToSpinBox.lineEdit().returnPressed.connect(lambda: self.stage.setY(moveYToSpinBox.value()))
        moveYToSpinBox.installEventFilter(self)
        self.addWidget(moveYToSpinBox, 3, 2)

        moveZToSpinBox = QDoubleSpinBox()
        moveZToSpinBox.setRange(0, 150)
        moveZToSpinBox.lineEdit().returnPressed.connect(lambda: self.stage.setZ(moveZToSpinBox.value()))
        moveZToSpinBox.installEventFilter(self)
        self.addWidget(moveZToSpinBox, 4, 2)

        moveMCMToSpinBox = QDoubleSpinBox()
        moveMCMToSpinBox.setRange(-5000, 5000)
        moveMCMToSpinBox.setDecimals(4)
        moveMCMToSpinBox.lineEdit().returnPressed.connect(lambda: self.objective.setZ(moveMCMToSpinBox.value()))
        moveMCMToSpinBox.installEventFilter(self)
        self.addWidget(moveMCMToSpinBox, 5, 2)

        moveLinPolToSpinBox = QDoubleSpinBox()
        moveLinPolToSpinBox.setRange(0, 360)
        moveLinPolToSpinBox.lineEdit().returnPressed.connect(lambda: self.polarizer.setLPAngle(moveLinPolToSpinBox.value()))
        moveLinPolToSpinBox.installEventFilter(self)
        self.addWidget(moveLinPolToSpinBox, 6, 2)

        moveHWPToSpinBox = QDoubleSpinBox()
        moveHWPToSpinBox.setRange(0, 360)
        moveHWPToSpinBox.lineEdit().returnPressed.connect(lambda: self.polarizer.setHWPAngle(moveHWPToSpinBox.value()))
        moveHWPToSpinBox.installEventFilter(self)
        self.addWidget(moveHWPToSpinBox, 7, 2)
        
        btn = QPushButton('Set X')
        btn.clicked.connect(lambda: self.stage.setX(moveXToSpinBox.value()))
        self.addWidget(btn, 2, 3)
        btn = QPushButton('Set Y')
        btn.clicked.connect(lambda: self.stage.setY(moveYToSpinBox.value()))
        self.addWidget(btn, 3, 3)
        btn = QPushButton('Set Z')
        btn.clicked.connect(lambda: self.stage.setZ(moveZToSpinBox.value()))
        self.addWidget(btn, 4, 3)
        btn = QPushButton('Set MCM')
        btn.clicked.connect(lambda: self.objective.setZ(moveMCMToSpinBox.value()))
        self.addWidget(btn, 5, 3)        
        btn = QPushButton('Set Analyzer')
        btn.clicked.connect(lambda: self.polarizer.setLPAngle(moveLinPolToSpinBox.value()))
        self.addWidget(btn, 6, 3)
        btn = QPushButton('Set HWP')
        btn.clicked.connect(lambda: self.polarizer.setHWPAngle(moveHWPToSpinBox.value()))
        self.addWidget(btn, 7, 3)
        
        self.addWidget(QLabel('X: '), 2, 0)
        self.addWidget(self.xPositionLabel, 2, 1)
        self.addWidget(QLabel('Y: '), 3, 0)
        self.addWidget(self.yPositionLabel, 3, 1)
        self.addWidget(QLabel('Z: '), 4, 0)
        self.addWidget(self.zPositionLabel, 4, 1)
        self.addWidget(QLabel('Coarse Z: '), 5, 0)
        self.addWidget(self.objectivePositionLabel, 5, 1)
        self.addWidget(QLabel('LP: '), 6, 0)
        self.addWidget(self.linPolLabel, 6, 1)
        self.addWidget(QLabel('HWP: '), 7, 0)
        self.addWidget(self.HWPLabel, 7, 1)

        btn = QPushButton('Home X, Y')
        btn.clicked.connect(self.stage.home)
        self.addWidget(btn, 8, 0, 1, 2)

        self.loadSampleButton = QPushButton('Unload Sample')
        self.loadSampleButton.clicked.connect(self.loadSample)
        self.sampleLoaded = True
        self.addWidget(self.loadSampleButton, 8, 2, 1, 2)
        self.stage.xChangedSignal.connect(lambda: self.setSampleLoaded(True))
        self.stage.yChangedSignal.connect(lambda: self.setSampleLoaded(True))

        self.alignSpectrometerButton = QPushButton("Align Spectrometer")
        self.alignSpectrometerButton.clicked.connect(self.alignSpectrometer)
        self.spectrometerAligned = False
        self.addWidget(self.alignSpectrometerButton, 9, 0, 1, 2)
        self.stage.xChangedSignal.connect(lambda: self.setSpectrometerAligned(False))
        self.stage.yChangedSignal.connect(lambda: self.setSpectrometerAligned(False))

        self.lockMCMCheckbox = QCheckBox('Lock MCM')
        self.lockMCMCheckbox.stateChanged.connect(self.lockMCM)
        self.objective.lockChangedSignal.connect(self.lockMCMCheckbox.setChecked)
        self.addWidget(self.lockMCMCheckbox, 9, 2, 1, 2)

        turtle = QIcon("GloveboxData/turtle.png") 
        self.slowModeCheckbox = QCheckBox()
        self.slowModeCheckbox.stateChanged.connect(self.slowMode)
        self.slowModeCheckbox.setIcon(turtle)
        self.addWidget(self.slowModeCheckbox, 10, 1, 1, 1)

        rabbit = QIcon("GloveboxData/rabbit.png") 
        self.fastModeCheckbox = QCheckBox()
        self.fastModeCheckbox.stateChanged.connect(self.fastMode)
        self.fastModeCheckbox.setIcon(rabbit)
        self.addWidget(self.fastModeCheckbox, 10, 0, 1, 1)

        lockAnalyzerCheckbox = QCheckBox('Lock Analyzer')
        lockAnalyzerCheckbox.stateChanged.connect(self.polarizer.setLocked)
        self.polarizer.lockChangedSignal.connect(lockAnalyzerCheckbox.setChecked)
        if 'lockAnalyzer' in self.main.oldGUIState: lockAnalyzerCheckbox.setChecked(self.main.oldGUIState['lockAnalyzer'])
        if 'rotationOffset' in self.main.oldGUIState: self.polarizer.setOffset(self.main.oldGUIState['rotationOffset'])
        self.addWidget(lockAnalyzerCheckbox, 10, 2, 1, 2)
        
    def lockMCM(self, locked):
        self.objective.setMCMLocked(locked)
        self.lockMCMCheckbox.setText(f'MCM locked at {self.objectivePositionLabel.text()}' if locked else 'Lock MCM')

    def slowMode(self, slow:bool):
        self.stage.speedMode = 'slow' if slow else 'normal'
        self.fastModeCheckbox.setChecked(False)

    def fastMode(self, fast:bool):
        self.stage.speedMode = 'fast' if fast else 'normal'
        self.slowModeCheckbox.setChecked(False)

    def loadSample(self):
        if self.sampleLoaded:
            self.cameraSettings.objectiveCombobox.setCurrentIndex(0)
            self.previousX = self.stage.getX()
            self.previousY = self.stage.getY()
            self.stage.setX(0)
            self.stage.setY(75)
            self.setSampleLoaded(False)
        else:
            self.stage.setX(self.previousX)
            self.stage.setY(self.previousY)
            self.setSampleLoaded(True)

    def setSampleLoaded(self, loaded:bool):
        self.sampleLoaded = loaded
        self.loadSampleButton.setText('Unload Sample' if loaded else 'Load Sample')   

    def alignSpectrometer(self):
        if self.spectrometerAligned:
            self.stage.setX(self.previousX)
            self.stage.setY(self.previousY)
            self.setSpectrometerAligned(False)
        else:
            self.previousX = self.stage.getX()
            self.previousY = self.stage.getY()
            self.stage.setX(2.328)
            self.stage.setY(74.941)
            self.setSpectrometerAligned(True)

    def setSpectrometerAligned(self, aligned:bool):
        # GaAs - 870 nm - (x,y) = (5.22, 71.02)
        self.spectrometerAligned = aligned
        self.alignSpectrometerButton.setText('Go Back' if aligned else 'Align Spectrometer')    
    
    def eventLoop(self):
        self.xPositionLabel.setText('%.4f' % self.stage.getX())
        self.yPositionLabel.setText('%.4f' % self.stage.getY())
        self.zPositionLabel.setText('%.4f' % self.stage.getZ())
        self.objectivePositionLabel.setText('%.4f' % self.objective.getZ())
        self.linPolLabel.setText('%.4f' % self.polarizer.getLPAngle())
        self.HWPLabel.setText('%.4f' % self.polarizer.getHWPAngle())

if __name__ == '__main__': import Glovebox