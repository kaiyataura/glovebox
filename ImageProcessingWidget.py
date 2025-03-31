from pyqtgraph import GraphicsLayoutWidget, InfiniteLine
from PyQt5.QtCore import pyqtSignal
import numpy as np
import cv2 as cv

class ImageProcessingWidget(GraphicsLayoutWidget):
    updateDisplaySignal = pyqtSignal()

    def __init__(self, main):
        super().__init__(title='Laplacian')
        from GloveboxWindow import GloveboxWindow # for autocomplete
        self.main:GloveboxWindow = main
        self.camera = self.main.devices.camera

    def createGUI(self):
        plot1 = self.addPlot(title='Color Distribution')
        plot1.setXRange(0, 50, padding=0)
        self.distributionPlot = plot1.plot([0,0,0])
        self.imageHist = []
        self.imagePos = []
        
        self.grayScaleThresholdLine = InfiniteLine(pos=self.main.oldGUIState['grayThreshold'] if 'grayThreshold' in self.main.oldGUIState else 40, angle=90, movable=True, pen=(255,0,0))
        self.grayScaleThresholdLine.sigPositionChangeFinished.connect(self.updateBlankHist)
        plot1.addItem(self.grayScaleThresholdLine)
        
        self.nextRow()
        
        self.interestingnessPlotWindow = plot2 = self.addPlot(title='Reduced Chi Squared With Blank Image')
        self.interestingnessPlot = plot2.plot([0,0,0])
        plot2.addItem(self.interestingnessPlot)
        
        self.interestingnessThresholdLine = InfiniteLine(pos=self.main.oldGUIState['interestingnessThreshold'] if 'interestingnessThreshold' in self.main.oldGUIState else 40, angle=0, movable=True, pen=(255,0,0)) 
            
        plot2.addItem(self.interestingnessThresholdLine)
        self.interestingnessArray = []

        self.enabled = False
        self.blankHist = None
        self.updateDisplaySignal.connect(self.updateDisplay)

    def setImageProcessingEnabled(self, enable:bool):
        self.enabled = enable
        if enable: self.main.ImageProcessingDock.show()
        else: self.main.ImageProcessingDock.hide()

    def updateBlankHist(self):
        blankImage = self.main.ScanWidget.blank
        if blankImage is None: 
            self.blankHist = None
            return
        lowerBound  = int(self.grayScaleThresholdLine.value())
        blankMask = cv.inRange(blankImage, lowerBound, 256)
        self.blankHist = cv.calcHist([blankImage], [0], blankMask, [256], [0, 256])
        
    def calcInterestingness(self, image):
        if self.blankHist is None: return 0
        lowerBound = self.grayScaleThresholdLine.value()
        mask = cv.inRange(image, lowerBound, 256)
        hist = cv.calcHist([image], [0], mask, [256], [0, 256])
        interestingness = cv.compareHist(hist, self.blankHist, cv.HISTCMP_CHISQR)
        return interestingness

    def isInteresting(self):
        return self.interestingness > self.interestingnessThresholdLine.value()

    def updateDisplay(self):
        self.distributionPlot.setData(self.imagePos, self.imageHist, stepMode='center', fillLevel=0, brush=(0,0,255,150))
        self.interestingnessPlot.setData(self.interestingnessArray, pen=(0,0,255))
        self.interestingnessPlotWindow.setXRange(0, 100, padding=0)
        self.main.ImageWidget.setROIDetected(self.isInteresting() if self.enabled and self.camera.getSlider() == 'PL' else None)

    def eventLoop(self):
        if self.enabled and self.camera.getSlider() == 'PL':
            image = self.main.ImageWidget.ROI.getArrayRegion(self.main.ImageWidget.getImageItem().image, self.main.ImageWidget.getImageItem()).astype(np.uint8)
            self.imageHist, self.imagePos = np.histogram(image, bins=100)
            self.interestingness = self.calcInterestingness(image)
            self.interestingnessArray.append(self.interestingness)
            
            if len(self.interestingnessArray) > 100:
                self.interestingnessArray.pop(0)

        self.updateDisplaySignal.emit()

if __name__ == '__main__': import Glovebox