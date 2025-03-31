from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

class GloveboxWidget:
    # updateDisplaySignal = pyqtSignal()

    def __init__(self, main):
        # super().__init__()
        from GloveboxWindow import GloveboxWindow # for autocomplete
        self.main:GloveboxWindow = main
        self.camera = self.main.devices.camera
        self.controller = self.main.devices.controller
        self.filterWheel = self.main.devices.filterWheel
        self.objective = self.main.devices.objective
        self.polarizer = self.main.devices.polarizer
        self.shutter = self.main.devices.shutter
        self.stage = self.main.devices.stage
        # self.updateDisplaySignal.connect(self.updateDisplay)
        self.createGUI()

    def createGUI(self):
        pass

    def updateDisplay(self):
        pass

    def eventLoop(self):
        pass