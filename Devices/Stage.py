from PyQt5.QtCore import QObject, pyqtSignal

class Stage(QObject):
    xChangedSignal = pyqtSignal(float)
    yChangedSignal = pyqtSignal(float)
    zChangedSignal = pyqtSignal(float)
    xySpeedChangedSignal = pyqtSignal(int)
    zSpeedChangedSignal = pyqtSignal(int)
    
    def __init__(self, virtual:bool):
        super().__init__()
        if virtual: from VirtualEquipment import Thorlabs2DStageKinesis, Thorlabs1DPiezoKinesis
        else:
            import sys
            sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\ThorlabsStages')
            from ThorlabsStages import Thorlabs2DStageKinesis
            from ThorlabsStages import Thorlabs1DPiezoKinesis

        self.xySpeed = 10
        self.zSpeed = 10
        self.speedMode = 'normal'

        print('Initializing 2D Stage')
        self.stage = Thorlabs2DStageKinesis(SN_motor = '73126054')
        print('2D Stage initialized')

        print('Initializing Z Piezo Motor')
        self.zMotor = Thorlabs1DPiezoKinesis(SN_piezo = '41106464')
        print('Z Piezo Motor initialized')

    def home(self): 
        self.homeX()
        self.homeY()
        
    def homeX(self): 
        self.stage.homeX()
        self.xChangedSignal.emit(self.getX())
    
    def homeY(self):
        self.stage.homeY()
        self.yChangedSignal.emit(self.getY())
    
    def setX(self, value, relative=False): 
        self.stage.moveXTo(value + (self.getX() if relative else 0))
        self.xChangedSignal.emit(self.getX())
        
    def setY(self, value, relative=False): 
        self.stage.moveYTo(value + (self.getY() if relative else 0))
        self.yChangedSignal.emit(self.getY())

    def setZ(self, value, relative=False): 
        self.zMotor.setVoltage(value + (self.getZ() if relative else 0))
        self.zChangedSignal.emit(self.getZ())

    def setXYSpeed(self, value, relative=False): 
        xySpeed = min(max(value + (self.xySpeed if relative else 0), 1), 100)
        if xySpeed == self.xySpeed: return
        self.xySpeed = xySpeed
        self.xySpeedChangedSignal.emit(int(self.xySpeed))

    def setZSpeed(self, value, relative=False): 
        zSpeed = min(max(value + (self.zSpeed if relative else 0), 1), 100)
        if zSpeed == self.zSpeed: return
        self.zSpeed = zSpeed
        self.zSpeedChangedSignal.emit(int(self.zSpeed))

    def setSpeedMode(self, mode): self.speedMode = mode

    def setPosition(self, x, y, z):
        self.setX(x)
        self.setY(y)
        self.setZ(z)

    def getX(self): return self.stage.getXPosition()
    
    def getY(self): return self.stage.getYPosition()

    def getZ(self): return self.zMotor.getVoltage()

    def getPosition(self): return (self.getX(), self.getY(), self.getZ())

    def getXYSpeed(self): 
        if self.speedMode == 'normal':
            return self.xySpeed
        if self.speedMode == 'slow':
            return 1
        if self.speedMode == 'fast':
            return 1000

    def getZSpeed(self): return self.zSpeed

    def getNormalizedXYSpeed(self, secPerTick):
        '''Returns the mm per event loop tick speed in the X or Y direction given the tick speed `secPerTick`. XYSpeed 100 = 1 mm/sec'''
        return self.getXYSpeed() / 100 * secPerTick
    
    def getNormalizedZSpeed(self, secPerTick):
        '''Returns the mm per event loop tick speed in the Z direction given the tick speed `secPerTick`. ZSpeed 100 = 1 V/sec'''
        return self.getZSpeed() / 100 * secPerTick

    def close(self): 
        self.stage.close()
        self.zMotor.close()