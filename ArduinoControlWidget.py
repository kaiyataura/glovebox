from pyqtgraph import LayoutWidget
from PyQt5.QtWidgets import QLabel, QDoubleSpinBox, QPushButton, QLineEdit

class ArduinoControlWidget(LayoutWidget):
    def __init__(self, main):
        super().__init__()
        from GloveboxWindow import GloveboxWindow # for autocomplete
        self.main:GloveboxWindow = main
        self.camera = self.main.devices.camera
        self.objective = self.main.devices.objective

    def createGUI(self):
        self.addWidget(QLabel('Slider Move Duration (s)'), 0, 0, 1, 1)
        sliderMoveDurationSpinbox = QDoubleSpinBox()
        self.addWidget(sliderMoveDurationSpinbox, 0, 1, 1, 1)
        
        btn = QPushButton('Move Slider Inward')
        btn.clicked.connect(lambda: self.camera.moveSliderInward(sliderMoveDurationSpinbox.value()))
        self.addWidget(btn, 1, 0, 1, 1)
        
        btn = QPushButton('Move Slider Outward')
        btn.clicked.connect(lambda: self.camera.moveSliderOutward(sliderMoveDurationSpinbox.value()))
        self.addWidget(btn, 1, 1, 1, 1)
        
        btn = QPushButton('Home Slider')
        btn.clicked.connect(self.camera.homeSlider)
        self.addWidget(btn, 2, 0, 1, 1)
        
        btn = QPushButton('Restart Slider Arduino')
        btn.clicked.connect(self.camera.restartSlider)
        self.addWidget(btn, 2, 1, 1, 1)
        
        GRBLTextbox = QLineEdit()
        self.addWidget(GRBLTextbox, 3, 0, 1, 2)
        
        btn = QPushButton('Send Objective Wheel GRBL Command')
        btn.clicked.connect(lambda: self.objective.sendWheelCommand(GRBLTextbox.text()))
        self.addWidget(btn, 4, 0, 1, 2)
        
        self.addWidget(QLabel('Step Size'), 5, 0, 1, 1)
        wheelStepSizeSpinbox = QDoubleSpinBox()
        wheelStepSizeSpinbox.setDecimals(4)
        self.addWidget(wheelStepSizeSpinbox, 5, 1, 1, 1)
        
        btn = QPushButton('Step +')
        btn.clicked.connect(lambda: self.objective.setRotation(abs(wheelStepSizeSpinbox.value()), True))
        self.addWidget(btn, 6, 1, 1, 1)
        
        btn = QPushButton('Step -')
        btn.clicked.connect(lambda: self.objective.setRotation(-abs(wheelStepSizeSpinbox.value()), True))
        self.addWidget(btn, 6, 0, 1, 1)
        
        btn = QPushButton('Restart Objective Wheel Arduino')
        def restart():
            self.objective.restartWheel()
            self.main.CameraSettingsWidget.objectiveCombobox.setCurrentIndex(0)
        btn.clicked.connect(restart)
        self.addWidget(btn, 7, 0, 1, 2)
        