from pyqtgraph import LayoutWidget
from PyQt5.QtWidgets import QLabel, QDoubleSpinBox, QPushButton, QCheckBox, QProgressBar
import datetime, os, threading, time
from PyQt5.QtCore import pyqtSignal
import numpy as np
from computer_info import computer
if computer == 'glovebox': import Aidan_quickplot # not sure what this is

class HWPScanWidget(LayoutWidget):
    scanProgressSignal = pyqtSignal()
    scanFinishedSignal = pyqtSignal()
    setSpectrumSignal = pyqtSignal(np.ndarray)
    
    def __init__(self, main):
        super().__init__()
        from GloveboxWindow import GloveboxWindow # for autocomplete
        self.main:GloveboxWindow = main
        self.controller = self.main.devices.controller
        self.shutter = self.main.devices.shutter
        self.polarizer = self.main.devices.polarizer

    def createGUI(self):
        self.addWidget(QLabel("HWP Start: "), 0, 0)
        self.startSpinBox = QDoubleSpinBox()
        self.startSpinBox.setRange(0, 360)
        self.startSpinBox.setValue(0)
        self.addWidget(self.startSpinBox, 0, 1)

        self.addWidget(QLabel("HWP Stop: "), 1, 0)
        self.stopSpinBox = QDoubleSpinBox()
        self.stopSpinBox.setRange(0, 360)
        self.stopSpinBox.setValue(359)
        self.addWidget(self.stopSpinBox, 1, 1)

        self.addWidget(QLabel("HWP Step: "), 2, 0)
        self.stepSpinBox = QDoubleSpinBox()
        self.stepSpinBox.setValue(1)
        self.addWidget(self.stepSpinBox, 2, 1)

        self.startScanButton = QPushButton('Start')
        self.startScanButton.clicked.connect(self.startHWPScan)
        self.addWidget(self.startScanButton, 3, 0, 1, 2)

        self.cancelScanCheckbox = QPushButton('Cancel')
        self.cancelScanCheckbox.clicked.connect(self.cancelHWPScan)
        self.cancelScanCheckbox.hide()
        self.addWidget(self.cancelScanCheckbox, 4, 0, 1, 2)

        self.scanProgressLabel = QLabel('HWP Scan: Not Running')
        self.scanProgressSignal.connect(self.updateProgress)
        self.scanFinishedSignal.connect(self.finishHWPScan)
        self.setSpectrumSignal.connect(self.setSpectrum)
        self.addWidget(self.scanProgressLabel, 5, 0, 1, 2)
        
    def updateProgress(self):
        self.scanProgressLabel.setText(f'HWP Scan: {self.count}/{self.total} ({self.count / self.total:.2%})')

    def cancelHWPScan(self):
        self.cancelled = True

    def setSpectrum(self, spec):
        self.main.SpectrometerWidget.setSpectrumData(spec)

    def startHWPScan(self):
        if self.main.SpectrometerWidget.SpectrometerWidget == None: return print("Spectrometer not connected! Abort scan!")

        self.startScanButton.hide()
        self.cancelScanCheckbox.show()
        self.cancelled = False

        if self.main.SpectrometerWidget.SpectrometerWidget.ContinousMode: # spelling error...
                self.main.SpectrometerWidget.SpectrometerWidget.ContinousModeEnabledCheckbox.setChecked(False)
                self.main.SpectrometerWidget.SpectrometerWidget.ContinousMode = False
            
        self.controller.setControllerEnabled(False, True)
        self.shutter.setOpen(True)

        self.scanThread = threading.Thread(target=self.runHWPScan)
        self.scanThread.start()

    def runHWPScan(self):
        startTimeFull = datetime.datetime.now()
        path = 'HWPScan/' + startTimeFull.strftime('%Y-%m-%d_%H-%M-%S')
        try: os.mkdir(path)
        except OSError:
            self.scanFinishedSignal.emit()
            return print(f'Creation of directory {path} failed')
        path = path + '/'

        angles = np.arange(self.startSpinBox.value(), self.stopSpinBox.value(), self.stepSpinBox.value())
        self.total = len(angles)
        
        for i, angle in enumerate(angles):
            if self.cancelled: break
            self.count = i
            self.scanProgressSignal.emit()
            
            self.polarizer.setHWPAngle(angle)
            if computer == 'glovebox':
                spec = self.main.SpectrometerWidget.SpectrometerWidget.takeSpectrum()
            else: 
                spec = np.zeros(len(self.main.SpectrometerWidget.SpectrometerWidget.wl_calibration))
                time.sleep(0.1)
            self.setSpectrumSignal.emit(spec)
            np.savez(path + str(angle) , spec=spec, wls=self.main.SpectrometerWidget.SpectrometerWidget.wl_calibration, angle=angle )

        self.scanFinishedSignal.emit()

        if computer == 'glovebox':
            plot_func = Aidan_quickplot.plot() # not sure what this is
            plot_func.plotAndFit(path)

    def finishHWPScan(self):
        self.shutter.setOpen(False)
        self.controller.setControllerEnabled(True, True)
        self.scanProgressLabel.setText(f'HWP Scan: {"Cancelled" if self.cancelled else "Finished"}')
        self.startScanButton.show()
        self.cancelScanCheckbox.hide()


if __name__ == '__main__': import Glovebox