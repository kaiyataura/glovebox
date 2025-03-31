import numpy as np
from computer_info import computer
if computer == 'glovebox':
    import sys
    sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\Andor')
    from AdvancedSpectrometerWidget import CloseableSpectrometerWidget
else: from Scripts.Andor.AdvancedSpectrometerWidget import CloseableSpectrometerWidget

class SpectrometerWidget(CloseableSpectrometerWidget):
    def __init__(self, main):
        super().__init__(self.setSpectrumData)
        from GloveboxWindow import GloveboxWindow # for autocomplete
        self.main:GloveboxWindow = main

    def createGUI(self):
        pass

    def setSpectrumData(self, spec=None):
        if spec is None: 
            if computer == 'glovebox': spec = self.SpectrometerWidget.takeSpectrum()
            else: spec = np.zeros(len(self.SpectrometerWidget.wl_calibration))
        self.main.SpectrumWidget.setData(self.SpectrometerWidget.wl_calibration, spec, pen=(0,0,255))
        return spec
        
if __name__ == '__main__': import Glovebox