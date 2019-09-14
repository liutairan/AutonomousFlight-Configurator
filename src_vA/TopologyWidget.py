import sys
import os
import string
import math
import re
import subprocess
import threading
from functools import partial
from apscheduler.schedulers.background import BackgroundScheduler
from random import *
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
    QListWidget, QListWidgetItem, QAbstractItemView, QWidget, QAction,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QHeaderView, QLabel, QTreeWidget, QTreeWidgetItem, QToolBar, QLineEdit,
    QCompleter, QSizePolicy, QComboBox, QMessageBox, QDialog, QDialogButtonBox,
    QFileDialog, QGridLayout, QFormLayout, QSlider, QScrollArea, QGroupBox,
    QSpinBox, QRadioButton, QDoubleSpinBox)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QSize

from SettingFileIO import *

class TopologyWidget(QWidget):
    topologySaveSignal = pyqtSignal(list)
    def __init__(self, parent=None, qsObj=None):
        super(QWidget, self).__init__(parent)
        self.initUI()
        self.running = False
        self.qsObj = qsObj
        self.defaultSettingData = None
        self.userSettingData = None
        self.initValues()

    def initUI(self):
        self.bundle_dir = os.path.dirname(os.path.abspath(__file__))
        # Switch Icon Image
        self.switchOFFImage = QPixmap(self.bundle_dir + "/Pics/OFF.png")
        self.switchONImage = QPixmap(self.bundle_dir + "/Pics/ON.png")

        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)

        self.saveandrebootButton = QPushButton("Save and Reboot", self)
        self.saveandrebootButton.clicked.connect(self.saveandreboot)
        saveRowSpacer = QWidget()
        saveRowSpacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        saveRowLayout = QHBoxLayout()
        saveRowLayout.addWidget(saveRowSpacer)
        saveRowLayout.addWidget(self.saveandrebootButton)
        self.layout.addLayout(saveRowLayout)

        self.scrollArea = QScrollArea()
        self.scrollAreaGroupBox = QGroupBox("Topology", self)
        self.scrollAreaLayout = QGridLayout()
        self.scrollAreaGroupBox.setLayout(self.scrollAreaLayout)
        self.scrollArea.setWidget(self.scrollAreaGroupBox)
        self.scrollArea.setWidgetResizable(True)
        self.layout.addWidget(self.scrollArea)

        self.scrollAreaGroupBoxInit()

        self.layout.addStretch(1)
        self.setLayout(self.layout)

    def scrollAreaGroupBoxInit(self):
        self.topologySettings = {}

        self.scrollAreaLayout.addWidget(QLabel("Telemetry Settings"), 0, 0, 1, 1)

        self.scrollAreaLayout.addWidget(QLabel("Current Telemetry Address (Self)"), 1, 0, 1, 1)
        self.topologySettings['Current Telemetry Address'] = QComboBox()
        self.scrollAreaLayout.addWidget(self.topologySettings['Current Telemetry Address'], 1, 1, 1, 1)

        self.scrollAreaLayout.addWidget(QLabel("Source"), 2, 0, 1, 1)
        self.topologySettings['Telemetry Source Type'] = QComboBox()
        self.scrollAreaLayout.addWidget(self.topologySettings['Telemetry Source Type'], 2, 1, 1, 1)
        self.topologySettings['Telemetry Source Address 0'] = QComboBox()
        self.scrollAreaLayout.addWidget(self.topologySettings['Telemetry Source Address 0'], 2, 2, 1, 1)
        self.topologySettings['Telemetry Source Address 1'] = QComboBox()
        self.scrollAreaLayout.addWidget(self.topologySettings['Telemetry Source Address 1'], 2, 3, 1, 1)
        self.topologySettings['Telemetry Source Address 2'] = QComboBox()
        self.scrollAreaLayout.addWidget(self.topologySettings['Telemetry Source Address 2'], 2, 4, 1, 1)

        self.scrollAreaLayout.addWidget(QLabel("Destination"), 3, 0, 1, 1)
        self.topologySettings['Telemetry Destination Type'] = QComboBox()
        self.scrollAreaLayout.addWidget(self.topologySettings['Telemetry Destination Type'], 3, 1, 1, 1)
        self.topologySettings['Telemetry Destination Address 0'] = QComboBox()
        self.scrollAreaLayout.addWidget(self.topologySettings['Telemetry Destination Address 0'], 3, 2, 1, 1)
        self.topologySettings['Telemetry Destination Address 1'] = QComboBox()
        self.scrollAreaLayout.addWidget(self.topologySettings['Telemetry Destination Address 1'], 3, 3, 1, 1)
        self.topologySettings['Telemetry Destination Address 2'] = QComboBox()
        self.scrollAreaLayout.addWidget(self.topologySettings['Telemetry Destination Address 2'], 3, 4, 1, 1)

        self.scrollAreaLayout.addWidget(QLabel("\nRemote Control Settings"), 4, 0, 1, 1)

        self.scrollAreaLayout.addWidget(QLabel("Current Remote Control Address"), 5, 0, 1, 1)
        self.topologySettings['Current Remote Control Address'] = QComboBox()
        self.scrollAreaLayout.addWidget(self.topologySettings['Current Remote Control Address'], 5, 1, 1, 1)

        self.scrollAreaLayout.addWidget(QLabel("Remote Control Source Address"), 6, 0, 1, 1)
        self.topologySettings['Remote Control Source Address'] = QComboBox()
        self.scrollAreaLayout.addWidget(self.topologySettings['Remote Control Source Address'], 6, 1, 1, 1)

    def saveandreboot(self):
        # Get values from UI: UI->userSettingData
        # userSettingData->qsObj
        # qsObj->Board write with MSP
        tbsList = []
        self.topologySaveSignal.emit(tbsList)
        # Save EEPROM
        # Reboot
        pass

    # Read widget values and set self.userSettingData: UI->userSettingData
    def getUIValues(self):
        self.userSettingData['Topology']['Current Telemetry Address'] = self.topologySettings['Current Telemetry Address'].currentIndex()
        self.userSettingData['Topology']['Telemetry Source Type'] = self.topologySettings['Telemetry Source Type'].currentIndex()
        self.userSettingData['Topology']['Telemetry Destination Type'] = self.topologySettings['Telemetry Destination Type'].currentIndex()
        for i in range(3):
            self.userSettingData['Topology']['Telemetry Source Address'][i] = self.topologySettings['Telemetry Source Address '+str(i)].currentIndex()
            self.userSettingData['Topology']['Telemetry Destination Address'][i] = self.topologySettings['Telemetry Destination Address '+str(i)].currentIndex()

        self.userSettingData['Topology']['Current Remote Control Address'] = self.topologySettings['Current Remote Control Address'].currentIndex()
        self.userSettingData['Topology']['Remote Control Source Address'] = self.topologySettings['Remote Control Source Address'].currentIndex()

    # Transfer userSettingData to qsObj
    # To do
    def setQSObj(self):
        # userSettingData->qsObj
        pass

    def loadValuesFromDefault(self):
        self.defaultSettingData = readDefaultSettingFile()

    def loadValuesFromUserSaved(self):
        self.userSettingData = readUserSettingFile()

    def initValues(self):
        self.loadValuesFromDefault()
        # self.setUIDefaultValues()
        self.userSettingData = dict(self.defaultSettingData)
        self.setUIValues()

    # Set UI widget values with userSettingData
    def setUIValues(self):
        self.topologySettings['Current Telemetry Address'].clear()
        self.topologySettings['Current Telemetry Address'].addItems(self.userSettingData['Topology']['Address Options'])
        self.topologySettings['Current Telemetry Address'].setCurrentIndex(self.userSettingData['Topology']['Current Telemetry Address'])

        self.topologySettings['Telemetry Source Type'].clear()
        self.topologySettings['Telemetry Source Type'].addItems(self.userSettingData['Topology']['Telemetry Source Type Options'])
        self.topologySettings['Telemetry Source Type'].setCurrentIndex(self.userSettingData['Topology']['Telemetry Source Type'])

        self.topologySettings['Telemetry Destination Type'].clear()
        self.topologySettings['Telemetry Destination Type'].addItems(self.userSettingData['Topology']['Telemetry Destination Type Options'])
        self.topologySettings['Telemetry Destination Type'].setCurrentIndex(self.userSettingData['Topology']['Telemetry Destination Type'])

        for i in range(3):
            self.topologySettings['Telemetry Source Address '+str(i)].clear()
            self.topologySettings['Telemetry Source Address '+str(i)].addItems(self.userSettingData['Topology']['Address Options'])
            self.topologySettings['Telemetry Source Address '+str(i)].setCurrentIndex(self.userSettingData['Topology']['Telemetry Source Address'][i])
            self.topologySettings['Telemetry Destination Address '+str(i)].clear()
            self.topologySettings['Telemetry Destination Address '+str(i)].addItems(self.userSettingData['Topology']['Address Options'])
            self.topologySettings['Telemetry Destination Address '+str(i)].setCurrentIndex(self.userSettingData['Topology']['Telemetry Destination Address'][i])

        self.topologySettings['Current Remote Control Address'].clear()
        self.topologySettings['Current Remote Control Address'].addItems(self.userSettingData['Topology']['Address Options'])
        self.topologySettings['Current Remote Control Address'].setCurrentIndex(self.userSettingData['Topology']['Current Remote Control Address'])

        self.topologySettings['Remote Control Source Address'].clear()
        self.topologySettings['Remote Control Source Address'].addItems(self.userSettingData['Topology']['Address Options'])
        self.topologySettings['Remote Control Source Address'].setCurrentIndex(self.userSettingData['Topology']['Remote Control Source Address'])

    # Transfer values from qsObj to userSettingData
    # To do
    def setValues(self):
        # From qsObj msp_topology?
        # self.userSettingData['Topology']['Current Telemetry Address']
        # self.userSettingData['Topology']['Telemetry Source Type']
        # self.userSettingData['Topology']['Telemetry Destination Type']
        # self.userSettingData['Topology']['Telemetry Source Address']
        # self.userSettingData['Topology']['Telemetry Destination Address']
        # self.userSettingData['Topology']['Current Remote Control Address']
        # self.userSettingData['Topology']['Remote Control Source Address']
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = TopologyWidget()
    form.resize(1080,720)
    form.show()
    app.exec_()
