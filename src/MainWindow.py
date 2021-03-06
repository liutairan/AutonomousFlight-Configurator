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
import time
import string
import math
from random import *
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
    QListWidget, QListWidgetItem, QAbstractItemView, QWidget, QAction,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QHeaderView, QLabel, QTreeWidget, QTreeWidgetItem, QToolBar, QLineEdit,
    QCompleter, QSizePolicy, QComboBox, QMessageBox, QDialog, QDialogButtonBox,
    QFileDialog, QStatusBar, QTabWidget, QFormLayout, QRadioButton)
from PyQt5.QtGui import QIcon, QPainter
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QStringListModel, QRect, QSize, Qt, QTimer

# from apscheduler.schedulers.background import BackgroundScheduler

from HeaderWidget import InitHeaderWidget, StatusHeaderWidget
from CoverPageWidget import CoverPageWidget
from OverviewInfoWidget import OverviewInfoWidget
from FlightModeWidget import FlightModeWidget
from CLIWidget import CLIWidget
from SerialTerminalWidget import SerialTerminalWidget
from CalibrationWidget import CalibrationWidget
from ConfigureWidget import ConfigureWidget
from ParameterSettingWidget import ParameterSettingWidget
from SensorWidget import SensorWidget
from MotorInfoWidget import MotorInfoWidget
from TopologyWidget import TopologyWidget
from BlackboxWidget import BlackboxWidget

from SerialCommunication import SerialCommunication
from MSPv1 import MSPv1
from QuadStates import QuadStates

class App(QMainWindow):
    resized = pyqtSignal()
    def __init__(self, width=1080, height=720):
        super().__init__()
        self.connectionStatus = False
        self.width = width
        self.height = height
        self.initUI()
        # self.initSignalsSlots()
        self.qsObj = None
        self.deviceName = ""
        self.serialPort = None
        self.currentTabMode = -1
        self.sched = None

    def initUI(self):
        self.title = 'AutonomousFlight Configurator v1.0'
        self.left = 0
        self.top = 0
        # self.width = 1080
        # self.height = 720
        self.toolbarheight = 65
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.centerWindow()
        self.bundle_dir = os.path.dirname(os.path.abspath(__file__))
        self.initWidgets()
        self.setFocus()

    def centerWindow(self):
        frameGeo = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGeo.moveCenter(centerPoint)
        self.move(frameGeo.topLeft())

    def initWidgets(self):
        # HeaderBar
        self.initHeaderWidget = InitHeaderWidget(self)
        self.initHeaderWidget.setGeometry(0, 0, self.width, 100)
        self.initHeaderWidget.show()
        self.initHeaderWidget.connectionStatusChangedSignal.connect(self.processInitConnection)
        # Init CoverPage
        self.coverPageWidget = CoverPageWidget(self)
        self.coverPageWidget.setGeometry(0, 100, self.width, self.height-100)
        self.coverPageWidget.show()

        # Show
        self.show()

    def initWorkingWidget(self):
        # Init StatusHeaderBar
        self.statusHeaderWidget = StatusHeaderWidget(self, self.qsObj)
        self.statusHeaderWidget.setGeometry(0, 0, self.width, 100)
        self.statusHeaderWidget.connectionStatusChangedSignal.connect(self.processStatusConnection)
        # self.statusHeaderWidget.hide()
        # Init InfoTabs
        self.infoTabsWidget = QTabWidget(self)
        self.infoTabsWidget.setGeometry(0, 100, self.width, self.height-130)
        # Vertical: 2
        self.infoTabsWidget.setTabPosition(2)

        self.tabNameList = ["CLI", "Overview", "Calibration", "Configure",
                            "ParameterSetting", "Mode", "Sensor", "Motor",
                            "Topology", "Blackbox", "SerialTerminal"]

        self.tabObjectDict = {"CLI":CLIWidget(self),
                              "Overview":OverviewInfoWidget(self, self.qsObj),
                              "Calibration":CalibrationWidget(self, self.qsObj),
                              "Configure":ConfigureWidget(self, self.qsObj),
                              "ParameterSetting":ParameterSettingWidget(self, self.qsObj),
                              "Mode":FlightModeWidget(self, self.qsObj),
                              "Sensor":SensorWidget(self, self.qsObj),
                              "Motor":MotorInfoWidget(self, self.qsObj),
                              "Topology":TopologyWidget(self, self.qsObj),
                              "Blackbox":BlackboxWidget(self),
                              "SerialTerminal":SerialTerminalWidget(self)}

        for key,value in self.tabObjectDict.items():
            self.infoTabsWidget.addTab(value, key)
        # self.infoTabsWidget.hide()
        self.infoTabsWidget.currentChanged.connect(self.setTabMode)
        # Init StatusBar
        self.statusBar = QStatusBar()
        # "Packet error:","I2C error:","Cycle Time:",
        # "CPU Load:","MSP Version:", "MSP Load:",
        # "MSP Roundtrip:","HW roundtrip:","Drop ratio:"
        self.statusBarTopicList = ["Cycle Time:", "I2C error:", "CPU Load:", "MSP Version:"]
        self.packetInfoLabel = QLabel(" | ".join(self.statusBarTopicList))
        self.statusBar.addWidget(self.packetInfoLabel)
        self.setStatusBar(self.statusBar)
        # self.statusBar.hide()

    def initSignalsSlots(self):
        pass

    def processInitConnection(self):
        result = False
        try:
            # Start serial port
            self.startSerialPort()
            self.qsObj = QuadStates()
            self.mspHandle = MSPv1(self.serialPort, self.qsObj)
            result = self.mspHandle.preCheck()
            # Respond to reboot command from MSPv1
            self.mspHandle.rebootSignal.connect(self.reboot)
        except:
            print("Fail to open serial port.")
        if result:
            self.connectionStatus = True
            self.debug()
            self.initWorkingWidget()

            # Send command to MSP class
            self.statusHeaderWidget.statusDataRequestSignal.connect(self.mspHandle.processHeaderDataRequest)
            self.tabObjectDict["CLI"].cliSignal.connect(self.mspHandle.cliCommandSwitch)
            self.tabObjectDict["Overview"].overviewInfoSignal.connect(self.mspHandle.overviewInfoResponse)
            self.tabObjectDict["Mode"].flightmodeSaveSignal.connect(self.mspHandle.processModeRangesSave)
            self.tabObjectDict["Configure"].configureSaveSignal.connect(self.mspHandle.processConfigureSave)
            self.tabObjectDict["ParameterSetting"].parameterSaveSignal.connect(self.mspHandle.processParameterSettingSave)
            self.tabObjectDict["Calibration"].accCalibrateSignal.connect(self.mspHandle.processAccCalibrationRequest)
            self.tabObjectDict["Calibration"].magCalibrateSignal.connect(self.mspHandle.processMagCalibrationRequest)
            self.tabObjectDict["Calibration"].calibrationSaveSignal.connect(self.mspHandle.processCalibrationSave)
            self.tabObjectDict["Sensor"].sensorDataRequestSignal.connect(self.mspHandle.processSensorDataRequest)
            self.tabObjectDict["Motor"].motorDataRequestSignal.connect(self.mspHandle.processMotorDataRequest)
            self.tabObjectDict["Mode"].modeRCDataRequestSignal.connect(self.mspHandle.processModeRCDataRequest)
            self.tabObjectDict["Topology"].topologySaveSignal.connect(self.mspHandle.processTopologySave)
            self.tabObjectDict["SerialTerminal"].serTerSignal.connect(self.mspHandle.processSerialTerminalRequest)

            # MSP data changed will raise this signal to update labels in UI page
            self.mspHandle.headerDataUpdateSignal.connect(self.headerPageUpdate)
            self.mspHandle.cliFeedbackSignal.connect(self.tabObjectDict["CLI"].processFeedback)
            self.mspHandle.calibrationFeedbackSignal.connect(self.tabObjectDict["Calibration"].processFeedback)
            self.mspHandle.overviewDataUpdateSignal.connect(self.overviewPageUpdate)
            self.mspHandle.sensorDataUpdateSignal.connect(self.sensorPageUpdate)
            self.mspHandle.motorDataUpdateSignal.connect(self.motorPageUpdate)
            self.mspHandle.modeRCDataUpdateSignal.connect(self.flightmodePageRCUpdate)
            self.mspHandle.serTerFeedbackSignal.connect(self.tabObjectDict["SerialTerminal"].processFeedback)

            # Change UI
            self.initHeaderWidget.hide()
            self.coverPageWidget.hide()
            self.statusHeaderWidget.show()
            self.infoTabsWidget.show()
            self.infoTabsWidget.setCurrentIndex(0)
            self.setTabMode(0)
            self.statusBar.show()

            # Start StatusHeader Timer
            self.statusHeaderWidget.start()

    def processStatusConnection(self):
        self.connectionStatus = False
        #
        # self.checkSchedulerShutdown()
        self.setTabMode(0)
        self.statusHeaderWidget.stop()
        # End serial port
        self.closeSerialPort()
        self.qsObj = None
        # Change UI
        self.statusHeaderWidget.hide()
        self.infoTabsWidget.hide()
        self.statusBar.hide()
        self.initHeaderWidget.show()
        self.coverPageWidget.show()

    def keyPressEvent(self, event):
        if self.currentTabMode == 0:
            self.tabObjectDict["CLI"].keyPressed(event)

    def debug(self):
        print("---Debug---")
        # print(self.qsObj.msp_activeboxes)
        # print(self.qsObj.msp_boxids)
        # print(len(self.qsObj.msp_boxids))
        # print(self.qsObj.msp_boxnames)
        # print(len(self.qsObj.msp_boxnames))
        # print(self.qsObj.msp_mode_ranges)
        # print(len(self.qsObj.msp_mode_ranges))
        print("---Debug---")
        pass

    # Process reboot
    def reboot(self):
        # Step 1: Close current connection
        self.processStatusConnection()
        # Step 2: Wait for 0.3 seconds
        self.waitTimer = QTimer()
        self.waitTimer.setInterval(300)
        self.waitTimer.setSingleShot(True)

        # Step 3: Reconnect
        self.waitTimer.timeout.connect(self.processInitConnection)
        self.waitTimer.start(300)

    # Page index
    # Change corresponding index if the tabObjectDict is changed.
    def setTabMode(self, index):
        if self.currentTabMode != index:
            if index == self.tabNameList.index("CLI"):
                # Stop header widget update
                self.statusHeaderWidget.stop()
            elif self.currentTabMode == self.tabNameList.index("CLI"):
                # Resume header widget update
                self.statusHeaderWidget.start()
            if index == self.tabNameList.index("Overview"):
                # Overview Page
                self.tabObjectDict["Overview"].start()
            elif self.currentTabMode == self.tabNameList.index("Overview"):
                self.tabObjectDict["Overview"].stop()
            if index == self.tabNameList.index("Calibration"):
                # Calibration
                self.calibrationPageUpdate()
            # Mode
            if index == self.tabNameList.index("Mode"):
                self.flightmodePageUpdate()
                self.tabObjectDict["Mode"].start()
            elif self.currentTabMode == self.tabNameList.index("Mode"):
                self.tabObjectDict["Mode"].stop()
            # Configure
            if index == self.tabNameList.index("Configure"):
                # Configure
                self.configurePageUpdate()
            if index == self.tabNameList.index("ParameterSetting"):
                # Parameter Setting
                self.parameterSettingPageUpdate()
            if index == self.tabNameList.index("Sensor"):
                # Sensor
                self.tabObjectDict["Sensor"].start()
            elif self.currentTabMode == self.tabNameList.index("Sensor"):
                self.tabObjectDict["Sensor"].stop()
            if index == self.tabNameList.index("Motor"):
                # Motor
                self.tabObjectDict["Motor"].start()
            elif self.currentTabMode == self.tabNameList.index("Motor"):
                self.tabObjectDict["Motor"].stop()
            # Topology
            if index == self.tabNameList.index("Topology"):
                # Topology
                self.topologyPageUpdate()
            if index == self.tabNameList.index("Blackbox"):
                # Blackbox
                pass
            if index == self.tabNameList.index("SerialTerminal"):
                # Serial Terminal
                # Stop header widget update
                self.statusHeaderWidget.stop()
                self.tabObjectDict["SerialTerminal"].start()
            elif self.currentTabMode == self.tabNameList.index("SerialTerminal"):
                self.tabObjectDict["SerialTerminal"].stop()
                # Resume header widget update
                self.statusHeaderWidget.start()

            self.currentTabMode = index

    def startSerialPort(self):
        self.deviceName = self.initHeaderWidget.connectionMethodComboBox.currentText()
        self.serialPort = SerialCommunication(self.deviceName)

    def closeSerialPort(self):
        self.serialPort.stopDevice()
        self.serialPort = None

    def headerPageUpdate(self, ind):
        if ind == 0:
            self.statusHeaderWidget.updateMMSV()
        elif ind == 1:
            self.statusHeaderWidget.updateSensorStatus()

    def overviewPageUpdate(self, ind):
        if ind == 0:
            self.tabObjectDict["Overview"].updateAttitudeLabels()
        elif ind == 1:
            self.tabObjectDict["Overview"].updateArmingFlagLabels()
        elif ind == 2:
            self.tabObjectDict["Overview"].updateBatteryLabels()
        elif ind == 3:
            self.tabObjectDict["Overview"].updateCommunicationLabels()
        elif ind == 4:
            self.tabObjectDict["Overview"].updateGPSLabels()
        # # Update header sensor lights.
        # self.statusHeaderWidget.update(self.qsObj.msp_sensor_status)
        # Update status bar
        self.statusBarUpdate()

    def statusBarUpdate(self):
        self.statusBarTopicList = ["Cycle Time:", "I2C Error:", "CPU Load:", "MSP Version:"]
        self.statusBarValueDict = {}
        for field in self.statusBarTopicList:
            data = None
            if field == "Cycle Time:":
                data = self.qsObj.msp_status_ex['cycleTime']
            elif field == "I2C Error:":
                data = self.qsObj.msp_status_ex['i2cError']
            elif field == "CPU Load:":
                data = self.qsObj.msp_status_ex['averageSystemLoadPercent']
            elif field == "MSP Version:":
                data = "1"
            else:
                pass
            self.statusBarValueDict[field] = str(data)
        labelString = "| "
        for key,value in self.statusBarValueDict.items():
            labelString = labelString + key + value + " | "
        self.packetInfoLabel.setText(labelString)


    def sensorPageUpdate(self, ind):
        if ind == 0:
            self.tabObjectDict["Sensor"].updateACCPlot()
            self.tabObjectDict["Sensor"].updateGYROPlot()
            self.tabObjectDict["Sensor"].updateMAGPlot()
        elif ind == 1:
            self.tabObjectDict["Sensor"].updateBAROPlot()
        elif ind == 2:
            self.tabObjectDict["Sensor"].updateRangeFinderPlot()

    def motorPageUpdate(self, ind):
        if ind == 0:
            self.tabObjectDict["Motor"].updateMotorValues()

    def flightmodePageRCUpdate(self, ind):
        if ind == 0:
            self.tabObjectDict["Mode"].updateCurrentValueLabels()

    def flightmodePageUpdate(self):
        self.tabObjectDict["Mode"].setRanges()

    def parameterSettingPageUpdate(self):
        self.mspHandle.processParameterSettingCheck()
        self.tabObjectDict['ParameterSetting'].setValues()

    def configurePageUpdate(self):
        self.mspHandle.processConfigureCheck()
        self.tabObjectDict['Configure'].setValues()

    def calibrationPageUpdate(self):
        self.mspHandle.processCalibrationCheck()
        self.tabObjectDict['Calibration'].setValues()

    def topologyPageUpdate(self):
        self.mspHandle.processTopologyCheck()
        self.tabObjectDict['Topology'].setValues()
