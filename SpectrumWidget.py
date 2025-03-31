from computer_info import computer
if computer == 'glovebox':
    import sys
    sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\SpecPlotGUIElement')
    from SpecPlotGUIElement import SpecPlotGUIElement
else: from Scripts.SpecPlotGUIElement.SpecPlotGUIElement import SpecPlotGUIElement

class SpectrumWidget(SpecPlotGUIElement):
    def __init__(self, main):
        super().__init__()
        from GloveboxWindow import GloveboxWindow # for autocomplete
        self.main:GloveboxWindow = main

    def createGUI(self):
        self.setData([650,750,850], [1,1,1])

if __name__ == '__main__': import Glovebox