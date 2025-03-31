from pyqtgraph import ImageView, ROI, LineSegmentROI
import pyqtgraph as pg
import numpy as np
from PyQt5.QtCore import pyqtSignal

class ImageWidget(ImageView):
    updateDisplaySignal = pyqtSignal()
    def __init__(self, main):
        super().__init__()
        from GloveboxWindow import GloveboxWindow # for autocomplete
        self.main:GloveboxWindow = main
        self.camera = self.main.devices.camera
        self.objective = self.main.devices.objective
        self.settings = self.main.CameraSettingsWidget

    def createGUI(self):
        self.getHistogramWidget().setHistogramRange(0, 255)
        if 'ROIPosition' in self.main.oldGUIState and 'ROISize' in self.main.oldGUIState:
            self.ROI = ROI(self.main.oldGUIState['ROIPosition'], self.main.oldGUIState['ROISize'])
        else: self.ROI = ROI((20,20), (100,100))
        self.ROI.hide()
        self.ROI.addScaleHandle((1,1), (0,0))
        self.addItem(self.ROI)

        hist = self.getHistogramWidget()
        hist.sigLevelChangeFinished.connect(self.updateSpinboxesFromHistogram)
        hist.sigLevelsChanged.connect(self.suppressRender)
        self.setLevels(0, 255)
        
        self.measurementLine = LineSegmentROI([[100,10], [150,10]], pen = (255, 0, 0))
        self.measurementLine.sigRegionChanged.connect(lambda scale: self.updateMeasurementLineLabel())
        self.addItem(self.measurementLine)
        self.updateMeasurementLineLabel()

        self.autoScaleRequired = True
        self.camera.sliderChangedSignal.connect(self.doAutoScale)
        self.camera.cameraChangedSignal.connect(self.doAutoScale)
        self.camera.resolutionDividerChangedSignal.connect(self.doAutoScale)
        self.objective.objectiveChangedSignal.connect(self.doAutoScale)
        
        self.updateDisplaySignal.connect(self.updateDisplay)

    def keyPressEvent(self, event):
        if event.key() == ord(' '): self.doAutoScale()
        return super().keyPressEvent(event)

    def setROIVisible(self, value:bool): 
        if value: self.ROI.show()
        else: self.ROI.hide()
        
    def setROIDetected(self, value:bool): 
        if value is None: self.ROI.setPen((125,125,125))
        elif value: self.ROI.setPen((0,255,0))
        else: self.ROI.setPen((255,0,0))

    def updateSpinboxesFromHistogram(self, histogram):
        levels = histogram.getLevels()
        if self.camera.getCamera() == 'PL':
            self.settings.PLMinSpinbox.setValue(levels[0])
            self.settings.PLMaxSpinbox.setValue(levels[1])
        if self.camera.getCamera() == 'WL':
            self.settings.WLMinSpinbox.setValue(levels[0])
            self.settings.WLMaxSpinbox.setValue(levels[1])

    def updateMeasurementLineLabel(self):
        pts = self.measurementLine.listPoints()
        delta = pts[1] - pts[0]
        L = np.sqrt(delta.x() ** 2 + delta.y() ** 2)
        self.main.CameraSettingsWidget.updateLengthLabel(f'{L:.4f}')

    def openImageExternally(self):
        scale = self.camera.getScale(self.objective.getObjectiveScale())
        win = pg.image(self.camera.getImage(), autoLevels=False, levels=(self.camera.getLevelMin(),self.camera.getLevelMax()), autoRange=True, autoHistogramRange=False, scale=(scale,scale))
        win.view = pg.PlotItem()

        text = pg.TextItem(text='Estimated length: ? µm', color=(255,255,255), border='w')
        line = pg.LineSegmentROI(self.measurementLine.listPoints(), pos=self.measurementLine.pos(), pen=self.measurementLine.pen)

        def updateLine():
            pts = line.listPoints()
            delta = pts[1] - pts[0]
            L = np.sqrt(delta.x() ** 2 + delta.y() ** 2)
            text.setText(f'Estimated length: {L:.4f} µm')

        line.sigRegionChanged.connect(updateLine)
        win.addItem(line)
        win.addItem(text)
        updateLine()

    def doAutoScale(self): self.autoScaleRequired = True

    def updateCameraImage(self):
        scale = self.camera.getScale(self.objective.getObjectiveScale())
        self.setImage(self.camera.getImage(), autoLevels=False, autoRange=False, autoHistogramRange=False, scale=(scale,scale))
        if self.autoScaleRequired:
            self.view.autoRange(item=self.getImageItem())
            self.autoScaleRequired = False

    def suppressRender(self):
        self.imageItem._renderRequired = False # forces render() to happen in eventLoopThread and not during paint(), which causes GUI lag

    def updateDisplay(self):
        self.updateCameraImage()
        self.suppressRender()
        # self.ui.graphicsView.setUpdatesEnabled(True)
        # self.imageItem.setVisible(True)
        # print(self.imageItem.updatesEnabled())
        # self.imageItem.update()

    def eventLoop(self):
        self.updateDisplaySignal.emit()
        # self.updateCameraImage() # updateDisplay
        # self.imageItem._renderRequired = False # updateDisplay
        self.imageItem.render()
        # img = self.camera.getImage()
        # self.image = img
        # self.imageDisp = None
        # self.axes = {'t': None, 'x': 0, 'y': 1, 'c': 2 if img.ndim==3 else None}
        # self.currentIndex = 0
        # self.image = self.getProcessedImage()

        # self.imageItem._xp = np
        # shapeChanged = self.imageItem.image is None or self.image.shape != self.imageItem.image.shape

        # image = self.image.view()
        # if self.imageItem.image is None or image.dtype != self.imageItem.image.dtype:
        #     self.imageItem._effectiveLut = None
        # self.imageItem.image = image

        # if shapeChanged:
        #     self.imageItem.prepareGeometryChange()
        #     self.imageItem.informViewBoundsChanged()

        # self.imageItem.sigImageChanged.emit()
        # if self.imageItem._defferedLevels is not None:
        #     levels = self.imageItem._defferedLevels
        #     self.imageItem._defferedLevels = None
        #     self.imageItem.setLevels((levels))

        # # if transform is None:
        # #     transform = QtGui.QTransform()
        # #     # note that the order of transform is
        # #     #   scale followed by translate
        # #     if pos is not None:
        # #         transform.translate(*pos)
        # #     if scale is not None:
        # #         transform.scale(*scale)
        # # self.imageItem.setTransform(transform)

        # self.imageItem.render()
        # self.updateDisplaySignal.emit()
        # self.imageItem.update() # updateDisplay


        # when you call self.setImage(), ImageView.imageItem.update() is called, which occasionally causes the ImageView to freeze.
        # self.ui.graphicsView.setUpdatesEnabled(False)
        # print(self.ui.graphicsView.)
        # self.imageItem.setVisible(False)
        # GraphicsView().
        # ViewBox
        # self.updateCameraImage()
        # self.imageItem.render() # this is called before ImageView.imageItem.paint() is called to make sure the image is rendered in the thread to prevent lagging
        # self.imageItem.setVisible(True)

if __name__ == '__main__': import Glovebox
