from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
import time
import numpy as np
import cv2 as cv
from PIL import Image

class Camera(QWidget):
    cameraChangedSignal = pyqtSignal(str)
    sliderChangedSignal = pyqtSignal(str)
    resolutionDividerChangedSignal = pyqtSignal(int)

    def __init__(self, virtual:bool):
        super().__init__()
        if virtual: from VirtualEquipment import ICMeasureCam, ThorlabsCam, PA_Arduino
        else:
            import os
            directory = os.getcwd()
            os.chdir(r'C:\Users\Glovebox\Documents\Python Scripts\ICMeasureCamera')
            from ICMeasureCamera import ICMeasureCam
            os.chdir(directory)
            import sys
            sys.path.append(r'C:\Users\GloveBox\Downloads\Python Compact Scientific Camera Toolkit\examples')
            sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\ThorlabsCamera')
            sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\GrblRotationStation')
            import polling_example
            from ThorlabsCamera import ThorlabsCam
            from PA_arduino import PA_Arduino

        print('Initializing White Light Camera')
        self.WL = ICMeasureCam(name='DFK 33UX265 24910240',  videoFormat="RGB32 (2048x1536)") # 1600x1200 , 2048x1536, 1280x720
        print('White Light Camera initialized')

        print('Initializing PL Camera')
        self.PL = ThorlabsCam()
        print('PL Camera initialized')

        print('Starting Beam Splitter Slider Arduino')
        self.slider = PA_Arduino()
        print('Beam Splitter Slider Arduino started')

        self.lazyegg = np.asarray(Image.open('GloveboxData/lazyegg.png')).transpose((1,0,2))
        self.RCB = np.asarray(Image.open('GloveboxData/RCB.png')).transpose((1,0,2))
        self.RCBMode = False

        self.WLLevelMin = 0
        self.WLLevelMax = 255
        self.PLLevelMin = 0
        self.PLLevelMax = 100
        
        self.medianBlur = False
        self.gaussianBlur = False

        self.currentCamera = None # 'WL' or 'PL'
        self.currentSlider = 'WL' # 'WL', 'PL', or 'Empty'
        self.WLImage = self.lazyegg
        self.PLImage = self.lazyegg
        self.start()
        self.updateImage()

    def start(self): 
        '''Starts the correct camera (WL or PL) based on the current slider position. If slider position is 'Empty', nothing happens.'''
        if self.currentSlider == 'WL':
            self.startWL()
        if self.currentSlider == 'PL':
            self.startPL()

    def startWL(self):
        '''Ends PL camera image acquisition and starts the WL camera.'''
        if self.currentCamera == 'WL': return
        self.PL.endImageAcquisition()
        self.WL.startImageAcquisition()
        self.currentCamera = 'WL'
        self.cameraChangedSignal.emit('WL')

    def startPL(self): 
        '''Ends WL camera image acquisition and starts the PL camera.'''
        if self.currentCamera == 'PL': return
        self.WL.endImageAcquisition()
        self.PL.startImageAcquisition()
        self.currentCamera = 'PL'
        self.cameraChangedSignal.emit('PL')

    def startWLAcquisition(self):
        '''Starts WL camera image acquisition.'''
        self.WL.startImageAcquisition()

    def startPLAcquisition(self): 
        '''Starts PL camera image acquisition.'''
        self.PL.startImageAcquisition()

    def endWLAcquisition(self):
        '''Ends WL camera image acquisition.'''
        self.WL.endImageAcquisition()

    def endPLAcquisition(self): 
        '''Ends PL camera image acquisition.'''
        self.PL.endImageAcquisition()
        
    def setSlider(self, name:str):
        '''Sets the slider position to `name` ('PL', 'WL', or 'Empty') and starts the corresponding camera. If set to 'Empty', camera doesn't change.'''
        if self.currentSlider == name: return
        self.slider.moveTo(name)
        self.currentSlider = name
        self.sliderChangedSignal.emit(name)
        if name != 'Empty': 
            self.start()

    def setWLResolutionDivider(self, divider:int):
        '''Reduces the WL camera image resolution by a factor of `divider`.'''
        if self.WL.CameraResolutionDivider == divider: return
        self.WL.CameraResolutionDivider = divider
        self.resolutionDividerChangedSignal.emit(divider)
    
    def setExposure(self, ms:float): 
        '''Sets the exposure of the current camera (WL or PL) to `ms` milliseconds.'''
        if self.currentCamera == 'WL':
            self.setWLExposure(ms)
        if self.currentCamera == 'PL':
            self.setPLExposure(ms)

    def setWLExposure(self, ms:float): 
        '''Sets the exposure of the WL camera to `ms` milliseconds.'''
        self.WL.setExposureTime(ms)

    def setPLExposure(self, ms:float): 
        '''Sets the exposure of the PL camera to `ms` milliseconds.'''
        self.PL.setExposureTime(ms)

    def setWLLevelMin(self, value:int): self.WLLevelMin = value
    def setWLLevelMax(self, value:int): self.WLLevelMax = value
    def setPLLevelMin(self, value:int): self.PLLevelMin = value
    def setPLLevelMax(self, value:int): self.PLLevelMax = value

    def setMedianBlur(self, value:bool): self.medianBlur = value
    def setGaussianBlur(self, value:bool): self.gaussianBlur = value

    def getCamera(self): 
        '''Returns the current camera name ('PL' or 'WL'). Use `getSlider` instead if the slider in the 'Empty' position matters'''
        return self.currentCamera

    def getSlider(self): 
        '''Returns the current slider position ('PL', 'WL', or 'Empty'). Use `getCamera` instead if the camera type matters when the slider is in the 'Empty' position'''
        return self.currentSlider

    def getExposure(self):
        '''Returns the exposure of the current camera (WL or PL) in milliseconds'''
        if self.currentCamera == 'WL':
            return self.getWLExposure()
        if self.currentCamera == 'PL':
            return self.getPLExposure()

    def getWLExposure(self): 
        '''Returns the exposure of the WL camera in milliseconds.'''
        return self.WL.getExposureTime()

    def getPLExposure(self): 
        '''Returns the exposure of the PL camera in milliseconds.'''
        return self.PL.getExposureTime()

    def getScale(self, objective:int):
        '''Returns the µm per pixel based on the current camera, the resolution divdider (for WL), and the objective scale, `objective` (should be 10, 20, or 50).'''
        if self.currentCamera == 'WL':
            return 130/1611.2541*50.0*100/97.8*self.WL.CameraResolutionDivider/objective
        if self.currentCamera == 'PL':
            return 150/1083.1395*50.0*100/96/objective

    def getLevelMin(self):
        '''Returns the histogram level minimum of the current camera (WL or PL).'''
        if self.currentCamera == 'WL':
            return self.WLLevelMin
        if self.currentCamera == 'PL':
            return self.PLLevelMin

    def getLevelMax(self):
        '''Returns the histogram level maximum of the current camera (WL or PL).'''
        if self.currentCamera == 'WL':
            return self.WLLevelMax
        if self.currentCamera == 'PL':
            return self.PLLevelMax

    def getImage(self):
        '''Returns the most recently updated image from the current camera. Images are updated every cycle in the imageEventLoop with `updateImage`.'''
        if self.currentCamera == 'WL':
            return self.getWLImage()
        if self.currentCamera == 'PL':
            return self.getPLImage()

    def getWLImage(self): return self.WLImage

    def getPLImage(self): return self.PLImage

    def updateImage(self): 
        '''
        Updates the current camera's image for `getImage` to return. Images are blurred and flipped as needed.

        This makes sure the same image is used in the same cycle of the imageEventLoop. Images are updated every cycle in the imageEventLoop.
        '''
        if self.currentCamera == 'WL':
            return self.updateWLImage()
        if self.currentCamera == 'PL':
            return self.updatePLImage()

    def updateWLImage(self): 
        img = self.WL.getImageAsNumpyArray()
        if isinstance(img, np.ndarray): self.WLImage = self.blur(np.rot90(img, 1, (0,1)))

    def updatePLImage(self): 
        img = self.PL.getImageAsNumpyArray()
        if isinstance(img, np.ndarray): self.PLImage = self.blur(img.T)

    def blur(self, image:np.ndarray):
        '''Returns `image` with each blur applied as needed.'''
        if self.medianBlur: image = cv.medianBlur(image, 5)
        if self.gaussianBlur: image = cv.GaussianBlur(image, (5,5), 0)
        return image

    def waitExposure(self): 
        '''Sleeps for the current camera's exposure time to make sure the image is fully exposed.'''
        time.sleep(self.getExposure() / 1000)
    
    def homeSlider(self): self.slider.home()

    def moveSliderInward(self, duration:float):
        '''Moves the slider inward for `duration` seconds to manually fix position errors'''
        self.slider.digital[self.slider.pin_inward].write(1)
        time.sleep(duration)
        self.slider.digital[self.slider.pin_inward].write(0)
    
    def moveSliderOutward(self, duration:float):
        '''Moves the slider outward for `duration` seconds to manually fix position errors'''
        self.slider.digital[self.slider.pin_outward].write(1)
        time.sleep(duration)
        self.slider.digital[self.slider.pin_outward].write(0)
    
    def restartSlider(self):
        self.slider.close()
        self.slider.__init__()

    def restartPLCamera(self):
        self.PL.close()
        self.PL.__init__()

    def close(self): 
        self.WL.close()
        self.PL.close()
        self.slider.close()