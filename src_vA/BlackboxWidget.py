import sys
import os
import string
import math
import re
import subprocess
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from random import *
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
    QListWidget, QListWidgetItem, QAbstractItemView, QWidget, QAction,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QHeaderView, QLabel, QTreeWidget, QTreeWidgetItem, QToolBar, QLineEdit,
    QCompleter, QSizePolicy, QComboBox, QMessageBox, QDialog, QDialogButtonBox,
    QFileDialog, QGridLayout, QFormLayout, QSlider, QScrollArea, QGroupBox)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt

class BlackboxWidget(QWidget):
    parameterSaveSignal = pyqtSignal(list)
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.initUI()
        self.running = False
        self.qsObj = None

    def initUI(self):
        self.bundle_dir = os.path.dirname(os.path.abspath(__file__))
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
