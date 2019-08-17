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
__copyright__ = "Copyright 2018, Tairan Liu"
__credits__ = ["Tairan Liu", "Other Supporters"]
__license__ = "GPLv3"
__version__ = "0.0-dev"
__maintainer__ = "Tairan Liu"
__email__ = "liutairan2012@gmail.com"
__status__ = "Development"

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

from FlashFirmware import FlashFirmware

class CoverPageWidget(QWidget):
    connectionStatusChangedSignal = pyqtSignal()
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.initUI()
        self.connectionStatus = False

    def initUI(self):
        self.bundle_dir = os.path.dirname(os.path.abspath(__file__))
        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)

        # Create GroupBoxes
        welcomeGroupBox = QGroupBox(self)
        docsGroupBox = QGroupBox(self)
        flashGroupBox = QGroupBox(self)
        # welcomeGroupBox.setMaximumWidth(350)
        # docsGroupBox.setMaximumWidth(320)
        flashGroupBox.setMaximumWidth(480)
        self.layout.addWidget(welcomeGroupBox)
        self.layout.addWidget(docsGroupBox)
        self.layout.addWidget(flashGroupBox)

        # Welcome GroupBox
        welcomeGroupBoxLayout = QVBoxLayout()

        welcomeTitleLabel = QLabel("Welcome")
        welcomeTitleLabel.setFont(QFont("Times", 26, QFont.Bold))
        welcomeTitleLabel.setStyleSheet("QLabel {color:white;}")
        welcomeGroupBoxLayout.addWidget(welcomeTitleLabel)

        introLabel = QLabel("AutonomousFlight Configurator is used to \n" \
                             "configure AutonomousFlight firmware based \n" \
                             "flight controllers. \n" \
                             "It works with QTGCS, which is a grouped \n" \
                             "drones ground control station. \n" \
                             "It uses a modified MSP-like communication \n" \
                             "protocol to do communication work, such \n" \
                             "as remote control and telemetry. \n")
        introLabel.setStyleSheet("QLabel {color:white;}")
        welcomeGroupBoxLayout.addWidget(introLabel)

        thanksLabel = QLabel("Special Thanks")
        thanksLabel.setFont(QFont("Times", 20, QFont.Bold))
        thanksLabel.setStyleSheet("QLabel {color:white;}")
        welcomeGroupBoxLayout.addWidget(thanksLabel)

        supporterLabelsLayout = QVBoxLayout()
        supporterLabelsLayout.setAlignment(Qt.AlignLeft)
        self.supporterLabelList = []
        self.loadSupporters()
        for supporterLabel in self.supporterLabelList:
            supporterLabelsLayout.addWidget(supporterLabel)
        welcomeGroupBoxLayout.addLayout(supporterLabelsLayout)

        welcomeGroupBoxLayout.addStretch(1)
        welcomeGroupBox.setLayout(welcomeGroupBoxLayout)

        # Document GroupBox
        docsGroupBoxLayout = QVBoxLayout()

        docsTitleLabel = QLabel("Documents")
        docsTitleLabel.setFont(QFont("Times", 26, QFont.Bold))
        docsTitleLabel.setStyleSheet("QLabel {color:white;}")
        docsGroupBoxLayout.addWidget(docsTitleLabel)

        docLabelsLayout = QVBoxLayout()
        docLabelsLayout.setAlignment(Qt.AlignLeft)
        self.docLabelList = []
        self.loadDocs()
        for docLabel in self.docLabelList:
            docLabelsLayout.addWidget(docLabel)
        docsGroupBoxLayout.addLayout(docLabelsLayout)

        docsGroupBoxLayout.addStretch(1)
        docsGroupBox.setLayout(docsGroupBoxLayout)

        # Flash GroupBox
        flashGroupBoxLayout = QVBoxLayout()

        flashTitleLabel = QLabel("Flash Firmware")
        flashTitleLabel.setFont(QFont("Times", 26, QFont.Bold))
        flashTitleLabel.setStyleSheet("QLabel {color:white;}")
        flashGroupBoxLayout.addWidget(flashTitleLabel)

        self.chooseBoardTypeComboBox = QComboBox()
        flashGroupBoxLayout.addWidget(self.chooseBoardTypeComboBox)
        self.loadBoardNames()
        self.chooseFirmwareVersionComboBox = QComboBox()
        flashGroupBoxLayout.addWidget(self.chooseFirmwareVersionComboBox)
        self.loadFirmwareVersions()

        wirelessLabel = QLabel("Wireless Mode")
        wirelessLabel.setStyleSheet("QLabel {background-color:white; border: none;}")
        wirelessLabel.setFixedSize(QSize(90,24))
        wirelessLabel.setMargin(0)

        # Switch Icon Image
        self.switchOFFImage = QPixmap(self.bundle_dir + "/Pics/OFF.png")
        self.switchONImage = QPixmap(self.bundle_dir + "/Pics/ON.png")

        self.rebootSequenceToggleButton = QPushButton("OFF", self)
        self.rebootSequenceToggleButton.setIcon(QIcon(self.switchOFFImage))
        self.rebootSequenceToggleButton.setIconSize(QSize(52,24))
        self.rebootSequenceToggleButton.setStyleSheet("QPushButton {background-color:rgb(122,122,122); border: none;}")
        self.rebootSequenceToggleButton.clicked.connect(self.rebootSequenceToggleButtonClicked)
        rebootSequenceLabel = QLabel("No reboot sequence")
        rebootSequenceLabel.setStyleSheet("QLabel {background-color:rgb(122,122,122);}")
        row3RightSpacer = QWidget()
        row3RightSpacer.setStyleSheet("QWidget {background-color:rgb(122,122,122);}")
        row3RightSpacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        row3Layout = QHBoxLayout()
        row3Layout.addWidget(self.rebootSequenceToggleButton)
        row3Layout.addWidget(rebootSequenceLabel)
        row3Layout.addWidget(row3RightSpacer)
        flashGroupBoxLayout.addLayout(row3Layout)

        self.fullChipEraseToggleButton = QPushButton("ON", self)
        self.fullChipEraseToggleButton.setIcon(QIcon(self.switchONImage))
        self.fullChipEraseToggleButton.setIconSize(QSize(52,24))
        self.fullChipEraseToggleButton.setStyleSheet("QPushButton {background-color:rgb(122,122,122); border: none;}")
        self.fullChipEraseToggleButton.clicked.connect(self.fullChipEraseToggleButtonClicked)
        fullChipEraseLabel = QLabel("Full chip erase")
        fullChipEraseLabel.setStyleSheet("QLabel {background-color:rgb(122,122,122);}")
        row4RightSpacer = QWidget()
        row4RightSpacer.setStyleSheet("QWidget {background-color:rgb(122,122,122);}")
        row4RightSpacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        row4Layout = QHBoxLayout()
        row4Layout.addWidget(self.fullChipEraseToggleButton)
        row4Layout.addWidget(fullChipEraseLabel)
        row4Layout.addWidget(row4RightSpacer)
        flashGroupBoxLayout.addLayout(row4Layout)

        self.manualBaudRateToggleButton = QPushButton("ON", self)
        self.manualBaudRateToggleButton.setIcon(QIcon(self.switchONImage))
        self.manualBaudRateToggleButton.setIconSize(QSize(52,24))
        self.manualBaudRateToggleButton.setStyleSheet("QPushButton {background-color:rgb(122,122,122); border: none;}")
        self.manualBaudRateToggleButton.clicked.connect(self.manualBaudRateToggleButtonClicked)
        manualBaudRateLabel = QLabel("Manual Baud Rate")
        manualBaudRateLabel.setStyleSheet("QLabel {background-color:rgb(122,122,122);}")
        self.manualBaudRateComboBox = QComboBox()
        self.manualBaudRateChoices = ["921600", "460800", "256000", "230400", "115200", "57600", "38400", "19200", "9600"]
        self.manualBaudRateComboBox.addItems(self.manualBaudRateChoices)
        self.manualBaudRateComboBox.setCurrentIndex(4)
        self.manualBaudRateComboBox.setStyleSheet("QComboBox {background-color:rgb(122,122,122);}")
        row5RightSpacer = QWidget()
        row5RightSpacer.setStyleSheet("QWidget {background-color:rgb(122,122,122);}")
        row5RightSpacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        row5Layout = QHBoxLayout()
        row5Layout.addWidget(self.manualBaudRateToggleButton)
        row5Layout.addWidget(manualBaudRateLabel)
        row5Layout.addWidget(self.manualBaudRateComboBox)
        row5Layout.addWidget(row5RightSpacer)
        flashGroupBoxLayout.addLayout(row5Layout)

        self.progressBar = QProgressBar(self)
        #progressBar.setMaximumWidth(410)
        self.progress = 0
        flashGroupBoxLayout.addWidget(self.progressBar)
        self.progressBar.setValue(self.progress)
        self.progressLabel = QLabel()
        flashGroupBoxLayout.addWidget(self.progressLabel)

        loadFirmwareButton = QPushButton("Load Firmware", self)
        flashGroupBoxLayout.addWidget(loadFirmwareButton)

        self.flashFirmwareButton = QPushButton("Flash Firmware", self)
        self.flashFirmwareButton.clicked.connect(self.flashFirmware)
        flashGroupBoxLayout.addWidget(self.flashFirmwareButton)

        flashGroupBoxLayout.addStretch(1)
        flashGroupBox.setLayout(flashGroupBoxLayout)

        # Set Main Layout of this page
        self.setLayout(self.layout)
        self.setStyleSheet("background-color:gray;")

    def connectionResp(self):
        self.connectionStatusChangedSignal.emit()

    def loadBoardNames(self):
        boardList = ["Serious Pro Racing F3", "Serious Pro Racing F4"]
        self.chooseBoardTypeComboBox.clear()
        self.chooseBoardTypeComboBox.addItems(boardList)
        self.chooseBoardTypeComboBox.setCurrentIndex(0)

    def loadFirmwareVersions(self):
        versionList = ["AutonomousFlight 1.9.3", "AutonomousFlight 2.0.1", "iNavFlight 1.9.1", "iNavFlight 2.0.0"]
        self.chooseFirmwareVersionComboBox.clear()
        self.chooseFirmwareVersionComboBox.addItems(versionList)
        self.chooseFirmwareVersionComboBox.setCurrentIndex(1)

    def rebootSequenceToggleButtonClicked(self):
        if self.rebootSequenceToggleButton.text() == "OFF":
            self.rebootSequenceToggleButton.setText("ON")
            self.rebootSequenceToggleButton.setIcon(QIcon(self.switchONImage))
        elif self.rebootSequenceToggleButton.text() == "ON":
            self.rebootSequenceToggleButton.setText("OFF")
            self.rebootSequenceToggleButton.setIcon(QIcon(self.switchOFFImage))

    def fullChipEraseToggleButtonClicked(self):
        if self.fullChipEraseToggleButton.text() == "OFF":
            self.fullChipEraseToggleButton.setText("ON")
            self.fullChipEraseToggleButton.setIcon(QIcon(self.switchONImage))
        elif self.fullChipEraseToggleButton.text() == "ON":
            self.fullChipEraseToggleButton.setText("OFF")
            self.fullChipEraseToggleButton.setIcon(QIcon(self.switchOFFImage))

    def manualBaudRateToggleButtonClicked(self):
        if self.manualBaudRateToggleButton.text() == "OFF":
            self.manualBaudRateToggleButton.setText("ON")
            self.manualBaudRateToggleButton.setIcon(QIcon(self.switchONImage))
        elif self.manualBaudRateToggleButton.text() == "ON":
            self.manualBaudRateToggleButton.setText("OFF")
            self.manualBaudRateToggleButton.setIcon(QIcon(self.switchOFFImage))

    def loadDocs(self):
        tempLinkList = ["<a href=\"http://github.com/liutairan\">CLI Sample</a>",
                        "<a href=\"http://github.com/liutairan\">Feature Mask</a>",
                        "<a href=\"http://github.com/liutairan\">MSP Codes</a>",
                        "<a href=\"http://github.com/liutairan\">Connection Graph</a>"]
        for link in tempLinkList:
            tempLabel = QLabel()
            tempLabel.setOpenExternalLinks(True)
            tempLabel.setText(link)
            self.docLabelList.append(tempLabel)

    def loadSupporters(self):
        imageLinkList = ["/Pics/lab-logo.png",
                         "/Pics/inav-logo.png",
                         "/Pics/cleanflight-logo.png",
                         "/Pics/seriously-pro-logo.png"]
        scalePairList = [[183,64],
                         [260,66],
                         [257,67],
                         [125,107]]
        for i in range(len(imageLinkList)):
            tempLabel = QLabel()
            imageLink = self.bundle_dir + imageLinkList[i]
            tempImage = QPixmap(imageLink)
            scalePair = scalePairList[i]
            tempImage = tempImage.scaled(scalePair[0], scalePair[1])
            tempLabel.setPixmap(tempImage)
            self.supporterLabelList.append(tempLabel)

    def flashFirmware(self):
        flashHandle = FlashFirmware(self)
        flashHandle.progressChangedSignal.connect(self.updateProgressBar)
        flashHandle.writeWithVerifyAndStartExecution()
        # the function below is used to simulate the process rather than connect to a real board.
        # flashHandle.sendoutDataSimulate()
        # Start the timer of checking stdout of the stm32flash app.
        flashHandle.start()

    def updateProgressBar(self, valueString):
        value = float(valueString.split("%")[0])
        self.progress = int(value)
        # print(self.progress)
        self.progressLabel.setText("Current flash progress: " + str(value) + "%")
        self.progressBar.setValue(self.progress)
