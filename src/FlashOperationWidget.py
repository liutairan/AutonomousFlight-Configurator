import sys
import os
import string
import math
from random import *
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
    QListWidget, QListWidgetItem, QAbstractItemView, QWidget, QAction,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QHeaderView, QLabel, QTreeWidget, QTreeWidgetItem, QToolBar, QLineEdit,
    QCompleter, QSizePolicy, QComboBox, QMessageBox, QDialog, QDialogButtonBox,
    QFileDialog, QGridLayout, QGroupBox, QProgressBar)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QSize, Qt, QTimer

class FlashOperationWidget(QWidget):
    # connectionStatusChangedSignal = pyqtSignal()
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.initUI()
        self.connectionStatus = False

    def initUI(self):
        self.bundle_dir = os.path.dirname(os.path.abspath(__file__))
        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = FlashOperationWidget()
    form.resize(1080,720)
    form.show()
    app.exec_()
