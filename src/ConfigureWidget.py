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

class ConfigureWidget(QWidget):
    configureSaveSignal = pyqtSignal(list)
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
        self.scrollAreaGroupBox = QGroupBox(self)
        self.scrollAreaLayout = QVBoxLayout()
        self.scrollAreaGroupBox.setLayout(self.scrollAreaLayout)
        self.scrollArea.setWidget(self.scrollAreaGroupBox)
        self.scrollArea.setWidgetResizable(True)
        self.layout.addWidget(self.scrollArea)

        # Port Group
        portGroupBox = QGroupBox("Port", self)
        self.scrollAreaLayout.addWidget(portGroupBox)
        self.portGroupBoxLayout = QGridLayout()
        self.portGroupBoxInit()
        portGroupBox.setLayout(self.portGroupBoxLayout)

        #
        mainConfigureLayout = QHBoxLayout()
        self.scrollAreaLayout.addLayout(mainConfigureLayout)

        # First Column
        mainConfigureCol1Layout = QVBoxLayout()
        mainConfigureLayout.addLayout(mainConfigureCol1Layout)
        # Second Column
        mainConfigureCol2Layout = QVBoxLayout()
        mainConfigureLayout.addLayout(mainConfigureCol2Layout)

        # First column
        # Mixer Group
        mixerGroupBox = QGroupBox("Mixer", self)
        mainConfigureCol1Layout.addWidget(mixerGroupBox)
        self.mixerGroupBoxLayout = QVBoxLayout()
        self.mixerGroupBoxInit()
        self.mixerGroupBoxLayout.addStretch(1)
        mixerGroupBox.setLayout(self.mixerGroupBoxLayout)

        # Sensors Group
        sensorGroupBox = QGroupBox("Sensors", self)
        mainConfigureCol1Layout.addWidget(sensorGroupBox)
        self.sensorGroupBoxLayout = QGridLayout()
        self.sensorGroupBoxInit()
        sensorGroupBox.setLayout(self.sensorGroupBoxLayout)

        # Board Alignment Group
        boardAlignmentGroupBox = QGroupBox("Board Alignment", self)
        mainConfigureCol1Layout.addWidget(boardAlignmentGroupBox)
        self.boardAlignmentGroupBoxLayout = QGridLayout()
        self.boardAlignmentGroupBoxInit()
        boardAlignmentGroupBox.setMaximumWidth(500)
        boardAlignmentGroupBox.setLayout(self.boardAlignmentGroupBoxLayout)

        # Receiver Group
        receiverGroupBox = QGroupBox("Receiver", self)
        mainConfigureCol1Layout.addWidget(receiverGroupBox)
        self.receiverGroupBoxLayout = QGridLayout()
        self.receiverGroupBoxInit()
        receiverGroupBox.setLayout(self.receiverGroupBoxLayout)

        # GPS Group
        gpsGroupBox = QGroupBox("GPS", self)
        mainConfigureCol1Layout.addWidget(gpsGroupBox)
        self.gpsGroupBoxLayout = QGridLayout()
        self.gpsGroupBoxInit()
        gpsGroupBox.setMaximumWidth(500)
        gpsGroupBox.setLayout(self.gpsGroupBoxLayout)

        # 3D Group
        threeDGroupBox = QGroupBox("3D", self)
        mainConfigureCol1Layout.addWidget(threeDGroupBox)
        self.threeDGroupBoxLayout = QGridLayout()
        self.threeDGroupBoxInit()
        threeDGroupBox.setMaximumWidth(500)
        threeDGroupBox.setLayout(self.threeDGroupBoxLayout)

        # Name Group
        nameGroupBox = QGroupBox("Name", self)
        mainConfigureCol1Layout.addWidget(nameGroupBox)
        self.nameGroupBoxLayout = QGridLayout()
        self.nameGroupBoxInit()
        nameGroupBox.setMaximumWidth(500)
        nameGroupBox.setLayout(self.nameGroupBoxLayout)

        # Other Features Group
        otherFeatureGroupBox = QGroupBox("Other Features", self)
        mainConfigureCol1Layout.addWidget(otherFeatureGroupBox)
        self.otherFeatureGroupBoxLayout = QGridLayout()
        self.otherFeatureGroupBoxInit()
        otherFeatureGroupBox.setMaximumWidth(500)
        otherFeatureGroupBox.setLayout(self.otherFeatureGroupBoxLayout)

        mainConfigureCol1Layout.addStretch(1)

        # ESC/Motor Feature Group
        escmotorGroupBox = QGroupBox("ESC/Motor Feature", self)
        mainConfigureCol2Layout.addWidget(escmotorGroupBox)
        self.escmotorGroupBoxLayout = QGridLayout()
        self.escmotorGroupBoxInit()
        escmotorGroupBox.setMaximumWidth(500)
        escmotorGroupBox.setLayout(self.escmotorGroupBoxLayout)

        # System Configure Group
        systemConfigureGroupBox = QGroupBox("System Configure", self)
        mainConfigureCol2Layout.addWidget(systemConfigureGroupBox)
        self.systemConfigureGroupBoxLayout = QGridLayout()
        self.systemConfigureGroupBoxInit()
        systemConfigureGroupBox.setMaximumWidth(500)
        systemConfigureGroupBox.setLayout(self.systemConfigureGroupBoxLayout)

        # Battery Voltage Group
        batteryVoltageGroupBox = QGroupBox("Battery Voltage", self)
        mainConfigureCol2Layout.addWidget(batteryVoltageGroupBox)
        self.batteryVoltageGroupBoxLayout = QGridLayout()
        self.batteryVoltageGroupBoxInit()
        batteryVoltageGroupBox.setMaximumWidth(500)
        batteryVoltageGroupBox.setLayout(self.batteryVoltageGroupBoxLayout)

        # Current Sensor Group
        currentSensorGroupBox = QGroupBox("Current Sensor", self)
        mainConfigureCol2Layout.addWidget(currentSensorGroupBox)
        self.currentSensorGroupBoxLayout = QGridLayout()
        self.currentSensorGroupBoxInit()
        currentSensorGroupBox.setMaximumWidth(500)
        currentSensorGroupBox.setLayout(self.currentSensorGroupBoxLayout)

        # Battery Capacity Group
        batteryCapacityGroupBox = QGroupBox("Battery Capacity", self)
        mainConfigureCol2Layout.addWidget(batteryCapacityGroupBox)
        self.batteryCapacityGroupBoxLayout = QGridLayout()
        self.batteryCapacityGroupBoxInit()
        batteryCapacityGroupBox.setMaximumWidth(500)
        batteryCapacityGroupBox.setLayout(self.batteryCapacityGroupBoxLayout)

        # Fourth column
        # Failsafe Settings Group
        failsafeSettingGroupBox = QGroupBox("Failsafe Settings", self)
        mainConfigureCol2Layout.addWidget(failsafeSettingGroupBox)
        self.failsafeSettingGroupBoxLayout = QGridLayout()
        self.failsafeSettingGroupBoxInit()
        failsafeSettingGroupBox.setMaximumWidth(500)
        failsafeSettingGroupBox.setLayout(self.failsafeSettingGroupBoxLayout)

        self.setLayout(self.layout)

    def initValues(self):
        self.loadValuesFromDefault()
        # self.setUIDefaultValues()
        self.userSettingData = dict(self.defaultSettingData)
        self.setUIValues()

    def setUIDefaultValues(self):
        pass

    # Set UI widget values with userSettingData
    def setUIValues(self):
        # Port
        for i in range(3):
            # Data
            if self.userSettingData['Port'][str(i)][0] == 1:
                self.dataSwitchValue[i] = True
                self.dataSwitch[i].setIcon(QIcon(self.switchONImage))
            else:
                self.dataSwitchValue[i] = False
                self.dataSwitch[i].setIcon(QIcon(self.switchOFFImage))
            self.dataBaudrateComboBox[i].clear()
            self.dataBaudrateComboBox[i].addItems(self.userSettingData['Port']['Baudrate'])
            self.dataBaudrateComboBox[i].setCurrentIndex(self.userSettingData['Port'][str(i)][1])

            # Telemetry
            self.telemetryTypeComboBox[i].clear()
            self.telemetryTypeComboBox[i].addItems(self.userSettingData['Port']['Telemetry'])
            if self.userSettingData['Port'][str(i)][0] == self.userSettingData['Port']['FunctionMask']["TELEMETRY_FRSKY"]:
                self.telemetryTypeComboBox[i].setCurrentIndex(self.userSettingData['Port']['Telemetry'].index("FrSky"))
            elif self.userSettingData['Port'][str(i)][0] == self.userSettingData['Port']['FunctionMask']["TELEMETRY_HOTT"]:
                self.telemetryTypeComboBox[i].setCurrentIndex(self.userSettingData['Port']['Telemetry'].index("HoTT"))
            elif self.userSettingData['Port'][str(i)][0] == self.userSettingData['Port']['FunctionMask']["TELEMETRY_LTM"]:
                self.telemetryTypeComboBox[i].setCurrentIndex(self.userSettingData['Port']['Telemetry'].index("LTM"))
            elif self.userSettingData['Port'][str(i)][0] == self.userSettingData['Port']['FunctionMask']["TELEMETRY_SMARTPORT"]:
                self.telemetryTypeComboBox[i].setCurrentIndex(self.userSettingData['Port']['Telemetry'].index("SmartPort"))
            elif self.userSettingData['Port'][str(i)][0] == self.userSettingData['Port']['FunctionMask']["TELEMETRY_MAVLINK"]:
                self.telemetryTypeComboBox[i].setCurrentIndex(self.userSettingData['Port']['Telemetry'].index("MAVLink"))
            elif self.userSettingData['Port'][str(i)][0] == self.userSettingData['Port']['FunctionMask']["TELEMETRY_IBUS"]:
                self.telemetryTypeComboBox[i].setCurrentIndex(self.userSettingData['Port']['Telemetry'].index("IBUS"))
            else:
                self.telemetryTypeComboBox[i].setCurrentIndex(self.userSettingData['Port']['Telemetry'].index("Disabled"))
            self.telemetryBaudrateComboBox[i].clear()
            self.telemetryBaudrateComboBox[i].addItems(self.userSettingData['Port']['Baudrate'])
            self.telemetryBaudrateComboBox[i].setCurrentIndex(self.userSettingData['Port'][str(i)][3])

            # RX
            if self.userSettingData['Port'][str(i)][0] == 64:
                self.rxSwitchValue[i] = True
                self.rxSwitch[i].setIcon(QIcon(self.switchONImage))
            elif self.userSettingData['Port'][str(i)][0] != 64:
                self.rxSwitchValue[i] = False
                self.rxSwitch[i].setIcon(QIcon(self.switchOFFImage))

            # Sensor
            self.sensorTypeComboBox[i].clear()
            self.sensorTypeComboBox[i].addItems(self.userSettingData['Port']['Sensor'])
            if self.userSettingData['Port'][str(i)][0] == self.userSettingData['Port']['FunctionMask']["GPS"]:
                self.sensorTypeComboBox[i].setCurrentIndex(self.userSettingData['Port']['Sensor'].index("GPS"))
            else:
                self.sensorTypeComboBox[i].setCurrentIndex(self.userSettingData['Port']['Sensor'].index("Disabled"))
            self.sensorBaudrateComboBox[i].clear()
            self.sensorBaudrateComboBox[i].addItems(self.userSettingData['Port']['Baudrate'])
            self.sensorBaudrateComboBox[i].setCurrentIndex(self.userSettingData['Port'][str(i)][2])

            # Peripherals
            self.peripheralsTypeComboBox[i].clear()
            self.peripheralsTypeComboBox[i].addItems(self.userSettingData['Port']['Peripherals'])
            if self.userSettingData['Port'][str(i)][0] == self.userSettingData['Port']['FunctionMask']["BLACKBOX"]:
                self.peripheralsTypeComboBox[i].setCurrentIndex(self.userSettingData['Port']['Peripherals'].index("Blackbox"))
            elif self.userSettingData['Port'][str(i)][0] == self.userSettingData['Port']['FunctionMask']["RCDEVICE"]:
                self.peripheralsTypeComboBox[i].setCurrentIndex(self.userSettingData['Port']['Peripherals'].index("RunCam Device"))
            elif self.userSettingData['Port'][str(i)][0] == self.userSettingData['Port']['FunctionMask']["VTX_SMARTAUDIO"]:
                self.peripheralsTypeComboBox[i].setCurrentIndex(self.userSettingData['Port']['Peripherals'].index("TBS SmartAudio"))
            elif self.userSettingData['Port'][str(i)][0] == self.userSettingData['Port']['FunctionMask']["VTX_TRAMP"]:
                self.peripheralsTypeComboBox[i].setCurrentIndex(self.userSettingData['Port']['Peripherals'].index("IRC Tramp"))
            else:
                self.peripheralsTypeComboBox[i].setCurrentIndex(self.userSettingData['Port']['Peripherals'].index("Disabled"))
            self.peripheralsBaudrateComboBox[i].clear()
            self.peripheralsBaudrateComboBox[i].addItems(self.userSettingData['Port']['Baudrate'])
            self.peripheralsBaudrateComboBox[i].setCurrentIndex(self.userSettingData['Port'][str(i)][4])

        # Mixer
        self.mixerComboBox.clear()
        self.mixerComboBox.addItems(self.userSettingData['Mixer']['Mixer Options'])
        self.mixerComboBox.setCurrentIndex(self.userSettingData['Mixer']['Mixer'])

        # Sensors
        self.sensorSettings['Accelerometer'].clear()
        self.sensorSettings['Accelerometer'].addItems(self.userSettingData['Sensors']['Accelerometer Options'])
        self.sensorSettings['Accelerometer'].setCurrentIndex(self.userSettingData['Sensors']['Accelerometer'])
        self.sensorSettings['Magnetometer'].clear()
        self.sensorSettings['Magnetometer'].addItems(self.userSettingData['Sensors']['Magnetometer Options'])
        self.sensorSettings['Magnetometer'].setCurrentIndex(self.userSettingData['Sensors']['Magnetometer'])
        self.sensorSettings['Barometer'].clear()
        self.sensorSettings['Barometer'].addItems(self.userSettingData['Sensors']['Barometer Options'])
        self.sensorSettings['Barometer'].setCurrentIndex(self.userSettingData['Sensors']['Barometer'])
        self.sensorSettings['Pitot tube'].clear()
        self.sensorSettings['Pitot tube'].addItems(self.userSettingData['Sensors']['Pitot tube Options'])
        self.sensorSettings['Pitot tube'].setCurrentIndex(self.userSettingData['Sensors']['Pitot tube'])
        self.sensorSettings['Rangefinder'].clear()
        self.sensorSettings['Rangefinder'].addItems(self.userSettingData['Sensors']['Rangefinder Options'])
        self.sensorSettings['Rangefinder'].setCurrentIndex(self.userSettingData['Sensors']['Rangefinder'])

        # Board and Sensor Alignment
        self.boardAlignmentSettings['Roll degrees'].setValue(self.userSettingData['Board and Sensor Alignment']['Roll degrees'])
        self.boardAlignmentSettings['Pitch degrees'].setValue(self.userSettingData['Board and Sensor Alignment']['Pitch degrees'])
        self.boardAlignmentSettings['Yaw degrees'].setValue(self.userSettingData['Board and Sensor Alignment']['Yaw degrees'])
        self.boardAlignmentSettings['Gyro Alignment'].clear()
        self.boardAlignmentSettings['Gyro Alignment'].addItems(self.userSettingData['Board and Sensor Alignment']['Gyro alignment Options'])
        self.boardAlignmentSettings['Gyro Alignment'].setCurrentIndex(self.userSettingData['Board and Sensor Alignment']['Gyro alignment'])
        self.boardAlignmentSettings['Acc Alignment'].clear()
        self.boardAlignmentSettings['Acc Alignment'].addItems(self.userSettingData['Board and Sensor Alignment']['Acc alignment Options'])
        self.boardAlignmentSettings['Acc Alignment'].setCurrentIndex(self.userSettingData['Board and Sensor Alignment']['Acc alignment'])
        self.boardAlignmentSettings['Mag Alignment'].clear()
        self.boardAlignmentSettings['Mag Alignment'].addItems(self.userSettingData['Board and Sensor Alignment']['Mag alignment Options'])
        self.boardAlignmentSettings['Mag Alignment'].setCurrentIndex(self.userSettingData['Board and Sensor Alignment']['Mag alignment'])

        # Receiver Mode
        self.receiverSettings['Receiver Mode'].clear()
        self.receiverSettings['Receiver Mode'].addItems(self.userSettingData['Receiver Mode']['Receiver Mode Options'])
        self.receiverSettings['Receiver Mode'].setCurrentIndex(self.userSettingData['Receiver Mode']['Receiver Mode'])

        # GPS
        if self.userSettingData['GPS']['GPS for navigation and telemetry'] == True:
            self.gpsSettings['GPS for navigation and telemetry switch'] = True
            self.gpsSettings['GPS for navigation and telemetry'].setIcon(QIcon(self.switchONImage))
        elif self.userSettingData['GPS']['GPS for navigation and telemetry'] == False:
            self.gpsSettings['GPS for navigation and telemetry switch'] = False
            self.gpsSettings['GPS for navigation and telemetry'].setIcon(QIcon(self.switchOFFImage))
        self.gpsSettings['Protocol'].clear()
        self.gpsSettings['Protocol'].addItems(self.userSettingData['GPS']['Protocol Options'])
        self.gpsSettings['Protocol'].setCurrentIndex(self.userSettingData['GPS']['Protocol'])
        self.gpsSettings['Ground Assistance Type'].clear()
        self.gpsSettings['Ground Assistance Type'].addItems(self.userSettingData['GPS']['Ground Assistance Type Options'])
        self.gpsSettings['Ground Assistance Type'].setCurrentIndex(self.userSettingData['GPS']['Ground Assistance Type'])
        self.gpsSettings['Magnetometer Declination'].setValue(self.userSettingData['GPS']['Magnetometer Declination'])
        # 3D
        self.threeDSettings['3D Deadband Low'].setValue(self.userSettingData['3D']['3D Deadband Low'])
        self.threeDSettings['3D Deadband High'].setValue(self.userSettingData['3D']['3D Deadband High'])
        self.threeDSettings['3D Neutral'].setValue(self.userSettingData['3D']['3D Neutral'])

        # Personalization
        self.craftNameLineEdit.setText(self.userSettingData['Personalization']['Craft Name'])

        # ESC/Motor Features
        if self.userSettingData['ESC/Motor Features']['Enable motor and servo output'] == True:
            self.escmotorSettings['Enable motor and servo output switch'] = True
            self.escmotorSettings['Enable motor and servo output'].setIcon(QIcon(self.switchONImage))
        elif self.userSettingData['ESC/Motor Features']['Enable motor and servo output'] == False:
            self.escmotorSettings['Enable motor and servo output switch'] = False
            self.escmotorSettings['Enable motor and servo output'].setIcon(QIcon(self.switchOFFImage))
        self.escmotorSettings['ESC protocol'].clear()
        self.escmotorSettings['ESC protocol'].addItems(self.userSettingData['ESC/Motor Features']['ESC protocol Options'])
        self.escmotorSettings['ESC protocol'].currentIndexChanged.connect(self.escProtocolChanged)
        tempESCMotorProtocol = self.userSettingData['ESC/Motor Features']['ESC protocol']
        self.escmotorSettings['ESC protocol'].setCurrentIndex(tempESCMotorProtocol)
        tempESCRefreshRateOptions = self.userSettingData['ESC/Motor Features']['ESC refresh rate Options'][self.userSettingData['ESC/Motor Features']['ESC protocol Options'][tempESCMotorProtocol]]
        self.escmotorSettings['ESC refresh rate'].clear()
        self.escmotorSettings['ESC refresh rate'].addItems(tempESCRefreshRateOptions)
        self.escmotorSettings['ESC refresh rate'].setCurrentIndex(self.userSettingData['ESC/Motor Features']['ESC refresh rate'])
        self.escmotorSettings['Servo refresh rate'].clear()
        self.escmotorSettings['Servo refresh rate'].addItems(self.userSettingData['ESC/Motor Features']['Servo refresh rate Options'])
        self.escmotorSettings['Servo refresh rate'].setCurrentIndex(self.userSettingData['ESC/Motor Features']['Servo refresh rate'])
        if self.userSettingData['ESC/Motor Features']['Do not spin the motors when armed'] == True:
            self.escmotorSettings['Do not spin the motors when armed switch'] = True
            self.escmotorSettings['Do not spin the motors when armed'].setIcon(QIcon(self.switchONImage))
        elif self.userSettingData['ESC/Motor Features']['Do not spin the motors when armed'] == False:
            self.escmotorSettings['Do not spin the motors when armed switch'] = False
            self.escmotorSettings['Do not spin the motors when armed'].setIcon(QIcon(self.switchOFFImage))
        self.escmotorSettings['Min throttle'].setValue(self.userSettingData['ESC/Motor Features']['Min throttle'])
        self.escmotorSettings['Mid throttle'].setValue(self.userSettingData['ESC/Motor Features']['Mid throttle'])
        self.escmotorSettings['Max throttle'].setValue(self.userSettingData['ESC/Motor Features']['Max throttle'])
        self.escmotorSettings['Min command'].setValue(self.userSettingData['ESC/Motor Features']['Min command'])

        # System Configuration
        self.systemConfigureSettings['Gyroscope LFP cutoff frequency'].clear()
        self.systemConfigureSettings['Gyroscope LFP cutoff frequency'].addItems(self.userSettingData['System Configuration']['Gyroscope LPF cutoff frequency Options'])
        self.systemConfigureSettings['Gyroscope LFP cutoff frequency'].setCurrentIndex(self.userSettingData['System Configuration']['Gyroscope LPF cutoff frequency'])
        self.systemConfigureSettings['Asynchronous mode'].clear()
        self.systemConfigureSettings['Asynchronous mode'].addItems(self.userSettingData['System Configuration']['Asynchronous mode Options'])
        self.systemConfigureSettings['Asynchronous mode'].setCurrentIndex(self.userSettingData['System Configuration']['Asynchronous mode'])
        if self.userSettingData['System Configuration']['Synchronize looptime with gyroscope'] == True:
            self.systemConfigureSettings['Synchronize looptime with gyroscope switch'] = True
            self.systemConfigureSettings['Synchronize looptime with gyroscope'].setIcon(QIcon(self.switchONImage))
        elif self.userSettingData['System Configuration']['Synchronize looptime with gyroscope'] == False:
            self.systemConfigureSettings['Synchronize looptime with gyroscope switch'] = False
            self.systemConfigureSettings['Synchronize looptime with gyroscope'].setIcon(QIcon(self.switchOFFImage))
        self.systemConfigureSettings['Flight controller loop time'].clear()
        self.systemConfigureSettings['Flight controller loop time'].addItems(self.userSettingData['System Configuration']['Flight controller loop time Options'])
        self.systemConfigureSettings['Flight controller loop time'].setCurrentIndex(self.userSettingData['System Configuration']['Flight controller loop time'])

        # Battery Voltage
        if self.userSettingData['Battery Voltage']['Battery voltage monitoring'] == True:
            self.batteryVoltageSettings['Battery voltage monitoring switch'] = True
            self.batteryVoltageSettings['Battery voltage monitoring'].setIcon(QIcon(self.switchONImage))
        elif self.userSettingData['Battery Voltage']['Battery voltage monitoring'] == False:
            self.batteryVoltageSettings['Battery voltage monitoring switch'] = False
            self.batteryVoltageSettings['Battery voltage monitoring'].setIcon(QIcon(self.switchOFFImage))
        self.batteryVoltageSettings['Min cell voltage'].setValue(self.userSettingData['Battery Voltage']['Min cell voltage'])
        self.batteryVoltageSettings['Max cell voltage'].setValue(self.userSettingData['Battery Voltage']['Max cell voltage'])
        self.batteryVoltageSettings['Warning cell voltage'].setValue(self.userSettingData['Battery Voltage']['Warning cell voltage'])
        self.batteryVoltageSettings['Voltage scale'].setValue(self.userSettingData['Battery Voltage']['Voltage scale'])
        self.batteryVoltageSettings['Battery voltage'].setText(str(self.userSettingData['Battery Voltage']['Battery voltage']))

        # Current Sensor
        if self.userSettingData['Current Sensor']['Battery current monitoring'] == True:
            self.currentSensorSettings['Battery current monitoring switch'] = True
            self.currentSensorSettings['Battery current monitoring'].setIcon(QIcon(self.switchONImage))
        elif self.userSettingData['Current Sensor']['Battery current monitoring'] == False:
            self.currentSensorSettings['Battery current monitoring switch'] = False
            self.currentSensorSettings['Battery current monitoring'].setIcon(QIcon(self.switchOFFImage))
        self.currentSensorSettings['Scale the output voltage to milliamps'].setValue(self.userSettingData['Current Sensor']['Scale the output voltage to milliamps'])
        self.currentSensorSettings['Offset in millivolt steps'].setValue(self.userSettingData['Current Sensor']['Offset in millivolt steps'])
        self.currentSensorSettings['Battery current'].setText(str(self.userSettingData['Current Sensor']['Battery current']))

        # Battery Capacity
        self.batteryCapacitySettings['Unit'].clear()
        self.batteryCapacitySettings['Unit'].addItems(self.userSettingData['Battery Capacity']['Unit Options'])
        self.batteryCapacitySettings['Unit'].setCurrentIndex(self.userSettingData['Battery Capacity']['Unit'])
        self.batteryCapacitySettings['Capacity'].setValue(self.userSettingData['Battery Capacity']['Capacity'])
        self.batteryCapacitySettings['Warning capacity'].setValue(self.userSettingData['Battery Capacity']['Warning capacity'])
        self.batteryCapacitySettings['Critical capacity'].setValue(self.userSettingData['Battery Capacity']['Critical capacity'])

        # Failsafe settings
        self.failsafeSettings['Min length'].setValue(self.userSettingData['Failsafe']['Min length'])
        self.failsafeSettings['Max length'].setValue(self.userSettingData['Failsafe']['Max length'])
        if self.userSettingData['Failsafe']['Failsafe kill switch'] == True:
            self.failsafeSettings['Failsafe Kill Switch switch'] = True
            self.failsafeSettings['Failsafe Kill Switch'].setIcon(QIcon(self.switchONImage))
        elif self.userSettingData['Failsafe']['Failsafe kill switch'] == False:
            self.failsafeSettings['Failsafe Kill Switch switch'] = False
            self.failsafeSettings['Failsafe Kill Switch'].setIcon(QIcon(self.switchOFFImage))
        self.failsafeSettings['Guard time'].setValue(self.userSettingData['Failsafe']['Guard time'])
        self.failsafeSettings['Failsafe throttle low delay'].setValue(self.userSettingData['Failsafe']['Failsafe throttle low delay'])
        tempProcedure = self.userSettingData['Failsafe']['Procedure']
        tempProcedureName = self.userSettingData['Failsafe']['Procedure Options'][tempProcedure]
        self.failsafeSettings[tempProcedureName].setChecked(True)
        self.failsafeSettings['Throttle value while landing'].setValue(self.userSettingData['Failsafe']['Throttle value while landing'])
        self.failsafeSettings['Delay for turning off the motors during failsafe'].setValue(self.userSettingData['Failsafe']['Delay for turning off the motors during failsafe'])
        if self.userSettingData['Failsafe']['Use alternate min distance failsafe procedure'] == True:
            self.failsafeSettings['Use alternate Minimum Distance failsafe procedure when close to home switch'] = True
            self.failsafeSettings['Use alternate Minimum Distance failsafe procedure when close to home'].setIcon(QIcon(self.switchONImage))
        elif self.userSettingData['Failsafe']['Use alternate min distance failsafe procedure'] == False:
            self.failsafeSettings['Use alternate Minimum Distance failsafe procedure when close to home switch'] = False
            self.failsafeSettings['Use alternate Minimum Distance failsafe procedure when close to home'].setIcon(QIcon(self.switchOFFImage))
        self.failsafeSettings['Failsafe min distance'].setValue(self.userSettingData['Failsafe']['Failsafe min distance'])
        self.failsafeSettings['Failsafe min distance procedure'].clear()
        self.failsafeSettings['Failsafe min distance procedure'].addItems(self.userSettingData['Failsafe']['Failsafe min distance procedure Options'])
        self.failsafeSettings['Failsafe min distance procedure'].setCurrentIndex(self.userSettingData['Failsafe']['Failsafe min distance procedure'])
        # Other Features
        featureMask = self.userSettingData['Other Features']['Mask']
        temp = format(featureMask, '032b')
        # RX_PPM
        if temp[31-0] == "1":
            pass
        else:
            pass
        # Voltage monitoring
        if temp[31-1] == "1":
            self.batteryVoltageSettings['Battery voltage monitoring switch'] = True
            self.batteryVoltageSettings['Battery voltage monitoring'].setIcon(QIcon(self.switchONImage))
        else:
            self.batteryVoltageSettings['Battery voltage monitoring switch'] = False
            self.batteryVoltageSettings['Battery voltage monitoring'].setIcon(QIcon(self.switchOFFImage))
        # Profile selection by TX stick command
        if temp[31-2] == "1":
            self.featureSwitchValue[14] = True
            self.featureSwitch[14].setIcon(QIcon(self.switchONImage))
        else:
            self.featureSwitchValue[14] = False
            self.featureSwitch[14].setIcon(QIcon(self.switchOFFImage))
        # RX Serial
        if temp[31-3] == "1":
            pass
        else:
            pass
        # Motor stop
        if temp[31-4] == "1":
            self.escmotorSettings['Do not spin the motors when armed switch'] = True
            self.escmotorSettings['Do not spin the motors when armed'].setIcon(QIcon(self.switchONImage))
        else:
            self.escmotorSettings['Do not spin the motors when armed switch'] = False
            self.escmotorSettings['Do not spin the motors when armed'].setIcon(QIcon(self.switchOFFImage))
        # SERVO_TILT
        if temp[31-5] == "1":
            self.featureSwitchValue[0] = True
            self.featureSwitch[0].setIcon(QIcon(self.switchONImage))
        else:
            self.featureSwitchValue[0] = False
            self.featureSwitch[0].setIcon(QIcon(self.switchOFFImage))
        # SOFTSERIAL
        if temp[31-6] == "1":
            self.featureSwitchValue[1] = True
            self.featureSwitch[1].setIcon(QIcon(self.switchONImage))
        else:
            self.featureSwitchValue[1] = False
            self.featureSwitch[1].setIcon(QIcon(self.switchOFFImage))
        # GPS
        if temp[31-7] == "1":
            self.gpsSettings['GPS for navigation and telemetry switch'] = True
            self.gpsSettings['GPS for navigation and telemetry'].setIcon(QIcon(self.switchONImage))
        else:
            self.gpsSettings['GPS for navigation and telemetry switch'] = False
            self.gpsSettings['GPS for navigation and telemetry'].setIcon(QIcon(self.switchOFFImage))
        if temp[31-8] == "1":
            pass
        else:
            pass
        if temp[31-9] == "1":
            pass
        else:
            pass
        # Telemetry
        if temp[31-10] == "1":
            self.featureSwitchValue[2] = True
            self.featureSwitch[2].setIcon(QIcon(self.switchONImage))
        else:
            self.featureSwitchValue[2] = False
            self.featureSwitch[2].setIcon(QIcon(self.switchOFFImage))
        # Current meter
        if temp[31-11] == "1":
            self.currentSensorSettings['Battery current monitoring switch'] = True
            self.currentSensorSettings['Battery current monitoring'].setIcon(QIcon(self.switchONImage))
        else:
            self.currentSensorSettings['Battery current monitoring switch'] = False
            self.currentSensorSettings['Battery current monitoring'].setIcon(QIcon(self.switchOFFImage))
        # 3D
        if temp[31-12] == "1":
            self.featureSwitchValue[3] = True
            self.featureSwitch[3].setIcon(QIcon(self.switchONImage))
        else:
            self.featureSwitchValue[3] = False
            self.featureSwitch[3].setIcon(QIcon(self.switchOFFImage))
        # rx parallel pwm
        if temp[31-13] == "1":
            pass
        else:
            pass
        # rx msp
        if temp[31-14] == "1":
            pass
        else:
            pass
        # RSSI ADC
        if temp[31-15] == "1":
            self.featureSwitchValue[4] = True
            self.featureSwitch[4].setIcon(QIcon(self.switchONImage))
        else:
            self.featureSwitchValue[4] = False
            self.featureSwitch[4].setIcon(QIcon(self.switchOFFImage))
        # LED Strip
        if temp[31-16] == "1":
            self.featureSwitchValue[5] = True
            self.featureSwitch[5].setIcon(QIcon(self.switchONImage))
        else:
            self.featureSwitchValue[5] = False
            self.featureSwitch[5].setIcon(QIcon(self.switchOFFImage))
        # Dashboard
        if temp[31-17] == "1":
            self.featureSwitchValue[6] = True
            self.featureSwitch[6].setIcon(QIcon(self.switchONImage))
        else:
            self.featureSwitchValue[6] = False
            self.featureSwitch[6].setIcon(QIcon(self.switchOFFImage))
        if temp[31-18] == "1":
            pass
        else:
            pass
        # Blackbox
        if temp[31-19] == "1":
            self.featureSwitchValue[7] = True
            self.featureSwitch[7].setIcon(QIcon(self.switchONImage))
        else:
            self.featureSwitchValue[7] = False
            self.featureSwitch[7].setIcon(QIcon(self.switchOFFImage))
        # CHANNEL_FORWARDING
        if temp[31-20] == "1":
            self.featureSwitchValue[8] = True
            self.featureSwitch[8].setIcon(QIcon(self.switchONImage))
        else:
            self.featureSwitchValue[8] = False
            self.featureSwitch[8].setIcon(QIcon(self.switchOFFImage))
        # TRANSPONDER
        if temp[31-21] == "1":
            pass
        else:
            pass
        # AIRMODE
        if temp[31-22] == "1":
            self.featureSwitchValue[12] = True
            self.featureSwitch[12].setIcon(QIcon(self.switchONImage))
        else:
            self.featureSwitchValue[12] = False
            self.featureSwitch[12].setIcon(QIcon(self.switchOFFImage))
        # SUPEREXPO_RATES
        if temp[31-23] == "1":
            pass
        else:
            pass
        # VTX
        if temp[31-24] == "1":
            pass
        else:
            pass
        # RX SPI
        if temp[31-25] == "1":
            pass
        else:
            pass
        # SOFT SPI
        if temp[31-26] == "1":
            self.featureSwitchValue[9] = True
            self.featureSwitch[9].setIcon(QIcon(self.switchONImage))
        else:
            self.featureSwitchValue[9] = False
            self.featureSwitch[9].setIcon(QIcon(self.switchOFFImage))
        # PWM_SERVO_DRIVER
        if temp[31-27] == "1":
            self.featureSwitchValue[10] = True
            self.featureSwitch[10].setIcon(QIcon(self.switchONImage))
        else:
            self.featureSwitchValue[10] = False
            self.featureSwitch[10].setIcon(QIcon(self.switchOFFImage))
        # PWM_OUTPUT_ENABLE
        if temp[31-28] == "1":
            self.escmotorSettings['Enable motor and servo output switch'] = True
            self.escmotorSettings['Enable motor and servo output'].setIcon(QIcon(self.switchONImage))
        else:
            self.escmotorSettings['Enable motor and servo output switch'] = False
            self.escmotorSettings['Enable motor and servo output'].setIcon(QIcon(self.switchOFFImage))
        # OSD
        if temp[31-29] == "1":
            self.featureSwitchValue[11] = True
            self.featureSwitch[11].setIcon(QIcon(self.switchONImage))
        else:
            self.featureSwitchValue[11] = False
            self.featureSwitch[11].setIcon(QIcon(self.switchOFFImage))
        # fw launch
        if temp[31-30] == "1":
            self.featureSwitchValue[13] = True
            self.featureSwitch[13].setIcon(QIcon(self.switchONImage))
        else:
            self.featureSwitchValue[13] = False
            self.featureSwitch[13].setIcon(QIcon(self.switchOFFImage))
        # Debug Trace
        if temp[31-30] == "1":
            pass
        else:
            pass

    def saveandreboot(self):
        # Get values from UI: UI->userSettingData
        self.getUIValues()
        # userSettingData->qsObj
        self.setQSObj()
        # qsObj->Board write with MSP
        tbsList = []
        self.configureSaveSignal.emit(tbsList)

    # Read widget values and set self.userSettingData: UI->userSettingData
    def getUIValues(self):
        # Port
        for i in range(3):
            # Data
            if self.dataSwitchValue[i] == True:
                self.userSettingData['Port'][str(i)][0] = 1
            elif self.dataSwitchValue[i] == False:
                # Set the value to 0 first, if other features are turned on, then change this value again.
                self.userSettingData['Port'][str(i)][0] = 0
            # Data Baudrate index
            self.userSettingData['Port'][str(i)][1] = self.dataBaudrateComboBox[i].currentIndex()

            # Telemetry
            if self.userSettingData['Port'][str(i)][0] == 0:
                telemetryIndex = self.telemetryTypeComboBox[i].currentIndex()
                if telemetryIndex == self.userSettingData['Port']['Telemetry'].index("FrSky"):
                    self.userSettingData['Port'][str(i)][0] = self.userSettingData['Port']['FunctionMask']["TELEMETRY_FRSKY"]
                elif telemetryIndex == self.userSettingData['Port']['Telemetry'].index("HoTT"):
                    self.userSettingData['Port'][str(i)][0] = self.userSettingData['Port']['FunctionMask']["TELEMETRY_HOTT"]
                elif telemetryIndex == self.userSettingData['Port']['Telemetry'].index("LTM"):
                    self.userSettingData['Port'][str(i)][0] = self.userSettingData['Port']['FunctionMask']["TELEMETRY_LTM"]
                elif telemetryIndex == self.userSettingData['Port']['Telemetry'].index("SmartPort"):
                    self.userSettingData['Port'][str(i)][0] = self.userSettingData['Port']['FunctionMask']["TELEMETRY_SMARTPORT"]
                elif telemetryIndex == self.userSettingData['Port']['Telemetry'].index("MAVLink"):
                    self.userSettingData['Port'][str(i)][0] = self.userSettingData['Port']['FunctionMask']["TELEMETRY_MAVLINK"]
                elif telemetryIndex == self.userSettingData['Port']['Telemetry'].index("IBUS"):
                    self.userSettingData['Port'][str(i)][0] = self.userSettingData['Port']['FunctionMask']["TELEMETRY_IBUS"]
                elif telemetryIndex == self.userSettingData['Port']['Telemetry'].index("Disabled"):
                    pass

            # Telemetry Baudrate index
            self.userSettingData['Port'][str(i)][3] = self.telemetryBaudrateComboBox[i].currentIndex()

            # RX
            if self.rxSwitchValue[i] == True:
                self.userSettingData['Port'][str(i)][0] = 64
            elif self.rxSwitchValue[i] == False:
                pass

            # Sensor
            if self.userSettingData['Port'][str(i)][0] == 0:
                if self.sensorTypeComboBox[i].currentIndex() == self.userSettingData['Port']['Sensor'].index("GPS"):
                    self.userSettingData['Port'][str(i)][0] = self.userSettingData['Port']['FunctionMask']["GPS"]
                elif self.sensorTypeComboBox[i].currentIndex() != self.userSettingData['Port']['Sensor'].index("Disabled"):
                    pass
            self.userSettingData['Port'][str(i)][2] = self.sensorBaudrateComboBox[i].currentIndex()

            # Peripherals
            if self.userSettingData['Port'][str(i)][0] == 0:
                peripheralIndex = self.peripheralsTypeComboBox[i].currentIndex()
                if peripheralIndex == self.userSettingData['Port']['Peripherals'].index("Blackbox"):
                    self.userSettingData['Port'][str(i)][0] = self.userSettingData['Port']['FunctionMask']["BLACKBOX"]
                elif peripheralIndex == self.userSettingData['Port']['Peripherals'].index("RunCam Device"):
                    self.userSettingData['Port'][str(i)][0] = self.userSettingData['Port']['FunctionMask']["RCDEVICE"]
                elif peripheralIndex == self.userSettingData['Port']['Peripherals'].index("TBS SmartAudio"):
                    self.userSettingData['Port'][str(i)][0] = self.userSettingData['Port']['FunctionMask']["VTX_SMARTAUDIO"]
                elif peripheralIndex == self.userSettingData['Port']['Peripherals'].index("IRC Tramp"):
                    self.userSettingData['Port'][str(i)][0] = self.userSettingData['Port']['FunctionMask']["VTX_TRAMP"]
                elif peripheralIndex == self.userSettingData['Port']['Peripherals'].index("Disabled"):
                    pass
            self.userSettingData['Port'][str(i)][4] = self.peripheralsBaudrateComboBox[i].currentIndex()
        # End of for loop, for 3 ports.

        # Mixer
        self.userSettingData['Mixer']['Mixer'] = self.mixerComboBox.currentIndex()

        # Sensors
        self.userSettingData['Sensors']['Accelerometer'] = self.sensorSettings['Accelerometer'].currentIndex()
        self.userSettingData['Sensors']['Magnetometer'] = self.sensorSettings['Magnetometer'].currentIndex()
        self.userSettingData['Sensors']['Barometer'] = self.sensorSettings['Barometer'].currentIndex()
        self.userSettingData['Sensors']['Pitot tube'] = self.sensorSettings['Pitot tube'].currentIndex()
        self.userSettingData['Sensors']['Rangefinder'] = self.sensorSettings['Rangefinder'].currentIndex()

        # Board and Sensor Alignment
        self.userSettingData['Board and Sensor Alignment']['Roll degrees'] = self.boardAlignmentSettings['Roll degrees'].value()
        self.userSettingData['Board and Sensor Alignment']['Pitch degrees'] = self.boardAlignmentSettings['Pitch degrees'].value()
        self.userSettingData['Board and Sensor Alignment']['Yaw degrees'] = self.boardAlignmentSettings['Yaw degrees'].value()
        self.userSettingData['Board and Sensor Alignment']['Gyro alignment'] = self.boardAlignmentSettings['Gyro Alignment'].currentIndex()
        self.userSettingData['Board and Sensor Alignment']['Acc alignment'] = self.boardAlignmentSettings['Acc Alignment'].currentIndex()
        self.userSettingData['Board and Sensor Alignment']['Mag alignment'] = self.boardAlignmentSettings['Mag Alignment'].currentIndex()

        # Receiver Mode
        self.userSettingData['Receiver Mode']['Receiver Mode'] = self.receiverSettings['Receiver Mode'].currentIndex()

        # GPS
        if self.gpsSettings['GPS for navigation and telemetry switch'] == True:
            self.userSettingData['GPS']['GPS for navigation and telemetry'] = True
        elif self.gpsSettings['GPS for navigation and telemetry switch'] == False:
            self.userSettingData['GPS']['GPS for navigation and telemetry'] = False
        self.userSettingData['GPS']['Protocol'] = self.gpsSettings['Protocol'].currentIndex()
        self.userSettingData['GPS']['Ground Assistance Type'] = self.gpsSettings['Ground Assistance Type'].currentIndex()
        self.userSettingData['GPS']['Magnetometer Declination'] = self.gpsSettings['Magnetometer Declination'].value()
        # 3D
        self.userSettingData['3D']['3D Deadband Low'] = self.threeDSettings['3D Deadband Low'].value()
        self.userSettingData['3D']['3D Deadband High'] = self.threeDSettings['3D Deadband High'].value()
        self.userSettingData['3D']['3D Neutral'] = self.threeDSettings['3D Neutral'].value()

        # Personalization
        self.userSettingData['Personalization']['Craft Name'] = self.craftNameLineEdit.text()
        # ESC/Motor Features
        if self.escmotorSettings['Enable motor and servo output switch'] == True:
            self.userSettingData['ESC/Motor Features']['Enable motor and servo output'] = True
        elif self.escmotorSettings['Enable motor and servo output switch'] == False:
            self.userSettingData['ESC/Motor Features']['Enable motor and servo output'] = False
        self.userSettingData['ESC/Motor Features']['ESC protocol'] = self.escmotorSettings['ESC protocol'].currentIndex()
        self.userSettingData['ESC/Motor Features']['ESC refresh rate'] = self.escmotorSettings['ESC refresh rate'].currentIndex()
        self.userSettingData['ESC/Motor Features']['Servo refresh rate'] = self.escmotorSettings['Servo refresh rate'].currentIndex()
        if self.escmotorSettings['Do not spin the motors when armed switch'] == True:
            self.userSettingData['ESC/Motor Features']['Do not spin the motors when armed'] = True
        elif self.escmotorSettings['Do not spin the motors when armed switch'] == False:
            self.userSettingData['ESC/Motor Features']['Do not spin the motors when armed'] = False
        self.userSettingData['ESC/Motor Features']['Min throttle'] = self.escmotorSettings['Min throttle'].value()
        self.userSettingData['ESC/Motor Features']['Mid throttle'] = self.escmotorSettings['Mid throttle'].value()
        self.userSettingData['ESC/Motor Features']['Max throttle'] = self.escmotorSettings['Max throttle'].value()
        self.userSettingData['ESC/Motor Features']['Min command'] = self.escmotorSettings['Min command'].value()

        # System Configuration
        self.userSettingData['System Configuration']['Gyroscope LPF cutoff frequency'] = self.systemConfigureSettings['Gyroscope LFP cutoff frequency'].currentIndex()
        self.userSettingData['System Configuration']['Asynchronous mode'] = self.systemConfigureSettings['Asynchronous mode'].currentIndex()
        if self.systemConfigureSettings['Synchronize looptime with gyroscope switch'] == True:
            self.userSettingData['System Configuration']['Synchronize looptime with gyroscope'] = True
        elif self.systemConfigureSettings['Synchronize looptime with gyroscope switch'] == False:
            self.userSettingData['System Configuration']['Synchronize looptime with gyroscope'] = False
        self.userSettingData['System Configuration']['Flight controller loop time'] = self.systemConfigureSettings['Flight controller loop time'].currentIndex()

        # Battery Voltage
        if self.batteryVoltageSettings['Battery voltage monitoring switch'] == True:
            self.userSettingData['Battery Voltage']['Battery voltage monitoring'] = True
        elif self.batteryVoltageSettings['Battery voltage monitoring switch'] == False:
            self.userSettingData['Battery Voltage']['Battery voltage monitoring'] = False
        self.userSettingData['Battery Voltage']['Min cell voltage'] = self.batteryVoltageSettings['Min cell voltage'].value()
        self.userSettingData['Battery Voltage']['Max cell voltage'] = self.batteryVoltageSettings['Max cell voltage'].value()
        self.userSettingData['Battery Voltage']['Warning cell voltage'] = self.batteryVoltageSettings['Warning cell voltage'].value()
        self.userSettingData['Battery Voltage']['Voltage scale'] = self.batteryVoltageSettings['Voltage scale'].value()
        self.userSettingData['Battery Voltage']['Battery voltage'] = float(self.batteryVoltageSettings['Battery voltage'].text())
        # Current Sensor
        if self.currentSensorSettings['Battery current monitoring switch'] == True:
            self.userSettingData['Current Sensor']['Battery current monitoring'] = True
        elif self.currentSensorSettings['Battery current monitoring switch'] == False:
            self.userSettingData['Current Sensor']['Battery current monitoring'] = False
        self.userSettingData['Current Sensor']['Scale the output voltage to milliamps'] = self.currentSensorSettings['Scale the output voltage to milliamps'].value()
        self.userSettingData['Current Sensor']['Offset in millivolt steps'] = self.currentSensorSettings['Offset in millivolt steps'].value()
        self.userSettingData['Current Sensor']['Battery current'] = float(self.currentSensorSettings['Battery current'].text())
        # Battery Capacity
        self.userSettingData['Battery Capacity']['Unit'] = self.batteryCapacitySettings['Unit'].currentIndex()
        self.userSettingData['Battery Capacity']['Capacity'] = self.batteryCapacitySettings['Capacity'].value()
        self.userSettingData['Battery Capacity']['Warning capacity'] = self.batteryCapacitySettings['Warning capacity'].value()
        self.userSettingData['Battery Capacity']['Critical capacity'] = self.batteryCapacitySettings['Critical capacity'].value()
        # Failsafe settings
        self.userSettingData['Failsafe']['Min length'] = self.failsafeSettings['Min length'].value()
        self.userSettingData['Failsafe']['Max length'] = self.failsafeSettings['Max length'].value()
        if self.failsafeSettings['Failsafe Kill Switch switch'] == True:
            self.userSettingData['Failsafe']['Failsafe kill switch'] = True
        elif self.failsafeSettings['Failsafe Kill Switch switch'] == False:
            self.userSettingData['Failsafe']['Failsafe kill switch'] = False
        self.userSettingData['Failsafe']['Guard time'] = self.failsafeSettings['Guard time'].value()
        self.userSettingData['Failsafe']['Failsafe throttle low delay'] = self.failsafeSettings['Failsafe throttle low delay'].value()
        for i in range(len(self.userSettingData['Failsafe']['Procedure Options'])):
            if self.failsafeSettings[self.userSettingData['Failsafe']['Procedure Options'][i]].isChecked():
                #if self.userSettingData['Failsafe']['Procedure Options'][i].isChecked():
                self.userSettingData['Failsafe']['Procedure'] = i
        self.userSettingData['Failsafe']['Throttle value while landing'] = self.failsafeSettings['Throttle value while landing'].value()
        self.userSettingData['Failsafe']['Delay for turning off the motors during failsafe'] = self.failsafeSettings['Delay for turning off the motors during failsafe'].value()
        # If the alternate switch is ON, then set failsafe min distance to
        #    the reading of spinbox; if it is OFF, then set failsafe min
        #    distance to 0. This is required since when setting the switch,
        #    its ON/OFF property is determined by the failsafe min distance,
        #    it min distance is 0, then set this switch to OFF, if min
        #    distance is not 0, then set this switch to ON.
        if self.failsafeSettings['Use alternate Minimum Distance failsafe procedure when close to home switch'] == True:
            self.userSettingData['Failsafe']['Use alternate min distance failsafe procedure'] = True
            self.userSettingData['Failsafe']['Failsafe min distance'] = self.failsafeSettings['Failsafe min distance'].value()
        elif self.failsafeSettings['Use alternate Minimum Distance failsafe procedure when close to home switch'] == False:
            self.userSettingData['Failsafe']['Use alternate min distance failsafe procedure'] = False
            self.userSettingData['Failsafe']['Failsafe min distance'] = 0
        self.userSettingData['Failsafe']['Failsafe min distance procedure'] = self.failsafeSettings['Failsafe min distance procedure'].currentIndex()
        # Other Features
        featureMask = self.userSettingData['Other Features']['Mask']
        # RX_PPM
        # if temp[31-0] == "1":
        #     pass
        # else:
        #     pass
        # Voltage monitoring
        if self.batteryVoltageSettings['Battery voltage monitoring switch'] == True:
            featureMask = featureMask | (1<<1)
        elif self.batteryVoltageSettings['Battery voltage monitoring switch'] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<1))
        # Profile selection by TX stick command
        if self.featureSwitchValue[14] == True:
            featureMask = featureMask | (1<<2)
        elif self.featureSwitchValue[14] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<2))
        # RX Serial
        # if temp[31-3] == "1":
        #     pass
        # else:
        #     pass
        # Motor stop
        if self.escmotorSettings['Do not spin the motors when armed switch'] == True:
            featureMask = featureMask | (1<<4)
        elif self.escmotorSettings['Do not spin the motors when armed switch'] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<4))
        # SERVO_TILT
        if self.featureSwitchValue[0] == True:
            featureMask = featureMask | (1<<5)
        elif self.featureSwitchValue[0] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<5))
        # SOFTSERIAL
        if self.featureSwitchValue[1] == True:
            featureMask = featureMask | (1<<6)
        elif self.featureSwitchValue[1] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<6))
        # GPS
        if self.gpsSettings['GPS for navigation and telemetry switch'] == True:
            featureMask = featureMask | (1<<7)
        elif self.gpsSettings['GPS for navigation and telemetry switch'] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<7))

        # if temp[31-8] == "1":
        #     pass
        # else:
        #     pass
        # if temp[31-9] == "1":
        #     pass
        # else:
        #     pass
        # Telemetry
        if self.featureSwitchValue[2] == True:
            featureMask = featureMask | (1<<10)
        elif self.featureSwitchValue[2] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<10))
        # Current meter
        if self.currentSensorSettings['Battery current monitoring switch'] == True:
            featureMask = featureMask | (1<<11)
        elif self.currentSensorSettings['Battery current monitoring switch'] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<11))
        # 3D
        if self.featureSwitchValue[3] == True:
            featureMask = featureMask | (1<<12)
        elif self.featureSwitchValue[3] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<12))
        # rx parallel pwm
        # if temp[31-13] == "1":
        #     pass
        # else:
        #     pass
        # rx msp
        # if temp[31-14] == "1":
        #     pass
        # else:
        #     pass
        # RSSI ADC
        if self.featureSwitchValue[4] == True:
            featureMask = featureMask | (1<<15)
        elif self.featureSwitchValue[4] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<15))
        # LED Strip
        if self.featureSwitchValue[5] == True:
            featureMask = featureMask | (1<<16)
        elif self.featureSwitchValue[5] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<16))
        # Dashboard
        if self.featureSwitchValue[6] == True:
            featureMask = featureMask | (1<<17)
        elif self.featureSwitchValue[6] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<17))
        # if temp[31-18] == "1":
        #     pass
        # else:
        #     pass
        # Blackbox
        if self.featureSwitchValue[7] == True:
            featureMask = featureMask | (1<<19)
        elif self.featureSwitchValue[7] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<19))
        # CHANNEL_FORWARDING
        if self.featureSwitchValue[8] == True:
            featureMask = featureMask | (1<<20)
        elif self.featureSwitchValue[8] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<20))
        # TRANSPONDER
        # if temp[31-21] == "1":
        #     pass
        # else:
        #     pass
        # AIRMODE
        if self.featureSwitchValue[12] == True:
            featureMask = featureMask | (1<<22)
        elif self.featureSwitchValue[12] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<22))
        # SUPEREXPO_RATES
        # if temp[31-23] == "1":
        #     pass
        # else:
        #     pass
        # VTX
        # if temp[31-24] == "1":
        #     pass
        # else:
        #     pass
        # RX SPI
        # if temp[31-25] == "1":
        #     pass
        # else:
        #     pass
        # SOFT SPI
        if self.featureSwitchValue[9] == True:
            featureMask = featureMask | (1<<26)
        elif self.featureSwitchValue[9] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<26))
        # PWM_SERVO_DRIVER
        if self.featureSwitchValue[10] == True:
            featureMask = featureMask | (1<<27)
        elif self.featureSwitchValue[10] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<27))
        # PWM_OUTPUT_ENABLE
        if self.escmotorSettings['Enable motor and servo output switch'] == True:
            featureMask = featureMask | (1<<28)
        elif self.escmotorSettings['Enable motor and servo output switch'] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<28))
        # OSD
        if self.featureSwitchValue[11] == True:
            featureMask = featureMask | (1<<29)
        elif self.featureSwitchValue[11] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<29))
        # fw launch
        if self.featureSwitchValue[13] == True:
            featureMask = featureMask | (1<<30)
        elif self.featureSwitchValue[13] == False:
            featureMask = featureMask & (0xFFFFFFFF ^ (1<<30))
        # Debug Trace
        # if temp[31-30] == "1":
        #     pass
        # else:
        #     pass
        self.userSettingData['Other Features']['Mask'] = featureMask

    # Transfer userSettingData to qsObj
    def setQSObj(self):
        # userSettingData->qsObj
        # Port
        self.qsObj.msp_cf_serial_config = [0, self.userSettingData['Port']["0"], 1, self.userSettingData['Port']["1"], 2, self.userSettingData['Port']["2"]]
        # Mixer
        self.qsObj.msp_mixer['mixer_mode'] = self.userSettingData['Mixer']['Mixer']

        # Sensors
        self.qsObj.msp_sensor_config['acc'] = self.userSettingData['Sensors']['Accelerometer']
        self.qsObj.msp_sensor_config['mag'] = self.userSettingData['Sensors']['Magnetometer']
        self.qsObj.msp_sensor_config['baro'] = self.userSettingData['Sensors']['Barometer']
        self.qsObj.msp_sensor_config['pitot'] = self.userSettingData['Sensors']['Pitot tube']
        self.qsObj.msp_sensor_config['rangefinder'] = self.userSettingData['Sensors']['Rangefinder']
        self.qsObj.msp_sensor_config['opflow'] = self.userSettingData['Sensors']['Optical Flow']

        # Board and sensor alignment
        self.qsObj.msp_board_alignment['roll_deci_degrees'] = self.userSettingData['Board and Sensor Alignment']['Roll degrees']
        self.qsObj.msp_board_alignment['pitch_deci_degrees'] = self.userSettingData['Board and Sensor Alignment']['Pitch degrees']
        self.qsObj.msp_board_alignment['yaw_deci_degrees'] = self.userSettingData['Board and Sensor Alignment']['Yaw degrees']
        self.qsObj.msp_sensor_alignment['gyro_align'] = self.userSettingData['Board and Sensor Alignment']['Gyro alignment']
        self.qsObj.msp_sensor_alignment['acc_align'] = self.userSettingData['Board and Sensor Alignment']['Acc alignment']
        self.qsObj.msp_sensor_alignment['mag_align'] = self.userSettingData['Board and Sensor Alignment']['Mag alignment']
        # Receiver mode
        self.qsObj.msp_rx_config['receiver_type'] = self.userSettingData['Receiver Mode']['Receiver Mode']
        # print(self.qsObj.msp_rx_config)

        # GPS
        # To qsObj msp_misc
        self.qsObj.msp_misc['gps_provider'] = self.userSettingData['GPS']['Protocol']
        self.qsObj.msp_misc['gps_sbas_mode'] = self.userSettingData['GPS']['Ground Assistance Type']
        self.qsObj.msp_misc['mag_declination'] = self.userSettingData['GPS']['Magnetometer Declination']

        # 3D
        # To qsObj msp_3d
        self.qsObj.msp_3d['deadband3d_low'] = self.userSettingData['3D']['3D Deadband Low']
        self.qsObj.msp_3d['deadband3d_high'] = self.userSettingData['3D']['3D Deadband High']
        self.qsObj.msp_3d['neutral3d'] = self.userSettingData['3D']['3D Neutral']

        # Name
        # To qsObj msp_name
        self.qsObj.msp_name = self.userSettingData['Personalization']['Craft Name']

        # ESC/Motor Features
        # To qsObj msp_advanced_config and msp_misc
        self.qsObj.msp_advanced_config['motor_pwm_protocol'] = self.userSettingData['ESC/Motor Features']['ESC protocol']
        escProtocolName = self.userSettingData['ESC/Motor Features']['ESC protocol Options'][self.userSettingData['ESC/Motor Features']['ESC protocol']]
        self.qsObj.msp_advanced_config['motor_pwm_rate'] = int(self.userSettingData['ESC/Motor Features']['ESC refresh rate Options'][escProtocolName][self.userSettingData['ESC/Motor Features']['ESC refresh rate']].replace("Hz", ""))
        # self.userSettingData['ESC/Motor Features']['ESC refresh rate'] = self.userSettingData['ESC/Motor Features']['ESC refresh rate Options'][escProtocolName].index(str(self.qsObj.msp_advanced_config['motor_pwm_rate'])+"Hz")
        # self.userSettingData['ESC/Motor Features']['Servo refresh rate'] = self.userSettingData['ESC/Motor Features']['Servo refresh rate Options'].index(str(self.qsObj.msp_advanced_config['servo_pwm_rate'])+"Hz")
        self.qsObj.msp_advanced_config['servo_pwm_rate'] = int(self.userSettingData['ESC/Motor Features']['Servo refresh rate Options'][self.userSettingData['ESC/Motor Features']['Servo refresh rate']].replace("Hz", ""))
        self.qsObj.msp_misc['min_throttle'] = self.userSettingData['ESC/Motor Features']['Min throttle']
        self.qsObj.msp_misc['mid_rc'] = self.userSettingData['ESC/Motor Features']['Mid throttle']
        self.qsObj.msp_misc['max_throttle'] = self.userSettingData['ESC/Motor Features']['Max throttle']
        self.qsObj.msp_misc['min_command'] = self.userSettingData['ESC/Motor Features']['Min command']

        # System Configuration
        # To qsObj msp_inav_pid, msp_loop_time and msp_advanced_config
        self.qsObj.msp_inav_pid['gyro_lpf'] = self.userSettingData['System Configuration']['Gyroscope LPF cutoff frequency']
        self.qsObj.msp_inav_pid['async_mode'] = self.userSettingData['System Configuration']['Asynchronous mode']
        if self.userSettingData['System Configuration']['Synchronize looptime with gyroscope'] == True:
            self.qsObj.msp_advanced_config['gyro_sync'] = 1
        elif self.userSettingData['System Configuration']['Synchronize looptime with gyroscope'] == False:
            self.qsObj.msp_advanced_config['gyro_sync'] = 0
        self.qsObj.msp_loop_time['looptime'] = self.userSettingData['System Configuration']['Flight controller loop time']

        # Battery Voltage
        # To qsObj msp_misc and msp_analog
        self.qsObj.msp_misc['voltage_cell_min'] = int(self.userSettingData['Battery Voltage']['Min cell voltage']*10)
        self.qsObj.msp_misc['voltage_cell_max'] = int(self.userSettingData['Battery Voltage']['Max cell voltage']*10)
        self.qsObj.msp_misc['voltage_cell_warning'] = int(self.userSettingData['Battery Voltage']['Warning cell voltage']*10)
        self.qsObj.msp_misc['voltage_scale'] = self.userSettingData['Battery Voltage']['Voltage scale']
        # self.qsObj.msp_analog['vbat']

        # Current Sensor
        # To qsObj
        self.qsObj.msp_current_meter_config['scale'] = self.userSettingData['Current Sensor']['Scale the output voltage to milliamps']
        self.qsObj.msp_current_meter_config['offset'] = self.userSettingData['Current Sensor']['Offset in millivolt steps']
        self.qsObj.msp_analog['amps'] = self.userSettingData['Current Sensor']['Battery current']

        # Battery Capacity
        # To qsObj
        # self.userSettingData['Battery Capacity']['Unit']
        # self.userSettingData['Battery Capacity']['Capacity']  msp_analog['powermetersum']
        # self.userSettingData['Battery Capacity']['Warning capacity']
        # self.userSettingData['Battery Capacity']['Critical capacity']

        # Failsafe
        # To qsObj msp_rx_config and msp_failsafe_config
        self.qsObj.msp_rx_config['rx_min_usec'] = self.userSettingData['Failsafe']['Min length']
        self.qsObj.msp_rx_config['rx_max_usec'] = self.userSettingData['Failsafe']['Max length']
        if self.userSettingData['Failsafe']['Failsafe kill switch'] == False:
            self.qsObj.msp_failsafe_config['failsafe_kill_switch'] = 0
        elif self.userSettingData['Failsafe']['Failsafe kill switch'] == True:
            self.qsObj.msp_failsafe_config['failsafe_kill_switch'] = 1
        self.qsObj.msp_failsafe_config['failsafe_delay'] = self.userSettingData['Failsafe']['Guard time']
        self.qsObj.msp_failsafe_config['failsafe_throttle_low_delay'] = self.userSettingData['Failsafe']['Failsafe throttle low delay']
        self.qsObj.msp_failsafe_config['failsafe_procedure'] = self.userSettingData['Failsafe']['Procedure']
        self.qsObj.msp_failsafe_config['failsafe_throttle'] = self.userSettingData['Failsafe']['Throttle value while landing']
        self.qsObj.msp_failsafe_config['failsafe_off_delay'] = self.userSettingData['Failsafe']['Delay for turning off the motors during failsafe']
        self.qsObj.msp_failsafe_config['failsafe_min_distance'] = self.userSettingData['Failsafe']['Failsafe min distance']
        self.qsObj.msp_failsafe_config['failsafe_min_distance_procedure'] = self.userSettingData['Failsafe']['Failsafe min distance procedure']

        # Other Features
        # To qsObj msp_feature
        self.qsObj.msp_feature['mask'] = self.userSettingData['Other Features']['Mask']

    def portGroupBoxInit(self):
        self.portGroupBoxLayout.addWidget(QLabel("Identifier"), 0, 0, 1, 1)

        dataLabel = QLabel("Data")
        dataLabel.setAlignment(Qt.AlignCenter)
        self.portGroupBoxLayout.addWidget(dataLabel, 0, 1, 1, 2)

        telemetryLabel = QLabel("Telemetry")
        telemetryLabel.setAlignment(Qt.AlignCenter)
        self.portGroupBoxLayout.addWidget(telemetryLabel, 0, 3, 1, 2)

        rxLabel = QLabel("RX")
        rxLabel.setAlignment(Qt.AlignCenter)
        self.portGroupBoxLayout.addWidget(rxLabel, 0, 5, 1, 1)

        sensorLabel = QLabel("Sensors")
        sensorLabel.setAlignment(Qt.AlignCenter)
        self.portGroupBoxLayout.addWidget(sensorLabel, 0, 6, 1, 2)

        peripheralLabel = QLabel("Peripherals")
        peripheralLabel.setAlignment(Qt.AlignCenter)
        self.portGroupBoxLayout.addWidget(peripheralLabel, 0, 8, 1, 2)

        portNumber = 3
        self.dataSwitchValue = [False]*portNumber
        self.dataSwitch = [None]*3
        self.dataBaudrateComboBox = [None]*3
        self.telemetryTypeComboBox = [None]*3
        self.telemetryBaudrateComboBox = [None]*3
        self.sensorTypeComboBox = [None]*3
        self.sensorBaudrateComboBox = [None]*3
        self.peripheralsTypeComboBox = [None]*3
        self.peripheralsBaudrateComboBox = [None]*3
        self.rxSwitchValue = [False]*portNumber
        self.rxSwitch = [None]*3
        for i in range(portNumber):
            # Identifier
            self.portGroupBoxLayout.addWidget(QLabel("UART"+str(i+1)), i+1, 0, 1, 1)

            # Data
            self.dataSwitchValue[i] = False
            self.dataSwitch[i] = QPushButton(QIcon(self.switchOFFImage), None, self)
            self.dataSwitch[i].setIconSize(QSize(39,18))
            self.dataSwitch[i].setStyleSheet("QPushButton {border: none;}")
            self.dataSwitch[i].clicked.connect(partial(self.dataSwitchClicked, i))
            self.portGroupBoxLayout.addWidget(self.dataSwitch[i], i+1, 1, 1, 1)
            self.dataBaudrateComboBox[i] = QComboBox(self)
            self.portGroupBoxLayout.addWidget(self.dataBaudrateComboBox[i], i+1, 2, 1, 1)

            # Telemetry
            self.telemetryTypeComboBox[i] = QComboBox(self)
            self.portGroupBoxLayout.addWidget(self.telemetryTypeComboBox[i], i+1, 3, 1, 1)
            self.telemetryBaudrateComboBox[i] = QComboBox(self)
            self.portGroupBoxLayout.addWidget(self.telemetryBaudrateComboBox[i], i+1, 4, 1, 1)

            # RX
            self.rxSwitchValue[i] = False
            self.rxSwitch[i] = QPushButton(QIcon(self.switchOFFImage), None, self)
            self.rxSwitch[i].setIconSize(QSize(39,18))
            self.rxSwitch[i].setStyleSheet("QPushButton {border: none;}")
            self.rxSwitch[i].clicked.connect(partial(self.rxSwitchClicked, i))
            self.portGroupBoxLayout.addWidget(self.rxSwitch[i], i+1, 5, 1, 1)

            # Sensor
            self.sensorTypeComboBox[i] = QComboBox(self)
            self.portGroupBoxLayout.addWidget(self.sensorTypeComboBox[i], i+1, 6, 1, 1)
            self.sensorBaudrateComboBox[i] = QComboBox(self)
            self.portGroupBoxLayout.addWidget(self.sensorBaudrateComboBox[i], i+1, 7, 1, 1)

            # Peripherals
            self.peripheralsTypeComboBox[i] = QComboBox(self)
            self.portGroupBoxLayout.addWidget(self.peripheralsTypeComboBox[i], i+1, 8, 1, 1)
            self.peripheralsBaudrateComboBox[i] = QComboBox(self)
            self.portGroupBoxLayout.addWidget(self.peripheralsBaudrateComboBox[i], i+1, 9, 1, 1)

    def dataSwitchClicked(self, index):
        if self.dataSwitchValue[index] == False:
            self.dataSwitch[index].setIcon(QIcon(self.switchONImage))
            self.dataSwitchValue[index] = True
        elif self.dataSwitchValue[index] == True:
            self.dataSwitch[index].setIcon(QIcon(self.switchOFFImage))
            self.dataSwitchValue[index] = False

    def rxSwitchClicked(self, index):
        if self.rxSwitchValue[index] == False:
            self.rxSwitch[index].setIcon(QIcon(self.switchONImage))
            self.rxSwitchValue[index] = True
        elif self.rxSwitchValue[index] == True:
            self.rxSwitch[index].setIcon(QIcon(self.switchOFFImage))
            self.rxSwitchValue[index] = False

    def mixerGroupBoxInit(self):
        self.mixerComboBox = QComboBox(self)
        self.mixerComboBox.setStyleSheet("QComboBox {max-width:180}")
        self.mixerGroupBoxLayout.addWidget(self.mixerComboBox)

    def sensorGroupBoxInit(self):
        self.sensorSettings = {}
        self.sensorSettings['Accelerometer'] = QComboBox(self)
        self.sensorGroupBoxLayout.addWidget(self.sensorSettings['Accelerometer'], 0, 0, 1, 1)
        self.sensorGroupBoxLayout.addWidget(QLabel("Accelerometer"), 0, 1, 1, 1)

        self.sensorSettings['Magnetometer'] = QComboBox(self)
        self.sensorGroupBoxLayout.addWidget(self.sensorSettings['Magnetometer'], 1, 0, 1, 1)
        self.sensorGroupBoxLayout.addWidget(QLabel("Magnetometer"), 1, 1, 1, 1)

        self.sensorSettings['Barometer'] = QComboBox(self)
        self.sensorGroupBoxLayout.addWidget(self.sensorSettings['Barometer'], 2, 0, 1, 1)
        self.sensorGroupBoxLayout.addWidget(QLabel("Barometer"), 2, 1, 1, 1)

        self.sensorSettings['Pitot tube'] = QComboBox(self)
        self.sensorGroupBoxLayout.addWidget(self.sensorSettings['Pitot tube'], 3, 0, 1, 1)
        self.sensorGroupBoxLayout.addWidget(QLabel("Pitot tube"), 3, 1, 1, 1)

        self.sensorSettings['Rangefinder'] = QComboBox(self)
        self.sensorGroupBoxLayout.addWidget(self.sensorSettings['Rangefinder'], 4, 0, 1, 1)
        self.sensorGroupBoxLayout.addWidget(QLabel("Rangefinder"), 4, 1, 1, 1)

    def boardAlignmentGroupBoxInit(self):
        self.boardAlignmentSettings = {}
        self.boardAlignmentGroupBoxLayout.addWidget(QLabel("Roll Degrees"), 0, 0, 1, 1)
        self.boardAlignmentGroupBoxLayout.addWidget(QLabel("Pitch Degrees"), 1, 0, 1, 1)
        self.boardAlignmentGroupBoxLayout.addWidget(QLabel("Yaw Degrees"), 2, 0, 1, 1)

        self.boardAlignmentSettings['Roll degrees'] = QDoubleSpinBox(self)
        self.boardAlignmentSettings['Roll degrees'].setDecimals(1)
        self.boardAlignmentSettings['Roll degrees'].setStyleSheet("QSpinBox {max-width:40}")
        self.boardAlignmentGroupBoxLayout.addWidget(self.boardAlignmentSettings['Roll degrees'], 0, 1, 1, 1)

        self.boardAlignmentSettings['Pitch degrees'] = QDoubleSpinBox(self)
        self.boardAlignmentSettings['Pitch degrees'].setDecimals(1)
        self.boardAlignmentSettings['Pitch degrees'].setStyleSheet("QSpinBox {max-width:40}")
        self.boardAlignmentGroupBoxLayout.addWidget(self.boardAlignmentSettings['Pitch degrees'], 1, 1, 1, 1)

        self.boardAlignmentSettings['Yaw degrees'] = QDoubleSpinBox(self)
        self.boardAlignmentSettings['Yaw degrees'].setDecimals(1)
        self.boardAlignmentSettings['Yaw degrees'].setStyleSheet("QSpinBox {max-width:40}")
        self.boardAlignmentGroupBoxLayout.addWidget(self.boardAlignmentSettings['Yaw degrees'], 2, 1, 1, 1)

        self.boardAlignmentGroupBoxLayout.addWidget(QLabel("Gyro Alignment"), 3, 0, 1, 1)
        self.boardAlignmentSettings['Gyro Alignment'] = QComboBox(self)
        self.boardAlignmentGroupBoxLayout.addWidget(self.boardAlignmentSettings['Gyro Alignment'], 3, 1, 1, 1)

        self.boardAlignmentGroupBoxLayout.addWidget(QLabel("Acc Alignment"), 4, 0, 1, 1)
        self.boardAlignmentSettings['Acc Alignment'] = QComboBox(self)
        self.boardAlignmentGroupBoxLayout.addWidget(self.boardAlignmentSettings['Acc Alignment'], 4, 1, 1, 1)

        self.boardAlignmentGroupBoxLayout.addWidget(QLabel("Mag Alignment"), 5, 0, 1, 1)
        self.boardAlignmentSettings['Mag Alignment'] = QComboBox(self)
        self.boardAlignmentGroupBoxLayout.addWidget(self.boardAlignmentSettings['Mag Alignment'], 5, 1, 1, 1)

    def receiverGroupBoxInit(self):
        self.receiverSettings = {}
        self.receiverSettings['Receiver Mode'] = QComboBox(self)
        self.receiverGroupBoxLayout.addWidget(self.receiverSettings['Receiver Mode'])

    def gpsGroupBoxInit(self):
        self.gpsSettings = {}
        self.gpsSettings['GPS for navigation and telemetry'] = QPushButton(QIcon(self.switchOFFImage), None, self)
        self.gpsSettings['GPS for navigation and telemetry'].setIconSize(QSize(39,18))
        self.gpsSettings['GPS for navigation and telemetry'].setStyleSheet("QPushButton {border: none;}")
        self.gpsSettings['GPS for navigation and telemetry switch'] = False
        self.gpsSettings['GPS for navigation and telemetry'].clicked.connect(self.useGPSNavTelSwitchClicked)
        self.gpsGroupBoxLayout.addWidget(self.gpsSettings['GPS for navigation and telemetry'], 0, 0, 1, 1)
        self.gpsGroupBoxLayout.addWidget(QLabel("GPS for navigation \nand telemetry"), 0, 1, 1, 1)

        self.gpsSettings['Protocol'] = QComboBox(self)
        self.gpsSettings['Protocol'].setStyleSheet("QComboBox {max-width:90}")
        self.gpsGroupBoxLayout.addWidget(self.gpsSettings['Protocol'], 1, 0, 1, 1)
        self.gpsGroupBoxLayout.addWidget(QLabel("Protocol"), 1, 1, 1, 1)

        self.gpsSettings['Ground Assistance Type'] = QComboBox(self)
        self.gpsSettings['Ground Assistance Type'].setStyleSheet("QComboBox {max-width:90}")
        self.gpsGroupBoxLayout.addWidget(self.gpsSettings['Ground Assistance Type'], 2, 0, 1, 1)
        self.gpsGroupBoxLayout.addWidget(QLabel("Ground Assistance Type"), 2, 1, 1, 1)

        self.gpsSettings['Magnetometer Declination'] = QDoubleSpinBox(self)
        self.gpsSettings['Magnetometer Declination'].setDecimals(1)
        self.gpsGroupBoxLayout.addWidget(self.gpsSettings['Magnetometer Declination'], 3, 0, 1, 1)
        self.gpsGroupBoxLayout.addWidget(QLabel("Magnetometer \nDeclination [deg]"), 3, 1, 1, 1)

    def threeDGroupBoxInit(self):
        self.threeDSettings = {}
        self.threeDSettings['3D Deadband Low'] = QSpinBox(self)
        self.threeDSettings['3D Deadband Low'].setRange(1000,2000)
        self.threeDGroupBoxLayout.addWidget(self.threeDSettings['3D Deadband Low'], 0, 0, 1, 1)
        self.threeDGroupBoxLayout.addWidget(QLabel("3D Deadband Low"), 0, 1, 1, 1)
        self.threeDSettings['3D Deadband High'] = QSpinBox(self)
        self.threeDSettings['3D Deadband High'].setRange(1000,2000)
        self.threeDGroupBoxLayout.addWidget(self.threeDSettings['3D Deadband High'], 1, 0, 1, 1)
        self.threeDGroupBoxLayout.addWidget(QLabel("3D Deadband High"), 1, 1, 1, 1)
        self.threeDSettings['3D Neutral'] = QSpinBox(self)
        self.threeDSettings['3D Neutral'].setRange(1000,2000)
        self.threeDGroupBoxLayout.addWidget(self.threeDSettings['3D Neutral'], 2, 0, 1, 1)
        self.threeDGroupBoxLayout.addWidget(QLabel("3D Neutral"), 2, 1, 1, 1)

    def nameGroupBoxInit(self):
        self.craftNameLineEdit = QLineEdit(self)
        self.craftNameLineEdit.setStyleSheet("QLineEdit {max-width:180}")
        self.nameGroupBoxLayout.addWidget(self.craftNameLineEdit, 0, 0, 1, 1)
        self.nameGroupBoxLayout.addWidget(QLabel("Craft Name"), 0, 1, 1, 1)

    def otherFeatureGroupBoxInit(self):
        featureList = ["Servo gimbal",
                       "Enable CPU based serial ports",
                       "Telemetry output",
                       "3D mode (for use with reversible ESCs)",
                       "Analog RSSI input",
                       "Multi-color RGB LED strip support",
                       "OLED Screen Display",
                       "Blackbox flight data recorder",
                       "Forward aux channels to servo outputs",
                       "CPU based SPI",
                       "External PWM servo driver",
                       "OSD",
                       "Permanently enable AIRMODE",
                       "Permanently enable Launch Mode for Fixed Wing",
                       "Profile selection with TX stick command"]
        self.featureSwitchValue = [False]*len(featureList)
        self.featureSwitch = [None]*len(featureList)
        for i in range(len(featureList)):
            self.featureSwitchValue[i] = False
            self.featureSwitch[i] = QPushButton(QIcon(self.switchOFFImage), None, self)
            self.featureSwitch[i].setIconSize(QSize(39,18))
            self.featureSwitch[i].setStyleSheet("QPushButton {border: none;}")
            self.featureSwitch[i].clicked.connect(partial(self.featureSwitchClicked, i))
            self.otherFeatureGroupBoxLayout.addWidget(self.featureSwitch[i], i, 0, 1, 1)
            self.otherFeatureGroupBoxLayout.addWidget(QLabel(featureList[i]), i, 1, 1, 2)

    def escmotorGroupBoxInit(self):
        self.escmotorSettings = {}
        self.escmotorSettings['Enable motor and servo output'] = QPushButton(QIcon(self.switchOFFImage), None, self)
        self.escmotorSettings['Enable motor and servo output switch'] = False
        self.escmotorSettings['Enable motor and servo output'].setIconSize(QSize(39,18))
        self.escmotorSettings['Enable motor and servo output'].setStyleSheet("QPushButton {border: none;}")
        self.escmotorSettings['Enable motor and servo output'].clicked.connect(self.motorServoOutputSwitchClicked)
        self.escmotorGroupBoxLayout.addWidget(self.escmotorSettings['Enable motor and servo output'], 0, 0, 1, 1)
        self.escmotorGroupBoxLayout.addWidget(QLabel("Enable motor and servo output"), 0, 1, 1, 1)

        self.escmotorSettings['ESC protocol'] = QComboBox()
        self.escmotorGroupBoxLayout.addWidget(self.escmotorSettings['ESC protocol'], 1, 0, 1, 1)
        self.escmotorGroupBoxLayout.addWidget(QLabel("ESC protocol"), 1, 1, 1, 1)

        self.escmotorSettings['ESC refresh rate'] = QComboBox()
        self.escmotorGroupBoxLayout.addWidget(self.escmotorSettings['ESC refresh rate'], 2, 0, 1, 1)
        self.escmotorGroupBoxLayout.addWidget(QLabel("ESC refresh rate"), 2, 1, 1, 1)

        self.escmotorSettings['Servo refresh rate'] = QComboBox()
        self.escmotorGroupBoxLayout.addWidget(self.escmotorSettings['Servo refresh rate'], 3, 0, 1, 1)
        self.escmotorGroupBoxLayout.addWidget(QLabel("Servo refresh rate"), 3, 1, 1, 1)

        self.escmotorSettings['Do not spin the motors when armed'] = QPushButton(QIcon(self.switchOFFImage), None, self)
        self.escmotorSettings['Do not spin the motors when armed switch'] = False
        self.escmotorSettings['Do not spin the motors when armed'].setIconSize(QSize(39,18))
        self.escmotorSettings['Do not spin the motors when armed'].setStyleSheet("QPushButton {border: none;}")
        self.escmotorSettings['Do not spin the motors when armed'].clicked.connect(self.donotSpinMotorWhenArmedSwitchClicked)
        self.escmotorGroupBoxLayout.addWidget(self.escmotorSettings['Do not spin the motors when armed'], 4, 0, 1, 1)
        self.escmotorGroupBoxLayout.addWidget(QLabel("Don't spin the motors when armed"), 4, 1, 1, 1)

        self.escmotorSettings['Min throttle'] = QSpinBox()
        self.escmotorSettings['Min throttle'].setRange(900, 2100)
        self.escmotorGroupBoxLayout.addWidget(self.escmotorSettings['Min throttle'], 5, 0, 1, 1)
        self.escmotorGroupBoxLayout.addWidget(QLabel("Min throttle"), 5, 1, 1, 1)

        self.escmotorSettings['Mid throttle'] = QSpinBox()
        self.escmotorSettings['Mid throttle'].setRange(900, 2100)
        self.escmotorGroupBoxLayout.addWidget(self.escmotorSettings['Mid throttle'], 6, 0, 1, 1)
        self.escmotorGroupBoxLayout.addWidget(QLabel("Mid throttle (RC inputs center value)"), 6, 1, 1, 1)

        self.escmotorSettings['Max throttle'] = QSpinBox()
        self.escmotorSettings['Max throttle'].setRange(900, 2100)
        self.escmotorGroupBoxLayout.addWidget(self.escmotorSettings['Max throttle'], 7, 0, 1, 1)
        self.escmotorGroupBoxLayout.addWidget(QLabel("Max throttle"), 7, 1, 1, 1)

        self.escmotorSettings['Min command'] = QSpinBox()
        self.escmotorSettings['Min command'].setRange(900, 1200)
        self.escmotorGroupBoxLayout.addWidget(self.escmotorSettings['Min command'], 8, 0, 1, 1)
        self.escmotorGroupBoxLayout.addWidget(QLabel("Min command"), 8, 1, 1, 1)

    def systemConfigureGroupBoxInit(self):
        self.systemConfigureSettings = {}
        self.systemConfigureSettings['Gyroscope LFP cutoff frequency'] = QComboBox()
        self.systemConfigureGroupBoxLayout.addWidget(self.systemConfigureSettings['Gyroscope LFP cutoff frequency'], 0, 0, 1, 1)
        self.systemConfigureGroupBoxLayout.addWidget(QLabel("Gyroscope LFP cutoff frequency"), 0, 1, 1, 1)

        self.systemConfigureSettings['Asynchronous mode'] = QComboBox()
        self.systemConfigureGroupBoxLayout.addWidget(self.systemConfigureSettings['Asynchronous mode'], 1, 0, 1, 1)
        self.systemConfigureGroupBoxLayout.addWidget(QLabel("Asynchronous mode"), 1, 1, 1, 1)

        self.systemConfigureSettings['Synchronize looptime with gyroscope'] = QPushButton(QIcon(self.switchOFFImage), None, self)
        self.systemConfigureSettings['Synchronize looptime with gyroscope switch'] = False
        self.systemConfigureSettings['Synchronize looptime with gyroscope'].setIconSize(QSize(39,18))
        self.systemConfigureSettings['Synchronize looptime with gyroscope'].setStyleSheet("QPushButton {border: none;}")
        self.systemConfigureSettings['Synchronize looptime with gyroscope'].clicked.connect(self.synchronizeLooptimeWithGyroSwitchClicked)
        self.systemConfigureGroupBoxLayout.addWidget(self.systemConfigureSettings['Synchronize looptime with gyroscope'], 2, 0, 1, 1)
        self.systemConfigureGroupBoxLayout.addWidget(QLabel("Synchronize looptime with gyroscope"), 2, 1, 1, 1)

        self.systemConfigureSettings['Flight controller loop time'] = QComboBox()
        self.systemConfigureGroupBoxLayout.addWidget(self.systemConfigureSettings['Flight controller loop time'], 3, 0, 1, 1)
        self.systemConfigureGroupBoxLayout.addWidget(QLabel("Flight controller loop time"), 3, 1, 1, 1)

    def batteryVoltageGroupBoxInit(self):
        self.batteryVoltageSettings = {}
        self.batteryVoltageSettings['Battery voltage monitoring'] = QPushButton(QIcon(self.switchOFFImage), None, self)
        self.batteryVoltageSettings['Battery voltage monitoring switch'] = False
        self.batteryVoltageSettings['Battery voltage monitoring'].setIconSize(QSize(39,18))
        self.batteryVoltageSettings['Battery voltage monitoring'].setStyleSheet("QPushButton {border: none;}")
        self.batteryVoltageSettings['Battery voltage monitoring'].clicked.connect(self.batteryVoltageMonitorSwitchClicked)
        self.batteryVoltageGroupBoxLayout.addWidget(self.batteryVoltageSettings['Battery voltage monitoring'], 0, 0, 1, 1)
        self.batteryVoltageGroupBoxLayout.addWidget(QLabel("Battery voltage monitoring"), 0, 1, 1, 1)

        self.batteryVoltageSettings['Min cell voltage'] = QDoubleSpinBox()
        self.batteryVoltageSettings['Min cell voltage'].setDecimals(1)
        self.batteryVoltageGroupBoxLayout.addWidget(self.batteryVoltageSettings['Min cell voltage'], 1, 0, 1, 1)
        self.batteryVoltageGroupBoxLayout.addWidget(QLabel("Min cell voltage"), 1, 1, 1, 1)

        self.batteryVoltageSettings['Max cell voltage'] = QDoubleSpinBox()
        self.batteryVoltageSettings['Max cell voltage'].setDecimals(1)
        self.batteryVoltageGroupBoxLayout.addWidget(self.batteryVoltageSettings['Max cell voltage'], 2, 0, 1, 1)
        self.batteryVoltageGroupBoxLayout.addWidget(QLabel("Max cell voltage"), 2, 1, 1, 1)

        self.batteryVoltageSettings['Warning cell voltage'] = QDoubleSpinBox()
        self.batteryVoltageSettings['Warning cell voltage'].setDecimals(1)
        self.batteryVoltageGroupBoxLayout.addWidget(self.batteryVoltageSettings['Warning cell voltage'], 3, 0, 1, 1)
        self.batteryVoltageGroupBoxLayout.addWidget(QLabel("Warning cell voltage"), 3, 1, 1, 1)

        self.batteryVoltageSettings['Voltage scale'] = QSpinBox()
        self.batteryVoltageSettings['Voltage scale'].setRange(0, 200)
        self.batteryVoltageGroupBoxLayout.addWidget(self.batteryVoltageSettings['Voltage scale'], 4, 0, 1, 1)
        self.batteryVoltageGroupBoxLayout.addWidget(QLabel("Voltage scale"), 4, 1, 1, 1)

        self.batteryVoltageSettings['Battery voltage'] = QLineEdit()
        self.batteryVoltageGroupBoxLayout.addWidget(self.batteryVoltageSettings['Battery voltage'], 5, 0, 1, 1)
        self.batteryVoltageGroupBoxLayout.addWidget(QLabel("Battery voltage"), 5, 1, 1, 1)

    def currentSensorGroupBoxInit(self):
        self.currentSensorSettings = {}
        self.currentSensorSettings['Battery current monitoring'] = QPushButton(QIcon(self.switchOFFImage), None, self)
        self.currentSensorSettings['Battery current monitoring switch'] = False
        self.currentSensorSettings['Battery current monitoring'].setIconSize(QSize(39,18))
        self.currentSensorSettings['Battery current monitoring'].setStyleSheet("QPushButton {border: none;}")
        self.currentSensorSettings['Battery current monitoring'].clicked.connect(self.batteryCurrentMonitorSwitchClicked)
        self.currentSensorGroupBoxLayout.addWidget(self.currentSensorSettings['Battery current monitoring'], 0, 0, 1, 1)
        self.currentSensorGroupBoxLayout.addWidget(QLabel("Battery current monitoring"), 0, 1, 1, 1)

        self.currentSensorSettings['Scale the output voltage to milliamps'] = QSpinBox()
        self.currentSensorSettings['Scale the output voltage to milliamps'].setRange(0, 1000)
        self.currentSensorGroupBoxLayout.addWidget(self.currentSensorSettings['Scale the output voltage to milliamps'], 1, 0, 1, 1)
        self.currentSensorGroupBoxLayout.addWidget(QLabel("Scale the output voltage to milliamps"), 1, 1, 1, 1)

        self.currentSensorSettings['Offset in millivolt steps'] = QSpinBox()
        self.currentSensorGroupBoxLayout.addWidget(self.currentSensorSettings['Offset in millivolt steps'], 2, 0, 1, 1)
        self.currentSensorGroupBoxLayout.addWidget(QLabel("Offset in millivolt steps"), 2, 1, 1, 1)

        self.currentSensorSettings['Battery current'] = QLineEdit()
        self.currentSensorGroupBoxLayout.addWidget(self.currentSensorSettings['Battery current'], 3, 0, 1, 1)
        self.currentSensorGroupBoxLayout.addWidget(QLabel("Battery current"), 3, 1, 1, 1)

    def batteryCapacityGroupBoxInit(self):
        self.batteryCapacitySettings = {}
        self.batteryCapacitySettings['Unit'] = QComboBox()
        self.batteryCapacityGroupBoxLayout.addWidget(self.batteryCapacitySettings['Unit'], 0, 0, 1, 1)
        self.batteryCapacityGroupBoxLayout.addWidget(QLabel("Unit"), 0, 1, 1, 1)

        self.batteryCapacitySettings['Capacity'] = QSpinBox()
        self.batteryCapacityGroupBoxLayout.addWidget(self.batteryCapacitySettings['Capacity'], 1, 0, 1, 1)
        self.batteryCapacityGroupBoxLayout.addWidget(QLabel("Capacity"), 1, 1, 1, 1)

        self.batteryCapacitySettings['Warning capacity'] = QSpinBox()
        self.batteryCapacityGroupBoxLayout.addWidget(self.batteryCapacitySettings['Warning capacity'], 2, 0, 1, 1)
        self.batteryCapacityGroupBoxLayout.addWidget(QLabel("Warning Capacity (%)"), 2, 1, 1, 1)

        self.batteryCapacitySettings['Critical capacity'] = QSpinBox()
        self.batteryCapacityGroupBoxLayout.addWidget(self.batteryCapacitySettings['Critical capacity'], 3, 0, 1, 1)
        self.batteryCapacityGroupBoxLayout.addWidget(QLabel("Critical Capacity (%)"), 3, 1, 1, 1)

    def failsafeSettingGroupBoxInit(self):
        self.failsafeSettings = {}
        self.failsafeSettingGroupBoxLayout.addWidget(QLabel("Valid Pulse Range Settings"), 0, 0, 1, 2)

        self.failsafeSettings['Min length'] = QSpinBox()
        self.failsafeSettings['Min length'].setRange(800, 2200)
        self.failsafeSettingGroupBoxLayout.addWidget(self.failsafeSettings['Min length'], 1, 0, 1, 1)
        self.failsafeSettingGroupBoxLayout.addWidget(QLabel("Min Length"), 1, 1, 1, 1)

        self.failsafeSettings['Max length'] = QSpinBox()
        self.failsafeSettings['Max length'].setRange(800, 2200)
        self.failsafeSettingGroupBoxLayout.addWidget(self.failsafeSettings['Max length'], 2, 0, 1, 1)
        self.failsafeSettingGroupBoxLayout.addWidget(QLabel("Max Length"), 2, 1, 1, 1)

        self.failsafeSettingGroupBoxLayout.addWidget(QLabel("Setting"), 3, 0, 1, 1)

        self.failsafeSettings['Failsafe Kill Switch'] = QPushButton(QIcon(self.switchOFFImage), None, self)
        self.failsafeSettings['Failsafe Kill Switch'].setIconSize(QSize(39,18))
        self.failsafeSettings['Failsafe Kill Switch'].setStyleSheet("QPushButton {border: none;}")
        self.failsafeSettings['Failsafe Kill Switch switch'] = False
        self.failsafeSettings['Failsafe Kill Switch'].clicked.connect(self.failsafeKillSwitchClicked)
        self.failsafeSettingGroupBoxLayout.addWidget(self.failsafeSettings['Failsafe Kill Switch'], 4, 0, 1, 1)
        self.failsafeSettingGroupBoxLayout.addWidget(QLabel("Failsafe Kill Switch"), 4, 1, 1, 1)

        self.failsafeSettings['Guard time'] = QSpinBox()
        self.failsafeSettings['Guard time'].setRange(0, 100)
        self.failsafeSettingGroupBoxLayout.addWidget(self.failsafeSettings['Guard time'], 5, 0, 1, 1)
        self.failsafeSettingGroupBoxLayout.addWidget(QLabel("Guard Time"), 5, 1, 1, 1)

        self.failsafeSettings['Failsafe throttle low delay'] = QSpinBox()
        self.failsafeSettings['Failsafe throttle low delay'].setRange(0, 1000)
        self.failsafeSettingGroupBoxLayout.addWidget(self.failsafeSettings['Failsafe throttle low delay'], 6, 0, 1, 1)
        self.failsafeSettingGroupBoxLayout.addWidget(QLabel("Failsafe Throttle Low Delay"), 6, 1, 1, 1)

        self.failsafeSettingGroupBoxLayout.addWidget(QLabel("Procedure"), 7, 0, 1, 2)

        self.failsafeSettings['Drop'] = QRadioButton()
        self.failsafeSettingGroupBoxLayout.addWidget(self.failsafeSettings['Drop'], 8, 0, 1, 1)
        self.failsafeSettingGroupBoxLayout.addWidget(QLabel("Drop"), 8, 1, 1, 1)

        self.failsafeSettings['Land'] = QRadioButton()
        self.failsafeSettingGroupBoxLayout.addWidget(self.failsafeSettings['Land'], 9, 0, 1, 1)
        self.failsafeSettingGroupBoxLayout.addWidget(QLabel("Land"), 9, 1, 1, 1)

        self.failsafeSettings['Throttle value while landing'] = QSpinBox()
        self.failsafeSettings['Throttle value while landing'].setRange(1000, 2000)
        self.failsafeSettingGroupBoxLayout.addWidget(self.failsafeSettings['Throttle value while landing'], 10, 0, 1, 1)
        self.failsafeSettingGroupBoxLayout.addWidget(QLabel("Throttle value while landing"), 10, 1, 1, 1)

        self.failsafeSettings['Delay for turning off the motors during failsafe'] = QSpinBox()
        self.failsafeSettings['Delay for turning off the motors during failsafe'].setRange(0, 500)
        self.failsafeSettingGroupBoxLayout.addWidget(self.failsafeSettings['Delay for turning off the motors during failsafe'], 11, 0, 1, 1)
        self.failsafeSettingGroupBoxLayout.addWidget(QLabel("Delay for turning off the motors \nduring Failsafe"), 11, 1, 1, 1)

        self.failsafeSettings['RTH'] = QRadioButton()
        self.failsafeSettingGroupBoxLayout.addWidget(self.failsafeSettings['RTH'], 12, 0, 1, 1)
        self.failsafeSettingGroupBoxLayout.addWidget(QLabel("RTH"), 12, 1, 1, 1)

        self.failsafeSettings['Do nothing'] = QRadioButton()
        self.failsafeSettingGroupBoxLayout.addWidget(self.failsafeSettings['Do nothing'], 13, 0, 1, 1)
        self.failsafeSettingGroupBoxLayout.addWidget(QLabel("Do nothing"), 13, 1, 1, 1)

        self.failsafeSettings['Use alternate Minimum Distance failsafe procedure when close to home'] = QPushButton(QIcon(self.switchOFFImage), None, self)
        self.failsafeSettings['Use alternate Minimum Distance failsafe procedure when close to home'].setIconSize(QSize(39,18))
        self.failsafeSettings['Use alternate Minimum Distance failsafe procedure when close to home'].setStyleSheet("QPushButton {border: none;}")
        self.failsafeSettings['Use alternate Minimum Distance failsafe procedure when close to home switch'] = False
        self.failsafeSettings['Use alternate Minimum Distance failsafe procedure when close to home'].clicked.connect(self.useAlterMinFailsafeSwitchClicked)
        self.failsafeSettingGroupBoxLayout.addWidget(self.failsafeSettings['Use alternate Minimum Distance failsafe procedure when close to home'], 14, 0, 1, 1)
        self.failsafeSettingGroupBoxLayout.addWidget(QLabel("Use alternate Minimum Distance \nFailsafe Procedure when close to \nHome"), 14, 1, 1, 1)

        self.failsafeSettings['Failsafe min distance'] = QSpinBox()
        self.failsafeSettings['Failsafe min distance'].setRange(0, 5000)
        self.failsafeSettingGroupBoxLayout.addWidget(self.failsafeSettings['Failsafe min distance'], 15, 0, 1, 1)
        self.failsafeSettingGroupBoxLayout.addWidget(QLabel("Failsafe Min Distance in cm"), 15, 1, 1, 1)

        self.failsafeSettings['Failsafe min distance procedure'] = QComboBox()
        self.failsafeSettingGroupBoxLayout.addWidget(self.failsafeSettings['Failsafe min distance procedure'], 16, 0, 1, 1)
        self.failsafeSettingGroupBoxLayout.addWidget(QLabel("Failsafe Min Distance Procedure"), 16, 1, 1, 1)

    def featureSwitchClicked(self, index):
        if self.featureSwitchValue[index] == False:
            self.featureSwitch[index].setIcon(QIcon(self.switchONImage))
            self.featureSwitchValue[index] = True
        elif self.featureSwitchValue[index] == True:
            self.featureSwitch[index].setIcon(QIcon(self.switchOFFImage))
            self.featureSwitchValue[index] = False

    def motorServoOutputSwitchClicked(self):
        if self.escmotorSettings['Enable motor and servo output switch'] == False:
            self.escmotorSettings['Enable motor and servo output'].setIcon(QIcon(self.switchONImage))
            self.escmotorSettings['Enable motor and servo output switch'] = True
        elif self.escmotorSettings['Enable motor and servo output switch'] == True:
            self.escmotorSettings['Enable motor and servo output'].setIcon(QIcon(self.switchOFFImage))
            self.escmotorSettings['Enable motor and servo output switch'] = False

    # Adjust esc fresh rate when esc protocol is changed.
    def escProtocolChanged(self, index):
        tempESCMotorProtocol = self.escmotorSettings['ESC protocol'].currentIndex()
        tempESCMotorProtocolName = self.userSettingData['ESC/Motor Features']['ESC protocol Options'][tempESCMotorProtocol]
        tempESCRefreshRateOptions = self.userSettingData['ESC/Motor Features']['ESC refresh rate Options'][self.userSettingData['ESC/Motor Features']['ESC protocol Options'][tempESCMotorProtocol]]
        self.escmotorSettings['ESC refresh rate'].clear()
        self.escmotorSettings['ESC refresh rate'].addItems(tempESCRefreshRateOptions)
        tempESCRefreshRateDefault = self.userSettingData['ESC/Motor Features']['ESC refresh rate default Options'][tempESCMotorProtocolName]
        self.escmotorSettings['ESC refresh rate'].setCurrentIndex(tempESCRefreshRateOptions.index(tempESCRefreshRateDefault))
        self.escmotorSettings['Servo refresh rate'].clear()
        self.escmotorSettings['Servo refresh rate'].addItems(self.userSettingData['ESC/Motor Features']['Servo refresh rate Options'])
        self.escmotorSettings['Servo refresh rate'].setCurrentIndex(self.userSettingData['ESC/Motor Features']['Servo refresh rate'])

    def donotSpinMotorWhenArmedSwitchClicked(self):
        if self.escmotorSettings['Do not spin the motors when armed switch'] == False:
            self.escmotorSettings['Do not spin the motors when armed'].setIcon(QIcon(self.switchONImage))
            self.escmotorSettings['Do not spin the motors when armed switch'] = True
        elif self.escmotorSettings['Do not spin the motors when armed switch'] == True:
            self.escmotorSettings['Do not spin the motors when armed'].setIcon(QIcon(self.switchOFFImage))
            self.escmotorSettings['Do not spin the motors when armed switch'] = False

    def synchronizeLooptimeWithGyroSwitchClicked(self):
        if self.systemConfigureSettings['Synchronize looptime with gyroscope switch'] == False:
            self.systemConfigureSettings['Synchronize looptime with gyroscope'].setIcon(QIcon(self.switchONImage))
            self.systemConfigureSettings['Synchronize looptime with gyroscope switch'] = True
        elif self.systemConfigureSettings['Synchronize looptime with gyroscope switch'] == True:
            self.systemConfigureSettings['Synchronize looptime with gyroscope'].setIcon(QIcon(self.switchOFFImage))
            self.systemConfigureSettings['Synchronize looptime with gyroscope switch'] = False

    def batteryCurrentMonitorSwitchClicked(self):
        if self.currentSensorSettings['Battery current monitoring switch'] == False:
            self.currentSensorSettings['Battery current monitoring'].setIcon(QIcon(self.switchONImage))
            self.currentSensorSettings['Battery current monitoring switch'] = True
        elif self.currentSensorSettings['Battery current monitoring switch'] == True:
            self.currentSensorSettings['Battery current monitoring'].setIcon(QIcon(self.switchOFFImage))
            self.currentSensorSettings['Battery current monitoring switch'] = False

    def batteryVoltageMonitorSwitchClicked(self):
        if self.batteryVoltageSettings['Battery voltage monitoring switch'] == False:
            self.batteryVoltageSettings['Battery voltage monitoring'].setIcon(QIcon(self.switchONImage))
            self.batteryVoltageSettings['Battery voltage monitoring switch'] = True
        elif self.batteryVoltageSettings['Battery voltage monitoring switch'] == True:
            self.batteryVoltageSettings['Battery voltage monitoring'].setIcon(QIcon(self.switchOFFImage))
            self.batteryVoltageSettings['Battery voltage monitoring switch'] = False

    def failsafeKillSwitchClicked(self):
        if self.failsafeSettings['Failsafe Kill Switch switch'] == False:
            self.failsafeSettings['Failsafe Kill Switch'].setIcon(QIcon(self.switchONImage))
            self.failsafeSettings['Failsafe Kill Switch switch'] = True
        elif self.failsafeSettings['Failsafe Kill Switch switch'] == True:
            self.failsafeSettings['Failsafe Kill Switch'].setIcon(QIcon(self.switchOFFImage))
            self.failsafeSettings['Failsafe Kill Switch switch'] = False

    def useGPSNavTelSwitchClicked(self):
        if self.gpsSettings['GPS for navigation and telemetry switch'] == False:
            self.gpsSettings['GPS for navigation and telemetry'].setIcon(QIcon(self.switchONImage))
            self.gpsSettings['GPS for navigation and telemetry switch'] = True
        elif self.gpsSettings['GPS for navigation and telemetry switch'] == True:
            self.gpsSettings['GPS for navigation and telemetry'].setIcon(QIcon(self.switchOFFImage))
            self.gpsSettings['GPS for navigation and telemetry switch'] = False

    def useAlterMinFailsafeSwitchClicked(self):
        if self.failsafeSettings['Use alternate Minimum Distance failsafe procedure when close to home switch'] == False:
            self.failsafeSettings['Use alternate Minimum Distance failsafe procedure when close to home'].setIcon(QIcon(self.switchONImage))
            self.failsafeSettings['Use alternate Minimum Distance failsafe procedure when close to home switch'] = True
            self.failsafeSettings['Failsafe min distance'].setValue(2000)
        elif self.failsafeSettings['Use alternate Minimum Distance failsafe procedure when close to home switch'] == True:
            self.failsafeSettings['Use alternate Minimum Distance failsafe procedure when close to home'].setIcon(QIcon(self.switchOFFImage))
            self.failsafeSettings['Use alternate Minimum Distance failsafe procedure when close to home switch'] = False
            self.failsafeSettings['Failsafe min distance'].setValue(0)
        # if use alternate min distance switch is on, then set the min distance
        #    to 2000 cm automatically; if it is turned off, then set it to 0.
        # Doing this is because there is no value saving the value of this
        #    switch, we determine the switch on or off actually by the value
        #    of this min distance: if the distance is 0, then consider it as
        #    off; if the distance is not 0, then consider it as on.

    def loadValuesFromDefault(self):
        self.defaultSettingData = readDefaultSettingFile()

    def loadValuesFromUserSaved(self):
        self.userSettingData = readUserSettingFile()

    # Transfer values from qsObj to userSettingData
    def setValues(self):
        # Other Features
        # From qsObj msp_feature
        self.userSettingData['Other Features']['Mask'] = self.qsObj.msp_feature['mask']
        tempFeatureMask = format(self.userSettingData['Other Features']['Mask'], '032b')
        # Also need to set the value of switches

        # Port
        # From qsObj msp_cf_serial_config
        for i in range(int(len(self.qsObj.msp_cf_serial_config)/6)):
            self.userSettingData['Port'][str(self.qsObj.msp_cf_serial_config[6*i])] = list(self.qsObj.msp_cf_serial_config[6*i+1:6*i+6])

        # Mixer
        # From qsObj msp_mixer
        self.userSettingData['Mixer']['Mixer'] = self.qsObj.msp_mixer['mixer_mode']

        # Sensors
        # From qsObj msp_sensor_config
        self.userSettingData['Sensors']['Accelerometer'] = self.qsObj.msp_sensor_config['acc']
        self.userSettingData['Sensors']['Magnetometer'] = self.qsObj.msp_sensor_config['mag']
        self.userSettingData['Sensors']['Barometer'] = self.qsObj.msp_sensor_config['baro']
        self.userSettingData['Sensors']['Pitot tube'] = self.qsObj.msp_sensor_config['pitot']
        self.userSettingData['Sensors']['Rangefinder'] = self.qsObj.msp_sensor_config['rangefinder']
        self.userSettingData['Sensors']['Optical Flow'] = self.qsObj.msp_sensor_config['opflow']

        # Board and sensor alignment
        # From qsObj msp_board_alignment and msp_sensor_alignment
        self.userSettingData['Board and Sensor Alignment']['Roll degrees'] = self.qsObj.msp_board_alignment['roll_deci_degrees']
        self.userSettingData['Board and Sensor Alignment']['Pitch degrees'] = self.qsObj.msp_board_alignment['pitch_deci_degrees']
        self.userSettingData['Board and Sensor Alignment']['Yaw degrees'] = self.qsObj.msp_board_alignment['yaw_deci_degrees']
        self.userSettingData['Board and Sensor Alignment']['Gyro alignment'] = self.qsObj.msp_sensor_alignment['gyro_align']
        self.userSettingData['Board and Sensor Alignment']['Acc alignment'] = self.qsObj.msp_sensor_alignment['acc_align']
        self.userSettingData['Board and Sensor Alignment']['Mag alignment'] = self.qsObj.msp_sensor_alignment['mag_align']

        # Receiver mode
        # From qsObj msp_rx_config
        self.userSettingData['Receiver Mode']['Receiver Mode'] = self.qsObj.msp_rx_config['receiver_type']
        # print(self.qsObj.msp_rx_config)

        # GPS
        # From qsObj msp_misc
        if tempFeatureMask[31-7] == "1":
            self.userSettingData['GPS']['GPS for navigation and telemetry'] = True
        elif tempFeatureMask[31-7] == "0":
            self.userSettingData['GPS']['GPS for navigation and telemetry'] = False
        self.userSettingData['GPS']['Protocol'] = self.qsObj.msp_misc['gps_provider']
        self.userSettingData['GPS']['Ground Assistance Type'] = self.qsObj.msp_misc['gps_sbas_mode']
        self.userSettingData['GPS']['Magnetometer Declination'] = self.qsObj.msp_misc['mag_declination']

        # 3D
        # From qsObj msp_3d
        self.userSettingData['3D']['3D Deadband Low'] = self.qsObj.msp_3d['deadband3d_low']
        self.userSettingData['3D']['3D Deadband High'] = self.qsObj.msp_3d['deadband3d_high']
        self.userSettingData['3D']['3D Neutral'] = self.qsObj.msp_3d['neutral3d']

        # Name
        # From qsObj msp_name
        self.userSettingData['Personalization']['Craft Name'] = self.qsObj.msp_name

        # ESC/Motor Features
        # From qsObj msp_advanced_config and msp_misc
        if tempFeatureMask[31-28] == "1":
            self.userSettingData['ESC/Motor Features']['Enable motor and servo output'] = True
        elif tempFeatureMask[31-28] == "0":
            self.userSettingData['ESC/Motor Features']['Enable motor and servo output'] = False
        self.userSettingData['ESC/Motor Features']['ESC protocol'] = self.qsObj.msp_advanced_config['motor_pwm_protocol']
        escProtocolName = self.userSettingData['ESC/Motor Features']['ESC protocol Options'][self.qsObj.msp_advanced_config['motor_pwm_protocol']]
        self.userSettingData['ESC/Motor Features']['ESC refresh rate'] = self.userSettingData['ESC/Motor Features']['ESC refresh rate Options'][escProtocolName].index(str(self.qsObj.msp_advanced_config['motor_pwm_rate'])+"Hz")
        self.userSettingData['ESC/Motor Features']['Servo refresh rate'] = self.userSettingData['ESC/Motor Features']['Servo refresh rate Options'].index(str(self.qsObj.msp_advanced_config['servo_pwm_rate'])+"Hz")
        if tempFeatureMask[31-4] == "1":
            self.userSettingData['ESC/Motor Features']['Do not spin the motors when armed'] = True
        elif tempFeatureMask[31-4] == "0":
            self.userSettingData['ESC/Motor Features']['Do not spin the motors when armed'] = False
        self.userSettingData['ESC/Motor Features']['Min throttle'] = self.qsObj.msp_misc['min_throttle']
        self.userSettingData['ESC/Motor Features']['Mid throttle'] = self.qsObj.msp_misc['mid_rc']
        self.userSettingData['ESC/Motor Features']['Max throttle'] = self.qsObj.msp_misc['max_throttle']
        self.userSettingData['ESC/Motor Features']['Min command'] = self.qsObj.msp_misc['min_command']

        # System Configuration
        # From qsObj msp_inav_pid, msp_loop_time and msp_advanced_config
        self.userSettingData['System Configuration']['Gyroscope LPF cutoff frequency'] = self.qsObj.msp_inav_pid['gyro_lpf']
        self.userSettingData['System Configuration']['Asynchronous mode'] = self.qsObj.msp_inav_pid['async_mode']
        if self.qsObj.msp_advanced_config['gyro_sync'] == 1:
            self.userSettingData['System Configuration']['Synchronize looptime with gyroscope'] = True
        elif self.qsObj.msp_advanced_config['gyro_sync'] == 0:
            self.userSettingData['System Configuration']['Synchronize looptime with gyroscope'] = False
        self.userSettingData['System Configuration']['Flight controller loop time'] = self.qsObj.msp_loop_time['looptime']

        # Battery Voltage
        # From qsObj msp_misc and msp_analog
        if tempFeatureMask[31-1] == "1":
            self.userSettingData['Battery Voltage']['Battery voltage monitoring'] = True
        elif tempFeatureMask[31-1] == "0":
            self.userSettingData['Battery Voltage']['Battery voltage monitoring'] = False
        self.userSettingData['Battery Voltage']['Min cell voltage'] = self.qsObj.msp_misc['voltage_cell_min']/10.0
        self.userSettingData['Battery Voltage']['Max cell voltage'] = self.qsObj.msp_misc['voltage_cell_max']/10.0
        self.userSettingData['Battery Voltage']['Warning cell voltage'] = self.qsObj.msp_misc['voltage_cell_warning']/10.0
        self.userSettingData['Battery Voltage']['Voltage scale'] = self.qsObj.msp_misc['voltage_scale']
        self.userSettingData['Battery Voltage']['Battery voltage'] = self.qsObj.msp_analog['vbat']

        # Current Sensor
        # From qsObj
        if tempFeatureMask[31-11] == "1":
            self.userSettingData['Current Sensor']['Battery current monitoring'] = True
        elif tempFeatureMask[31-1] == "0":
            self.userSettingData['Current Sensor']['Battery current monitoring'] = False
        self.userSettingData['Current Sensor']['Scale the output voltage to milliamps'] = self.qsObj.msp_current_meter_config['scale']
        self.userSettingData['Current Sensor']['Offset in millivolt steps'] = self.qsObj.msp_current_meter_config['offset']
        self.userSettingData['Current Sensor']['Battery current'] = self.qsObj.msp_analog['amps']

        # Battery Capacity
        # From qsObj
        # self.userSettingData['Battery Capacity']['Unit']
        # self.userSettingData['Battery Capacity']['Capacity']  msp_analog['powermetersum'] msp_current_meter_config['capabity_value']
        # self.userSettingData['Battery Capacity']['Warning capacity']
        # self.userSettingData['Battery Capacity']['Critical capacity']

        # Failsafe
        # From qsObj msp_rx_config and msp_failsafe_config
        self.userSettingData['Failsafe']['Min length'] = self.qsObj.msp_rx_config['rx_min_usec']
        self.userSettingData['Failsafe']['Max length'] = self.qsObj.msp_rx_config['rx_max_usec']
        if self.qsObj.msp_failsafe_config['failsafe_kill_switch'] == 0:
            self.userSettingData['Failsafe']['Failsafe kill switch'] = False
        elif self.qsObj.msp_failsafe_config['failsafe_kill_switch'] == 1:
            self.userSettingData['Failsafe']['Failsafe kill switch'] = True
        self.userSettingData['Failsafe']['Guard time'] = self.qsObj.msp_failsafe_config['failsafe_delay']
        self.userSettingData['Failsafe']['Failsafe throttle low delay'] = self.qsObj.msp_failsafe_config['failsafe_throttle_low_delay']
        self.userSettingData['Failsafe']['Procedure'] = self.qsObj.msp_failsafe_config['failsafe_procedure']
        self.userSettingData['Failsafe']['Throttle value while landing'] = self.qsObj.msp_failsafe_config['failsafe_throttle']
        self.userSettingData['Failsafe']['Delay for turning off the motors during failsafe'] = self.qsObj.msp_failsafe_config['failsafe_off_delay']
        self.userSettingData['Failsafe']['Failsafe min distance'] = self.qsObj.msp_failsafe_config['failsafe_min_distance']
        if self.userSettingData['Failsafe']['Failsafe min distance'] > 0:
            self.userSettingData['Failsafe']['Use alternate min distance failsafe procedure'] = True
        elif self.userSettingData['Failsafe']['Failsafe min distance'] == 0:
            self.userSettingData['Failsafe']['Use alternate min distance failsafe procedure'] = False
        self.userSettingData['Failsafe']['Failsafe min distance procedure'] = self.qsObj.msp_failsafe_config['failsafe_min_distance_procedure']
        # Set UI Values
        self.setUIValues()

# Port
# Mixer
# Sensors
# Board Alignment
# Receiver
# GPS
# 3D
# Name
# Other Features
# ESC/Motor Feature
# System Configure
# Battery Voltage
# Current Sensor
# Battery Capacity
# Failsafe Settings

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = ConfigureWidget()
    form.resize(1080,720)
    form.show()
    app.exec_()
