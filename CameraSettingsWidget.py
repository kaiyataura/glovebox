from PyQt5.QtWidgets import QLabel, QDoubleSpinBox, QPushButton, QCheckBox, QComboBox
from pyqtgraph import LayoutWidget

class CameraSettingsWidget(LayoutWidget):
    def __init__(self, main):
        super().__init__()
        from GloveboxWindow import GloveboxWindow # for autocomplete
        self.main:GloveboxWindow = main
        self.camera = self.main.devices.camera
        self.objectives = self.main.devices.objective
        self.filters = self.main.devices.filterWheel
        self.shutter = self.main.devices.shutter

    def createGUI(self):
        self.addWidget(QLabel('Exposure Times'), 0, 0, 1, 2)
        self.WLExposureSpinbox = QDoubleSpinBox()
        self.WLExposureSpinbox.setRange(0.1, 5000)
        self.WLExposureSpinbox.setValue(self.camera.getWLExposure())
        self.WLExposureSpinbox.lineEdit().returnPressed.connect(lambda: self.camera.setWLExposure(self.WLExposureSpinbox.value()))
        self.WLExposureSpinbox.installEventFilter(self)
        self.addWidget(self.WLExposureSpinbox, 1, 0)

        btn = QPushButton('Set WL Exposure (ms)')
        btn.clicked.connect(lambda: self.camera.setWLExposure(self.WLExposureSpinbox.value()))
        self.addWidget(btn, 1, 1)
        
        self.PLExposureSpinbox = QDoubleSpinBox()
        self.PLExposureSpinbox.setRange(0.1, 5000)
        self.PLExposureSpinbox.setValue(self.camera.getPLExposure())
        self.PLExposureSpinbox.lineEdit().returnPressed.connect(lambda: self.camera.setPLExposure(self.PLExposureSpinbox.value()))
        self.PLExposureSpinbox.installEventFilter(self)
        self.addWidget(self.PLExposureSpinbox, 2, 0)

        btn = QPushButton('Set PL Exposure (ms)')
        btn.clicked.connect(lambda : self.camera.setPLExposure(self.PLExposureSpinbox.value()))
        self.addWidget(btn, 2, 1)
        
        self.addWidget(QLabel('WL Scaling (Min, Max)'), 3, 0, 1, 2)
        self.WLMinSpinbox = QDoubleSpinBox()
        self.WLMinSpinbox.setRange(-5000, 5000)
        self.WLMinSpinbox.setValue(0)
        self.WLMinSpinbox.lineEdit().returnPressed.connect(lambda: self.camera.setWLLevelMin(self.WLMinSpinbox.value()))
        self.addWidget(self.WLMinSpinbox, 4, 0)
        
        self.WLMaxSpinbox = QDoubleSpinBox()
        self.WLMaxSpinbox.setRange(-5000, 5000)
        self.WLMaxSpinbox.setValue(255)
        self.WLMaxSpinbox.lineEdit().returnPressed.connect(lambda: self.camera.setWLLevelMax(self.WLMinSpinbox.value()))
        self.addWidget(self.WLMaxSpinbox, 4, 1)
        
        self.addWidget(QLabel('PL Scaling (Min, Max)'), 5, 0, 1, 2)
        self.PLMinSpinbox = QDoubleSpinBox()
        self.PLMinSpinbox.setRange(-5000, 5000)
        self.PLMinSpinbox.setValue(0)
        self.PLMinSpinbox.lineEdit().returnPressed.connect(lambda: self.camera.setPLLevelMin(self.PLMinSpinbox.value()))
        self.addWidget(self.PLMinSpinbox, 6, 0)
        
        self.PLMaxSpinbox = QDoubleSpinBox()
        self.PLMaxSpinbox.setRange(-5000, 5000)
        self.PLMaxSpinbox.setValue(100)
        self.PLMaxSpinbox.lineEdit().returnPressed.connect(lambda: self.camera.setPLLevelMax(self.PLMaxSpinbox.value()))
        self.addWidget(self.PLMaxSpinbox, 6, 1)
        
        self.medianBlurCheckbox = QCheckBox('Blur')
        self.medianBlurCheckbox.stateChanged.connect(self.camera.setMedianBlur)
        self.addWidget(self.medianBlurCheckbox, 7, 0, 1, 1)
        
        self.gaussianBlurCheckbox = QCheckBox('Gaussian')
        self.gaussianBlurCheckbox.stateChanged.connect(self.camera.setGaussianBlur)
        self.addWidget(self.gaussianBlurCheckbox, 7, 1, 1, 1)

        self.addWidget(QLabel('Current Objective:'), 8, 0, 1, 1)
        self.objectiveCombobox = QComboBox()
        self.objectiveCombobox.addItem('10x')
        self.objectiveCombobox.addItem('20x')
        self.objectiveCombobox.addItem('50x')
        self.objectiveCombobox.addItem('50xIR')
        self.objectiveCombobox.currentIndexChanged.connect(lambda index: self.objectives.setObjective(self.objectiveCombobox.currentText()))
        self.objectives.objectiveChangedSignal.connect(lambda name: self.objectiveCombobox.setCurrentIndex(self.objectiveCombobox.findText(name)))
        self.addWidget(self.objectiveCombobox, 8, 1, 1, 1)

        self.addWidget(QLabel('Current Slider:'), 9, 0, 1, 1)
        self.lightSelectionCombobox = QComboBox()
        self.lightSelectionCombobox.addItem('White Light', 'WL')
        self.lightSelectionCombobox.addItem('Empty', 'Empty')
        self.lightSelectionCombobox.addItem('Blue Light', 'PL')
        self.lightSelectionCombobox.currentIndexChanged.connect(lambda index: self.camera.setSlider(self.lightSelectionCombobox.currentData()))
        self.camera.sliderChangedSignal.connect(lambda name: self.lightSelectionCombobox.setCurrentIndex(self.lightSelectionCombobox.findData(name)))
        self.addWidget(self.lightSelectionCombobox, 9, 1, 1, 1)

        self.addWidget(QLabel('Current Filter:'), 10, 0, 1, 1)
        self.filterCombobox = QComboBox()
        self.filterCombobox.addItem('LP 600 nm')
        self.filterCombobox.addItem('BP 750 ± 40 nm')
        self.filterCombobox.addItem('BP 750 ± 10 nm')
        self.filterCombobox.addItem('BP 730 ± 10 nm')
        self.filterCombobox.addItem('Empty')
        self.filterCombobox.currentIndexChanged.connect(self.setFilter)
        self.filters.filterChangedSignal.connect(self.filterCombobox.setCurrentIndex)
        self.addWidget(self.filterCombobox, 10, 1, 1, 1)

        self.addWidget(QLabel('Laser Shutter:'), 11, 0, 1, 1)
        self.shutterCombobox = QComboBox()
        self.shutterCombobox.addItem('Open')
        self.shutterCombobox.addItem('Closed')
        self.shutterCombobox.setCurrentIndex(1)
        self.shutterCombobox.currentIndexChanged.connect(lambda index: self.shutter.setOpen(index == 0))
        self.shutter.flipperChangedSignal.connect(lambda open: self.shutterCombobox.setCurrentIndex(0 if open else 1))
        self.addWidget(self.shutterCombobox, 11, 1, 1, 1)

        self.lengthLabel = QLabel('Estimated Length: ?')
        self.addWidget(self.lengthLabel, 12, 0, 1, 2)
        
        btn = QPushButton('Restart PL Camera')
        btn.clicked.connect(self.camera.restartPLCamera)
        self.addWidget(btn, 14, 0, 1, 1)

        btn = QPushButton('Open Image Externally')
        btn.clicked.connect(self.main.ImageWidget.openImageExternally)
        self.addWidget(btn, 13, 0, 1, 2)

        self.resolutionCombobox = QComboBox()
        self.resolutionCombobox.addItem('Full Resolution')
        self.resolutionCombobox.addItem('Half Resolution')
        self.resolutionCombobox.currentIndexChanged.connect(lambda index: self.camera.setWLResolutionDivider(index + 1))
        self.resolutionCombobox.setCurrentIndex(1)
        self.camera.resolutionDividerChangedSignal.connect(lambda divider: self.resolutionCombobox.setCurrentIndex(divider - 1))
        self.addWidget(self.resolutionCombobox, 14, 1, 1, 1)

    def setFilter(self, index):
        self.filters.setFilter(index)
        if index == 4: # If the selected value is the empty position
            self.PLExposureSpinbox.setValue(1)
            self.camera.setPLExposure(1)
            self.PLMaxSpinbox.setValue(110)
            self.camera.setPLLevelMax(110)
        else:
            self.PLExposureSpinbox.setValue(255)
            self.camera.setPLExposure(255)
            self.PLMaxSpinbox.setValue(15)
            self.camera.setPLLevelMax(15)

    def updateLengthLabel(self, length):
        self.lengthLabel.setText(f'Estimated Length: {length} µm')  

if __name__ == '__main__': import Glovebox