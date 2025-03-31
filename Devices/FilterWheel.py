from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

class FilterWheel(QWidget):
    filterChangedSignal = pyqtSignal(int)

    def __init__(self, virtual:bool):
        super().__init__()
        if virtual: from VirtualEquipment import ThorlabsFilterWheel
        else:
            import sys
            sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\Thorlabs Filter Wheel')
            from FilterWheel import ThorlabsFilterWheel

        print('Initializing Filter Wheel')
        self.filterWheel = ThorlabsFilterWheel(SN_wheel = 'TP02394482-18585')
        print('Filter Wheel initialized')
        
        self.filterIndex = None

    def setFilter(self, index): 
        if self.filterIndex == index: return
        self.filterIndex = index
        self.filterWheel.SetPosition(index + 1)
        self.filterChangedSignal.emit(self.filterIndex)

    def getFilter(self): return self.filterIndex
            
    def close(self): return self.filterWheel.close()
