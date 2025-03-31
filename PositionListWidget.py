from pyqtgraph import LayoutWidget, ImageView
from PyQt5.QtWidgets import QListWidget, QPushButton, QListWidgetItem, QMessageBox, QDialog, QCheckBox, QGridLayout, QFileDialog, QInputDialog, QComboBox, QLabel
from PyQt5.QtCore import Qt
import pickle, os, glob, shutil
import cv2 as cv

class PositionListWidget(LayoutWidget):
    def __init__(self, main):
        super().__init__()
        from GloveboxWindow import GloveboxWindow # for autocomplete
        self.main:GloveboxWindow = main
        self.stage = self.main.devices.stage
        self.stagePlot = self.main.StageLocationWidget

    def createGUI(self):
        self.positionsList = QListWidget()
        if 'positions' in self.main.oldGUIState:
            for name, data in self.main.oldGUIState['positions']:
                item = QListWidgetItem(name, self.positionsList)
                item.setData(Qt.ItemDataRole.UserRole, data)
        self.updateSpots()
        self.positionsList.itemDoubleClicked.connect(self.goToPositionInList)
        self.addWidget(self.positionsList, 0, 0, 1, 2)
        
        btn = QPushButton('Save Current Position')
        btn.clicked.connect(self.savePoint)
        self.addWidget(btn, 1, 0)
        
        btn = QPushButton('Delete Current Item')
        btn.clicked.connect(self.deleteCurrentItem)
        self.addWidget(btn, 1, 1)
        
        btn = QPushButton('Open Folder in List')
        btn.clicked.connect(self.loadPositionsFromFolder)
        self.addWidget(btn, 2, 0, 1, 2)
        
        btn = QPushButton('Flake Tinder')
        btn.clicked.connect(self.flakeTinder)
        self.addWidget(btn, 3, 0, 1, 1)
        
        btn = QPushButton('Import Likes')
        btn.clicked.connect(self.createAddDataPopup)
        self.addWidget(btn, 3, 1, 1, 1)
        
        btn = QPushButton('Clear List')
        btn.clicked.connect(self.clearList)
        self.addWidget(btn, 4, 0, 1, 2)

        self.itemCount = self.positionsList.count()

    def goToPositionInList(self, item:QListWidgetItem):
        pos = item.data(Qt.ItemDataRole.UserRole)
        self.stage.setX(pos[0])
        self.stage.setY(pos[1])
        self.stage.setZ(pos[2])

    def saveCorner(self, index, pos=None):
        self.saveCurrentPositionAs(f'Corner {index}', pos)

    def savePoint(self, pos=None):
        self.saveCurrentPositionAs(f'Position {self.itemCount}', pos)
        self.itemCount += 1
        return self.itemCount - 1

    def saveCurrentPositionAs(self, name, position=None):
        pos = self.stage.getPosition() if position is None else position
        item = QListWidgetItem(f'{name}\n  X: {pos[0]}\n  Y: {pos[1]}\n  Z: {pos[2]}', self.positionsList)
        item.setData(Qt.ItemDataRole.UserRole, pos)
        self.updateSpots()

    def deleteCurrentItem(self):
        self.positionsList.takeItem(self.positionsList.currentRow())
        self.updateSpots()

    def updateSpots(self):
        spots = []
        for i in range(self.positionsList.count()):    
            pos = self.positionsList.item(i).data(Qt.ItemDataRole.UserRole)
            spots.append((pos[0], pos[1]))
        self.stagePlot.setSpots(spots)
        
    def loadPositionsFromFolder(self):
        folder = str(QFileDialog.getExistingDirectory(self, 'Select Directory to Load'))
        if os.path.exists(folder + '/scanCorners.pickle'):
            savedCorners = {}
            with open(folder + '/scanCorners.pickle', 'rb') as f:
                savedCorners = pickle.load(f)
            for i, pos in enumerate(savedCorners['corners']): self.saveCorner(i, pos)
            # try:
            #     self.StageLocationPlot.addRect(savedCorners['corners'][0].x(), savedCorners['corners'][1].y(), abs(savedCorners['corners'][0].x() - savedCorners['corners'][1].y()), abs(savedCorners['corners'][0].y()-savedCorners['corners'][1].y()))
            # except AttributeError:
            #     print('StagePlotWindowItem doesnt exist yet')
        path = folder + '/*.jpg'
        files = glob.glob(path)   
        for name in files:
            stripPath = name[(len(folder)+1):-4] 
            name = stripPath.split('_')
            self.saveCurrentPositionAs(f'{name[0]} {name[1]}', [float(val[1:]) for val in name[2:]])
        self.updateSpots()
        
    def flakeTinder(self):
        path = 'ScanImages'
        dirs = [x[0] for x in os.walk(path)]
        folder, ok = QInputDialog.getItem(None, 'Select Folder', 'Accessible Folders', dirs[1:], 0, False)
        if not ok: return

        self.currentTinderFolder = folder
        path = folder + '/*.jpg'
        files = glob.glob(path)  
        self.currentTinderFiles = files
        self.flakeViewer = ImageView()
        self.imageIndex = 0    
        name = files[self.imageIndex]
        
        self.flakeViewer.setImage(cv.imread(name))
        self.flakeViewer.setWindowTitle('Position 1')
        self.likesList = []
        
        def myKeyPressEvent(event):
            key = event.key()

            if key == Qt.Key.Key_Left: self.imageIndex -= 1
            elif key == Qt.Key.Key_Right: self.imageIndex += 1
            elif key == Qt.Key.Key_Up:
                if self.imageIndex not in self.likesList: self.likesList.append(self.imageIndex)
            elif key == Qt.Key.Key_Down:
                if self.imageIndex in self.likesList: self.likesList.remove(self.imageIndex)
            else: return
            
            self.imageIndex = max(min(self.imageIndex, len(files) - 1), 0)
            name = files[self.imageIndex]
            stripPath = name[(len(folder) + 1):] 
            parts = stripPath.split('_')
            self.flakeViewer.setImage(cv.imread(name))
            self.flakeViewer.setWindowTitle(f'Position {parts[1]}')

        self.flakeViewer.keyPressEvent = myKeyPressEvent
        self.flakeViewer.show()

    def createAddDataPopup(self, filenames):    
        self.addDataDialog = QDialog()

        layout = QGridLayout()

        layout.addWidget(QLabel('Flake Material to Add:'), 0, 0)
        self.flakeTypeComboBox = QComboBox()
        self.flakeTypeComboBox.addItem('BP', 'ScanImages/BP labelled data') # add any path
        self.flakeTypeComboBox.addItem('WSe2', 'ScanImages/WSe2 labelled data')
        layout.addWidget(self.flakeTypeComboBox, 0, 1)

        self.addFlakeCheckbox = QCheckBox('Add Flakes to Labelled Data?')
        self.addBlankCheckbox = QCheckBox('Add Blanks to Labelled Data?')
        layout.addWidget(self.addFlakeCheckbox, 1, 0)
        layout.addWidget(self.addBlankCheckbox, 1, 1)

        btn = QPushButton('Done')
        btn.clicked.connect(self.importFlakeTinderLikes)
        layout.addWidget(btn, 2, 0)

        self.addDataDialog.setLayout(layout)
        self.addDataDialog.setMinimumSize(100, 100)
        self.addDataDialog.setWindowTitle('Do you want to add these to the labelled data set?')
        self.addDataDialog.show()

    def importFlakeTinderLikes(self):
        path = self.flakeTypeComboBox.currentData()
        if self.addFlakeCheckbox.isChecked():
            for i in self.likesList:
                oldfile = self.currentTinderFiles[i]
                newfilename = f'{path}/yes/yes_{os.path.basename(os.path.dirname(oldfile))}_{os.path.basename(oldfile)}'
                shutil.copy(oldfile, newfilename)
        
        if self.addBlankCheckbox.isChecked():
            notLiked = [i for i in self.currentTinderFiles if i not in self.likesList]
            for file in notLiked:
                newfilename = f'{path}/no/no_{os.path.basename(os.path.dirname(file))}_{os.path.basename(file)}'
                shutil.copy(file, newfilename)
        
        self.clearList()
        
        for i in self.likesList: 
            name = self.currentTinderFiles[i]
            stripPath = name[(len(self.currentTinderFolder)+1):-4] 
            parts = stripPath.split('_')
            self.saveCurrentPositionAs(f'Liked {parts[0]} {parts[1]}', [float(val[1:]) for val in parts[2:]])
        self.addDataDialog.close()
        
        self.updateSpots()

    def clearList(self):
        reply = QMessageBox.question(self, '', 'Clear List?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            for item in self.positionsList.findItems('Position', Qt.MatchFlag.MatchContains):
                self.positionsList.takeItem(self.positionsList.row(item))
            self.updateSpots()

if __name__ == '__main__': import Glovebox