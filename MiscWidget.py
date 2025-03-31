from pyqtgraph import LayoutWidget
import pyqtgraph as pg
from PyQt5.QtWidgets import QPushButton, QLabel, QLineEdit

class MiscWidget(LayoutWidget):
    def __init__(self, main):
        super().__init__()
        from GloveboxWindow import GloveboxWindow # for autocomplete
        self.main:GloveboxWindow = main
        self.camera = self.main.devices.camera
        self.objectives = self.main.devices.objective
        self.filters = self.main.devices.filterWheel
        self.shutter = self.main.devices.shutter

    def createGUI(self):
        btn = QPushButton('Hide Everything')
        # btn.clicked.connect(self.hideEverything)
        self.addWidget(btn, 0, 0, 1, 2)

        btn = QPushButton('RCB')
        # btn.clicked.connect(self.RCBFunc)
        self.RCBMode = False
        self.addWidget(btn, 4, 0, 1, 2)
        
        self.addWidget(QLabel("Savepath:"), 5, 0, 1, 1)
        self.ImageFolderSavePath = QLineEdit("")
        self.addWidget(self.ImageFolderSavePath, 5, 1, 1, 1)

        self.closeButton = QPushButton('Close Program')
        self.closeButton.clicked.connect(self.main.close)
        self.addWidget(self.closeButton, 6, 0, 1, 2)
        
    # def hideEverything(self):
    #     self.main.MiniButtonGroupBox.show()
    #     self.main.CameraSettingsGroupBox.hide()
    #     self.main.PositionListGroupBox.hide()
    #     self.main.ScanGroupBox.hide()
    #     self.main.StageControlGroupBox.hide()
    #     self.main.MiscGroupBox.hide()
    #     self.main.SpectrometerWidgetGroupBox.hide()
    #     self.main.PLMapGroupBox.hide()


    # def toggleRCBMode(self):
    #     if self.RCBMode:
    #         self.Camera.startImageAcquisition()
    #         self.WhiteLightCamera.startImageAcquisition()
    #         self.WhiteLightBlueLightSliderComboBox.setCurrentIndex(self.saveSliderPos)
    #         self.ShutterComboBox.setCurrentIndex(0)
    #         if self.SpectrometerWidget.SpectrometerWidget != None:        
    #             self.SpectrometerWidget.SpectrometerWidget.coolerCheckbox.setChecked(True)
    #     else:
    #         self.Camera.endImageAcquisition()
    #         self.WhiteLightCamera.endImageAcquisition()
    #         self.saveSliderPos = self.WhiteLightBlueLightSliderComboBox.currentIndex()
    #         self.WhiteLightBlueLightSliderComboBox.setCurrentIndex(1)
    #         self.ShutterComboBox.setCurrentIndex(1)
    #         if self.SpectrometerWidget.SpectrometerWidget != None:        
    #             if self.SpectrometerWidget.SpectrometerWidget.ContinousMode:
    #                 self.SpectrometerWidget.SpectrometerWidget.ContinousModeEnabledCheckbox.setChecked(False)
    #             self.SpectrometerWidget.SpectrometerWidget.coolerCheckbox.setChecked(False)

    #     self.RCBMode = not self.RCBMode
      

if __name__ == '__main__': import Glovebox