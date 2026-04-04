import sys
from PyQt5 import QtWidgets as qtw
from widget import TodoWidget

app = qtw.QApplication(sys.argv)
window = TodoWidget()
window.show()
sys.exit(app.exec_())