from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

class Polarizer(QWidget):
    lockChangedSignal = pyqtSignal(bool)
    HWPChangedSignal = pyqtSignal(float)
    LPChangedSignal = pyqtSignal(float)
    
    def __init__(self, virtual:bool):
        super().__init__()
        if virtual: from VirtualEquipment import ThorlabsCageRotator
        else:
            import sys
            sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\ThorlabsStages')
            from ThorlabsStages import ThorlabsCageRotator

        print('Initializing Linear Polarizer')
        self.LP = ThorlabsCageRotator(SN_motor = '55203454')
        if not self.LP.motor.Status.IsHomed: self.LP.home()
        print('Linear Polarizer initialized')

        print('Initializing Half Wave Plate')
        self.HWP = ThorlabsCageRotator(SN_motor = '55164244')
        if not self.HWP.motor.Status.IsHomed: self.HWP.home()
        print('Half Wave Plate initialized')
        
        self.offset = 0
        self.locked = False

    def getLPAngle(self): return self.LP.getRotation()
    def getHWPAngle(self): return 2 * self.HWP.getRotation()
    def getOffset(self): return self.offset
    def getLocked(self): return self.locked
    
    def setLocked(self, locked:bool): 
        if self.locked == bool(locked): return
        if locked: self.updateOffset()
        self.locked = bool(locked)
        print(f'locked: {self.locked}')
        self.lockChangedSignal.emit(self.locked)

    def setLPAngle(self, value:float): 
        self.LP.moveToDeg(value)
        self.LPChangedSignal.emit(value)
        if self.locked: 
            self.HWP.moveToDeg((value - self.offset) / 2)
            self.HWPChangedSignal.emit(value - self.offset)

    def setHWPAngle(self, value:float): 
        self.HWP.moveToDeg(value / 2)
        self.HWPChangedSignal.emit(value)
        if self.locked: 
            self.LP.moveToDeg(value + self.offset)
            self.LPChangedSignal.emit(value + self.offset)

    def updateOffset(self): 
        self.offset = self.getLPAngle() - self.getHWPAngle()

    def setOffset(self, offset): 
        self.offset = offset
            
    def close(self): 
        self.LP.close()
        self.HWP.close()




    # do % 360 on angle