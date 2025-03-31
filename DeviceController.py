from Devices import Camera, Objective, Polarizer, Stage, FilterWheel, Controller, Shutter
from PyQt5.QtWidgets import QProgressBar, QApplication
import time

class DeviceController:
    def __init__(self, main):
        from GloveboxWindow import GloveboxWindow # for autocomplete
        self.main:GloveboxWindow = main
        self.virtual = True
        self.loadDevices()

    def loadDevices(self):
        self.startProgressBar()

        self.stage = Stage.Stage(self.virtual)
        self.updateProgressBar(2)
        self.objective = Objective.Objective(self.virtual)
        self.updateProgressBar(2)
        self.filterWheel = FilterWheel.FilterWheel(self.virtual)
        self.updateProgressBar(1)
        self.polarizer = Polarizer.Polarizer(self.virtual)
        self.updateProgressBar(2)
        self.controller = Controller.Controller(self.virtual)
        self.updateProgressBar(1)
        self.camera = Camera.Camera(self.virtual)
        self.updateProgressBar(3)
        self.shutter = Shutter.Shutter(self.virtual)
        self.updateProgressBar(1)

        self.progressBar.close()

    def closeDevices(self):
        self.startProgressBar()

        self.stage.close()
        self.updateProgressBar(2)
        self.objective.close()
        self.updateProgressBar(2)
        self.filterWheel.close()
        self.updateProgressBar(1)
        self.polarizer.close()
        self.updateProgressBar(2)
        self.controller.close()
        self.updateProgressBar(1)
        self.camera.close()
        self.updateProgressBar(3)
        self.shutter.close()
        self.updateProgressBar(1)

        self.progressBar.close()

    def startProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setMaximum(12)
        self.progressBar.show()
        QApplication.processEvents()

    def updateProgressBar(self, n):
        time.sleep(0.05)
        self.progressBar.setValue(self.progressBar.value() + n)
        QApplication.processEvents()

if __name__ == '__main__': import Glovebox