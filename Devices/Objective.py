from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

class Objective(QWidget):
    objectiveChangedSignal = pyqtSignal(str)
    zChangedSignal = pyqtSignal(float)
    lockChangedSignal = pyqtSignal(bool)

    def __init__(self, virtual:bool):
        super().__init__()
        if virtual: from VirtualEquipment import ArduinoRotationStage, MCMStage
        else:
            import sys
            sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\GrblRotationStation')
            sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\ThorlabsStages')
            from ArduinoRotationStage import ArduinoRotationStage
            from MCMStage import MCMStage

        print('Starting Objective Wheel Arduino')
        self.wheel = ArduinoRotationStage()
        print('Objective Wheel Arduino started')

        print('Initializing MCM Stage')
        self.stage = MCMStage()
        print('MCM Stage initialized')
        
        self.locked = False
        self.objective = None
        self.scale = 1
        self.objectives = ['10x', '20x', '50x', '50xIR']
        self.nameToScale = {'10x': 10, '20x': 20, '50x': 50, '50xIR': 50}
        self.setObjective('10x')

    def getRotation(self): return self.wheel.getPosmm()

    def getZ(self): return self.stage.getPositionInMM()

    def getObjectiveScale(self): return self.scale

    def setRotation(self, pos, relative=False):
        if relative: pos += self.getRotation()
        self.wheel.moveAbsolutemm('Y', pos - 0.2) # backlash correction
        self.wheel.moveAbsolutemm('Y', pos)

    def setObjective(self, name): 
        name = str(name)
        if self.objective == name: return
        self.setRotation(self.wheel.Ypresetpositions[name])
        self.objective = name
        self.scale = self.nameToScale[name]
        self.objectiveChangedSignal.emit(name)

    def setZ(self, z, relative=False): 
        if not self.locked: 
            self.stage.setPositionInMM(z + (self.getZ() if relative else 0))  
            self.zChangedSignal.emit(self.getZ())      
    
    def setMCMLocked(self, locked:bool): 
        if self.locked == bool(locked): return
        self.locked = bool(locked)
        self.lockChangedSignal.emit(self.locked)

    def sendWheelCommand(self, command):
        self.wheel.ser.write(str.encode('\r\n{}\r\n'.format(command)))

    def restartWheel(self):
        self.wheel.close()
        self.wheel.__init__()

    def close(self): 
        self.wheel.close()
        self.stage.close()