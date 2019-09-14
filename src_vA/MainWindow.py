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
    QFileDialog, QStatusBar, QTabWidget, QFormLayout, QRadioButton)
from PyQt5.QtGui import QIcon, QPainter
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QStringListModel, QRect, QSize, Qt

from apscheduler.schedulers.background import BackgroundScheduler

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
from TopologyWidget import TopologyWidget
from BlackboxWidget import BlackboxWidget

from SerialCommunication import SerialCommunication
from MSPv1 import MSPv1
from QuadStates import QuadStates

class App(QMainWindow):
    resized = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.connectionStatus = False
        self.initUI()
        # self.initSignalsSlots()
        self.qsObj = None
        self.deviceName = ""
        self.serialPort = None
        self.currentTabMode = -1
        self.sched = None

    def initUI(self):
        self.title = 'AutonomousFlight Configurator v0.0'
        self.left = 0
        self.top = 0
        self.width = 1080
        self.height = 720
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
        self.statusHeaderWidget = StatusHeaderWidget(self)
        self.statusHeaderWidget.setGeometry(0, 0, self.width, 100)
        self.statusHeaderWidget.connectionStatusChangedSignal.connect(self.processStatusConnection)
        # self.statusHeaderWidget.hide()
        # Init InfoTabs
        self.infoTabsWidget = QTabWidget(self)
        self.infoTabsWidget.setGeometry(0, 100, self.width, self.height-130)
        # Vertical: 2
        self.infoTabsWidget.setTabPosition(2)

        self.tabObjectDict = {"CLI":CLIWidget(self),
                              "Overview":OverviewInfoWidget(self, self.qsObj),
                              "Calibration":CalibrationWidget(self, self.qsObj),
                              "Configure":ConfigureWidget(self, self.qsObj),
                              "ParameterSetting":ParameterSettingWidget(self, self.qsObj),
                              "Mode":FlightModeWidget(self, self.qsObj),
                              "Sensor":SensorWidget(self, self.qsObj),
                              "Topology":TopologyWidget(self, self.qsObj),
                              "Blackbox":BlackboxWidget(self),
                              "SerialTerminal":SerialTerminalWidget(self)}

        for key,value in self.tabObjectDict.items():
            self.infoTabsWidget.addTab(value, key)
        # self.infoTabsWidget.hide()
        self.infoTabsWidget.currentChanged.connect(self.setTabMode)
        # Init StatusBar
        self.statusBar = QStatusBar()
        self.statusBarTopicList = ["Packet error:","I2C error:","Cycle Time:",
                                   "CPU Load:","MSP Version:", "MSP Load:",
                                   "MSP Roundtrip:","HW roundtrip:","Drop ratio:"]
        self.packetInfoLabel = QLabel("|".join(self.statusBarTopicList))
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
        except:
            print("Fail to open serial port.")
        if result:
            self.connectionStatus = True
            self.debug()
            self.initWorkingWidget()

            # Send command to MSP class
            self.tabObjectDict["CLI"].cliSignal.connect(self.mspHandle.cliCommandSwitch)
            self.tabObjectDict["Overview"].overviewInfoSignal.connect(self.mspHandle.overviewInfoResponse)
            self.tabObjectDict["Mode"].flightmodeSaveSignal.connect(self.mspHandle.processModeRangesSave)
            self.tabObjectDict["Configure"].configureSaveSignal.connect(self.mspHandle.processConfigureSave)
            self.tabObjectDict["ParameterSetting"].parameterSaveSignal.connect(self.mspHandle.processParameterSettingSave)
            self.tabObjectDict["Calibration"].accCalibrateSignal.connect(self.mspHandle.processAccCalibrationRequest)
            self.tabObjectDict["Calibration"].magCalibrateSignal.connect(self.mspHandle.processMagCalibrationRequest)
            self.tabObjectDict["Calibration"].calibrationSaveSignal.connect(self.mspHandle.processCalibrationSave)
            self.tabObjectDict["Sensor"].sensorDataRequestSignal.connect(self.mspHandle.processSensorDataRequest)
            self.tabObjectDict["Topology"].topologySaveSignal.connect(self.mspHandle.processTopologySave)

            # MSP data changed will raise this signal to update labels in UI page
            self.mspHandle.cliFeedbackSignal.connect(self.tabObjectDict["CLI"].processFeedback)
            self.mspHandle.calibrationFeedbackSignal.connect(self.tabObjectDict["Calibration"].processFeedback)
            self.mspHandle.overviewDataUpdateSignal.connect(self.overviewPageUpdate)
            self.mspHandle.sensorDataUpdateSignal.connect(self.sensorPageUpdate)
            # Change UI
            self.initHeaderWidget.hide()
            self.coverPageWidget.hide()
            self.statusHeaderWidget.show()
            self.infoTabsWidget.show()
            self.infoTabsWidget.setCurrentIndex(0)
            self.setTabMode(0)
            self.statusBar.show()

    def processStatusConnection(self):
        self.connectionStatus = False
        #
        # self.checkSchedulerShutdown()
        self.setTabMode(0)
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

    # Page index
    # Change corresponding index if the tabObjectDict is changed.
    def setTabMode(self, index):
        if self.currentTabMode != index:
            if index == 1:
                # Overview Page
                self.tabObjectDict["Overview"].start()
            elif self.currentTabMode == 1:
                self.tabObjectDict["Overview"].stop()
            if index == 2:
                # Calibration
                self.calibrationPageUpdate()
            if index == 5:
                # Mode
                self.flightmodePageUpdate()
            if index == 3:
                # Configure
                self.configurePageUpdate()
            if index == 4:
                # Parameter Setting
                self.parameterSettingPageUpdate()
            if index == 6:
                # Sensor
                self.tabObjectDict["Sensor"].start()
            elif self.currentTabMode == 6:
                self.tabObjectDict["Sensor"].stop()
            if index == 7:
                # Topology
                self.topologyPageUpdate()
            if index == 8:
                # Blackbox
                pass
            self.currentTabMode = index

    def startSerialPort(self):
        self.deviceName = self.initHeaderWidget.connectionMethodComboBox.currentText()
        self.serialPort = SerialCommunication(self.deviceName)

    def closeSerialPort(self):
        self.serialPort.stopDevice()
        self.serialPort = None

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
        # Update header sensor lights.
        self.statusHeaderWidget.update(self.qsObj.msp_sensor_status)

    def sensorPageUpdate(self, ind):
        if ind == 0:
            self.tabObjectDict["Sensor"].updateACCPlot()
            self.tabObjectDict["Sensor"].updateGYROPlot()
            self.tabObjectDict["Sensor"].updateMAGPlot()
        elif ind == 1:
            self.tabObjectDict["Sensor"].updateBAROPlot()

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
