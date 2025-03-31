from computer_info import computer
if computer == 'glovebox':
    import sys
    sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\StageLocationGUIelement')
    from StageLocationGUIElement import StageLocationGUIElement
else: from Scripts.StageLocationGUIelement.StageLocationGUIElement import StageLocationGUIElement

class StageLocationWidget(StageLocationGUIElement):
    
    def __init__(self, main):
        super().__init__()
        from GloveboxWindow import GloveboxWindow # for autocomplete
        self.main:GloveboxWindow = main
        self.stage = self.main.devices.stage

    def createGUI(self):
        self.StageScatterPlot.scene().sigMouseClicked.connect(self.moveToMouse)

    def moveToMouse(self, event):
        if event.button() == 1 and event.double() == True:
            mousePoint =  self.StagePlotWindowItem.vb.mapSceneToView(event.scenePos())
            self.stage.setX(mousePoint.x())
            self.stage.setY(mousePoint.y())
            self.updateStagePos(mousePoint.x(), mousePoint.y())

    def setSpots(self, spots:list):
        self.StagePositionListPlot.setData(pos=spots)

    def eventLoop(self):
        self.updateStagePos(abs(self.stage.getX()), abs(self.stage.getY()))

if __name__ == '__main__': import Glovebox