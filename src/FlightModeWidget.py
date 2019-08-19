#!/usr/bin/env python3

'''
    This file is part of AutonomousFlight Configurator.

    AutonomousFlight Configurator is free software: you can
    redistribute it and/or modify it under the terms of the
    GNU General Public License as published by the Free Software
    Foundation, either version 3 of the License, or (at your
    option) any later version.

    AutonomousFlight Configurator is distributed in the hope
    that it will be useful, but WITHOUT ANY WARRANTY; without
    even the implied warranty of MERCHANTABILITY or FITNESS
    FOR A PARTICULAR PURPOSE.  See the GNU General Public
    License for more details.

    You should have received a copy of the GNU General Public
    License along with AutonomousFlight Configurator. If not,
    see <https://www.gnu.org/licenses/>.
'''

__author__ = "Tairan Liu"
__credits__ = ["Tairan Liu", "Other Supporters"]
__license__ = "GPLv3"
__maintainer__ = "Tairan Liu"
__email__ = "liutairan2012@gmail.com"

import sys
import os
import string
import math
import re
import subprocess
import threading
from random import *
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
    QListWidget, QListWidgetItem, QAbstractItemView, QWidget, QAction,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QHeaderView, QLabel, QTreeWidget, QTreeWidgetItem, QToolBar, QLineEdit,
    QCompleter, QSizePolicy, QComboBox, QMessageBox, QDialog, QDialogButtonBox,
    QFileDialog, QGridLayout, QFormLayout, QSlider, QScrollArea, QGroupBox)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt

from QRangeSlider import QRangeSlider

class FlightModeWidget(QWidget):
    flightmodeSaveSignal = pyqtSignal(list)
    def __init__(self, parent, qsObj):
        super(QWidget, self).__init__(parent)
        self.qsObj = qsObj
        self.initUI()
        self.running = False
        self.modeGroups = []

    def initUI(self):
        self.bundle_dir = os.path.dirname(os.path.abspath(__file__))
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)

        self.saveButton = QPushButton("Save", self)
        self.saveButton.clicked.connect(self.save)
        saveRowSpacer = QWidget()
        saveRowSpacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        saveRowLayout = QHBoxLayout()
        saveRowLayout.addWidget(saveRowSpacer)
        saveRowLayout.addWidget(self.saveButton)
        self.layout.addLayout(saveRowLayout)
        self.scrollArea = QScrollArea()
        self.scrollAreaGroupBox = QGroupBox(self)
        self.scrollAreaLayout = QGridLayout()
        self.scrollAreaGroupBox.setLayout(self.scrollAreaLayout)
        self.scrollArea.setWidget(self.scrollAreaGroupBox)
        self.scrollArea.setWidgetResizable(True)
        self.layout.addWidget(self.scrollArea)

        # self.flightmodeList = ["ARM", "ANGLE", "HORIZON", "TURN ASSIST",
        #                        "AIR MODE", "HEADING HOLD", "HEADFREE",
        #                        "HEADADJ", "NAV ALTHOLD", "SURFACE",
        #                        "NAV POSHOLD", "NAV RTH", "NAV WP",
        #                        "HOME RESET", "GCS NAV", "BEEPER", "OSD SW",
        #                        "KILLSWITCH", "FAILSAFE", "CAMERA CONTROL 1",
        #                        "CAMERA CONTROL 2", "CAMERA CONTROL 3"]
        self.flightmodeList = self.qsObj.msp_boxnames
        self.sliderList = []
        self.comboBoxList = []
        self.currentValueLabelList = []
        self.createSliders()

        # spacer = QWidget()
        # spacer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        # self.layout.addWidget(spacer)

        # Set Main Layout of this page
        self.setLayout(self.layout)

    def createSliders(self):
        for i in range(len(self.flightmodeList)):
            self.sliderList.append(QRangeSlider())
            self.sliderList[i].setMin(0)
            self.sliderList[i].setMax(48)
            self.sliderList[i].setBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);')
            self.sliderList[i].handle.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);') # #282, stop:1 #393
            self.sliderList[i].startValueChanged.connect(self.startvaluechange)
            self.sliderList[i].endValueChanged.connect(self.endvaluechange)
            label = QLabel(self.flightmodeList[i])
            label.setFont(QFont("Times", 22, QFont.Bold))
            self.comboBoxList.append(QComboBox())
            channelList = ["OFF"] + ["Ch. "+str(x) for x in range(5,15)]
            self.comboBoxList[i].addItems(channelList)
            self.comboBoxList[i].currentIndexChanged.connect(self.comboBoxValueChanged)
            self.currentValueLabelList.append(QLabel("900"))
            self.scrollAreaLayout.addWidget(label, i, 0)
            self.scrollAreaLayout.addWidget(self.comboBoxList[i], i, 1)
            self.scrollAreaLayout.addWidget(self.currentValueLabelList[i], i, 2)
            self.scrollAreaLayout.addWidget(self.sliderList[i], i, 3)

    def startvaluechange(self, value):
        pass

    def endvaluechange(self, value):
        pass

    def setRanges(self):
        # self.qsObj = qsObj
        self.getModeGroups()
        for i in range(len(self.flightmodeList)):
            settings = self.getRange(self.flightmodeList[i])
            if len(settings) > 0:
                self.comboBoxList[i].setCurrentIndex(settings[1]+1)
            if self.comboBoxList[i].currentIndex() == 0:
                self.sliderList[i].handle.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);')
                self.sliderList[i].setRange(16, 32)
            else:
                self.sliderList[i].handle.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #282, stop:1 #393);')
                self.sliderList[i].setRange(settings[2], settings[3])

    def getModeGroups(self):
        for i in range(int(len(self.qsObj.msp_mode_ranges)/4)):
            tempList = self.qsObj.msp_mode_ranges[4*i:4*i+4]
            if tempList[0] == 0 and tempList[1] == 0 and tempList[2] == 0 and tempList[3] == 0:
                pass
            else:
                self.modeGroups.append(tempList)

    def getRange(self, modename):
        retSetting = []
        modeIndex = self.qsObj.msp_boxnames.index(modename)
        if modeIndex >= 0:
            modeId = self.qsObj.msp_boxids[modeIndex]
            # rangeGroupIndex = [i for i,x in enumerate(self.modeGroups) if x[0]==modeId]
            # if rangeGroupIndex>=0:
            rangeGroups = list(filter(lambda x: x[0]==modeId, self.modeGroups))
            if len(rangeGroups) > 0:
                retSetting = rangeGroups[0]
        return retSetting

    def comboBoxValueChanged(self):
        for i in range(len(self.flightmodeList)):
            if self.comboBoxList[i].currentIndex() == 0:
                self.sliderList[i].handle.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);')
            else:
                self.sliderList[i].handle.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #282, stop:1 #393);')

    def save(self):
        saveFlightModeList = []
        for i in range(len(self.flightmodeList)):
            boxIndex = self.qsObj.msp_boxnames.index(self.flightmodeList[i])
            boxId = self.qsObj.msp_boxids[boxIndex]
            raw_channel = self.comboBoxList[i].currentIndex()
            if raw_channel != 0:
                channel = raw_channel - 1
                saveFlightModeList.append([boxId, channel, self.sliderList[i].start(), self.sliderList[i].end()])
                # print(self.flightmodeList[i])
        self.flightmodeSaveSignal.emit(saveFlightModeList)
