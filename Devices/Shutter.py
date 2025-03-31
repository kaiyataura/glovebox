from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

class Shutter(QWidget):
    flipperChangedSignal = pyqtSignal(bool)

    def __init__(self, virtual:bool):
        super().__init__()
        if virtual: from VirtualEquipment import LaserShutter
        else:
            import sys
            sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\ThorlabsStages')
            from ThorlabsStages import LaserShutter
        
        self.shutter = LaserShutter()
        self.open = False

    def setOpen(self, open): 
        if self.open == bool(open): return
        self.shutter.flipperOn() if open else self.shutter.flipperOff()
        self.open = bool(open)
        self.flipperChangedSignal.emit(self.open)

    def getOpen(self): return self.open

    def close(self): self.shutter.close()