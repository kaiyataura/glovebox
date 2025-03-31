from PyQt5.QtWidgets import QApplication
import sys
from GloveboxWindow import GloveboxWindow

app = QApplication([])
app.setStyle('Fusion')
window = GloveboxWindow()
window.show()
sys.exit(app.exec_())

# change computer to personal or glovebox in computer_info.py