import cv2 as cv
import numpy as np

class ThorlabsCageRotator:
    def __init__(self, SN_motor = '55164244' ):
        print("Initializing cage rotator")
        self.motor = self.Motor()
        print("Cage Rotator initialized")
        
    def getRotation(self):
        return self.motor.angle
    
    def moveToDeg(self, value):
        self.motor.Status.IsHomed = False
        if value < 0:
            value = 360 + value
        if value > 360:
            value = value - 360
        self.motor.angle = value
        print(f'Cage Rotator rotated to {value}')
        
    def home(self):
        print('homing HWP...')
        self.motor.angle = 0
        self.motor.Status.IsHomed = True
        print('Cage Rotator homed')

    def close(self):
        print("Cage Rotator closed")

    class Motor:
        def __init__(self):
            self.angle = 0
            self.Status = self.status()

        class status:
            def __init__(self):
                self.IsHomed = False

class Thorlabs2DStageKinesis:
    def __init__(self, SN_motor = '73126054'):
        print("device set up")
        print("device connected, serial No: ",SN_motor)
        self.channelX = 0
        self.channelY = 0
        print("X motor enabled")
        print("Y motor enabled")
        
        print("current positionX:",self.getXPosition())
        print("current positionY:",self.getYPosition())
        
    def home(self):
        self.homeX()
        self.homeY()
  
    def homeX(self):
        self.channelX = 0
        print('Stage X homed')
    
    def homeY(self):
        self.channelY = 0
        print('Stage Y homed')

    def moveXTo(self, value):
        self.channelX = value
        print(f'Stage X moved to {value}')
        
    def getXPosition(self):
        return self.channelX
    
    def moveYTo(self, value):
        self.channelY = value
        print(f'Stage Y moved to {value}')
        
    def getYPosition(self):
        return self.channelY
    
    def close(self):
        print("Motors closed")

class Thorlabs1DPiezoKinesis:
    def __init__(self, SN_piezo = '41106464'):
        self.channelZ = 0
        self.MaxVoltage = 150
        print("piezo initialized")
        print("piezo Z at Voltage: ",self.getVoltage())
    
    def getVoltage(self):
        return self.channelZ
    
    def setVoltage(self, value):
        if value >= 0 and value < self.MaxVoltage:
            self.channelZ = value
            print(f'Piezo voltage set to {value}')
        else:
            print('Voltage out of allowed range')
    
    def close(self):
        print("Piezo stopping")
        print("Piezo stopped polling. Trying to disconnect channel.")
        print("Channel disconnected. Trying to disconnect device")
        print("Piezo disconnected and closed")
        
class LaserShutter:
    def __init__(self, SN_flipper = '37002951'):
        self.flipper = 1
        print("flipper initialized")
        self.flipperOff()
    
    def flip(self):
        if self.flipper == 1:
            self.flipperOff()
        else:
            self.flipperOn()
    
    def flipperOff(self):
        self.flipper = 2
        print('Laser Shutter closed')
    
    def flipperOn(self):
        self.flipper = 1
        print('Laser Shutter opened')
        
    def close(self):
        print('Laser Shutter disconnected')

class MCMStage:
    def __init__(self, port='COM5'):
        self.pos = 0
        self.lastCorrectPosition = 0 
        self.lastCorrectPosition = self.getPosition()
        
    def setPosition(self, EncoderInt):    
        self.pos = EncoderInt
        print(f'Objective focus set to {self.pos} = {self.getPositionInMM()} mm')
        
    def getPosition(self): 
        self.lastCorrectPosition = self.pos
        return self.pos
            
    def getPositionInMM(self):
        return self.getPosition() * 0.2116667 / 1000.0
    
    def setPositionInMM(self, PositionInMM):
        if PositionInMM > 20.0:
            self.setPosition(int( 1000.0/0.2116667*20.0 ))
        else:
            self.setPosition(int( 1000.0/0.2116667*PositionInMM ))

    def close(self):
        print('MCM Stage closed')

class PA_Arduino:
    def __init__(self, port = 'COM7'):
        self.home()
        self.pin_inward = 0
        self.pin_outward = 1
        
        self.digital = [self.Pin(), self.Pin()]

    def home(self):
        self.current_pos = 'WL'
        print('Slider homed to WL')
        
    def moveTo(self, new_pos):
        self.current_pos = new_pos
        print(f'Slider moved to {new_pos}')
        
    def close(self):
        print('Slider closed')

    class Pin:
        def write(self, num): pass

class ArduinoRotationStage:
    def __init__(self, Port='COM4'):
        step_size = 0.963
        self.Ypresetpositions =	{
                                    "10x": 0*step_size,
                                    "20x": 1*step_size,
                                    "50x": 2*step_size,
                                    "50xIR": 3*step_size,                                    
                                    }
        print("Arduino connected")
        self.home()
        self.ser = self.Serial()
        
    def home(self):
        self.position = 0
        print('Objective Wheel homed to 0')
        
    def read(self):
        pass
            
    def getPosmm(self): 
        return self.position
    
    def reset(self):
        pass 
        
    def moveAbsolutemm(self, axis, distance):
        self.position = distance
        print(f'Objective Wheel moved to {self.position}')

    def moveRelativemm(self, axis, distance):
        self.position += distance
        print(f'Objective Wheel moved to {self.position}')
        
    def IncreaseObjective(self):
        currentobjective = self.whichOptic()
        
        if '50xIR' not in currentobjective:
            nextobjectiveindex = list(self.Ypresetpositions.keys()).index(currentobjective)+1
            nextobjective = list(self.Ypresetpositions.items())[nextobjectiveindex][0]
            self.moveAbsolutemm('Y', self.Ypresetpositions[nextobjective]) 
        else:
            print('cannot increase further')
            pass
        
    def DecreaseObjective(self):
        currentobjective = self.whichOptic()
        if '10x' not in currentobjective:
            nextobjectiveindex = list(self.Ypresetpositions.keys()).index(currentobjective)-1
            nextobjective = list(self.Ypresetpositions.items())[nextobjectiveindex][0]
            self.moveAbsolutemm('Y', -0.2+self.Ypresetpositions[str(nextobjective)])
            self.moveAbsolutemm('Y', self.Ypresetpositions[str(nextobjective)])
        else:
            print('cannot decrease further')
            pass
        
    def whichOptic(self):
        res_key, res_val = min(self.Ypresetpositions.items(), key=lambda x: abs(self.position - x[1]))
        return res_key
        
    def close(self):
        print('Close connection to Arduino Rotation Stage')

        print("Connection to Arduino Rotation Stage closed")

    class Serial:
        def write(self, command): pass

class ThorlabsFilterWheel:
    def __init__(self, SN_wheel = 'TP02394482-18585'):
        print("Initializing Filter Wheel")
        self.triggerMode = 'input mode'    
        self.speedMode = 'high speed'
        self.position = 0   
        print("Initialization successful")
    
    def home(self):
        self.triggerMode = 'input mode'
        self.speedMode = 'slow speed'
        self.position = 1
        print('Filter Wheel homed to:')
        self.CheckStates()
    
    def CheckStates(self):
        print("Current Trigger Mode:", self.triggerMode)
        print("Current Speed Mode:",self.speedMode)
        print("Current position: ", self.position)

    def SetPosition(self, pos):
        self.position = pos
        print('Filter Wheel moved to:')
        self.CheckStates()
        
    def GetPosition(self):
        return self.position
        
    def close(self):
        print("Successfully closed filter wheel")

class ICMeasureCam:
    def __init__(self, name="", videoFormat="RGB32 (1600x1200)", frameRate=30.00003):
        self.img = cv.cvtColor(cv.imread('test_1.png'), cv.COLOR_BGR2RGB)[::4,::4,:]

        self.on = False
        self.CameraResolutionDivider = 1
        self.exposure = 10

    def startImageAcquisition(self): 
        self.on = True
        print('WL Camera started image acquisition')
            
    def showCameraProperties(self): 
        print('WL Camera showed camera properties')
    
    def endImageAcquisition(self): 
        self.on = False        
        print('WL Camera ended image acquisition')
        
    def getExposureTime(self): return self.exposure
    
    def setExposureTime(self, setpoint_ms): 
        self.exposure = setpoint_ms
        print(f'WL Camera exposure set to {self.exposure}')

    def getImageAsNumpyArray(self):
        if not self.on: return print('Camera Off')
        img = self.img[::self.CameraResolutionDivider, ::self.CameraResolutionDivider]
        img = np.clip((img + np.random.randint(20, size=img.shape) - 10), 0, 255).astype(np.uint8)
        startX = 0
        endX = 1000

        startY = 0
        endY = 1000
        return img
        # return np.array(self.img.take(range(startY,endY),mode='wrap',axis=0).take(range(startX,endX),mode='wrap',axis=1),dtype='uint8')
    
    def close(self): 
        self.endImageAcquisition()
        print('WL Camera closed')

class ThorlabsCam:
    def __init__(self):
        self.img = cv.cvtColor(cv.imread('test_2.png'), cv.COLOR_BGR2RGB)[::8,::8,:1]
        self.on = False
        self.exposure = 10

    def startImageAcquisition(self): 
        self.on = True
        print('PL Camera started image acquisition')

    def showCameraProperties(self):
        print('PL Camera showed camera properties')
    
    def endImageAcquisition(self): 
        self.on = False        
        print('PL Camera ended image acquisition')
        
    def getExposureTime(self): return self.exposure
    
    def setExposureTime(self, setpoint_ms): 
        self.exposure = setpoint_ms
        print(f'PL Camera exposure set to {self.exposure}')

    def getImageAsNumpyArray(self):
        if not self.on: return print('Camera Off')
        startX = 0
        endX = 1000

        startY = 0
        endY = 1000
        return self.img
        # return np.array(self.img.take(range(startY,endY),mode='wrap',axis=0).take(range(startX,endX),mode='wrap',axis=1),dtype='uint8')
    
    def close(self): 
        self.endImageAcquisition()
        print('PL Camera closed')