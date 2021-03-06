import sys
import os
import string
import math
import re
import subprocess
from random import *
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
    QListWidget, QListWidgetItem, QAbstractItemView, QWidget, QAction,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QHeaderView, QLabel, QTreeWidget, QTreeWidgetItem, QToolBar, QLineEdit,
    QCompleter, QSizePolicy, QComboBox, QMessageBox, QDialog, QDialogButtonBox,
    QFileDialog, QGridLayout)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QSize

import serial.tools.list_ports

class InitHeaderWidget(QWidget):
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
        #
        # Empty Spacer
        leftSpacer = QLabel()
        leftSpacer.resize(300,200)
        # Logo Image
        logoImage = QPixmap(self.bundle_dir + "/Pics/icon.png")
        logoImage = logoImage.scaled(80,80)
        logoImageLabel = QLabel()
        logoImageLabel.setPixmap(logoImage)
        # Logo Text
        textTopSpacer = QWidget()
        textTopSpacer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        logoTextLabel1 = QLabel("ATFL")
        logoTextLabel1.setFont(QFont("Times", 36, QFont.Bold))
        logoTextLabel2 = QLabel("Configurator")
        logoTextLabel2.setFont(QFont("Times", 18, QFont.Bold))
        logoTextLabel3 = QLabel("Version 0.0")
        logoTextLabel3.setFont(QFont("Times", 16, QFont.StyleItalic))
        textBottomSpacer = QWidget()
        textBottomSpacer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        logoTextLayout = QVBoxLayout()
        logoTextLayout.addWidget(textTopSpacer)
        logoTextLayout.addWidget(logoTextLabel1)
        logoTextLayout.addWidget(logoTextLabel2)
        logoTextLayout.addWidget(logoTextLabel3)
        logoTextLayout.addWidget(textBottomSpacer)

        logoLayout = QHBoxLayout()
        logoLayout.addWidget(leftSpacer)
        logoLayout.addWidget(logoImageLabel)
        logoLayout.addLayout(logoTextLayout)
        self.layout.addLayout(logoLayout)

        spacer1 = QWidget()
        spacer1.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.layout.addWidget(spacer1)

        # Connection Setting
        connectionSettingTopSpacer = QWidget()
        connectionSettingTopSpacer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.connectionMethodComboBox = QComboBox()
        self.connectionMethodComboBox.setStyleSheet("QComboBox {background-color:gray; color: white; border: none;min-width:100;}")
        devList = self.checkDeviceList()
        self.deviceList = devList
        self.connectionMethodComboBox.addItems(devList)
        self.preSetDevice()
        self.refreshButton = QPushButton(QIcon(self.bundle_dir+"/Pics/Refresh.png"), "", self)
        self.refreshButton.setStyleSheet("QPushButton {border:none}")
        self.refreshButton.setIconSize(QSize(20,20))
        self.refreshButton.clicked.connect(self.refreshButtonClicked)
        self.connectionBaudrateComboBox = QComboBox()
        self.connectionBaudrateComboBox.setStyleSheet("QComboBox {background-color:gray; color: white; border: none;min-width:100;}")
        self.connectionBaudrateComboBox.addItems(["115200", "57600", "38400", "19200", "9600"])

        connectionSettingMidSpacer = QWidget()
        connectionSettingMidSpacer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        wirelessLabel = QLabel("Wireless Mode")
        wirelessLabel.setStyleSheet("QLabel {background-color:white; border: none;}")
        wirelessLabel.setFixedSize(QSize(90,24))
        wirelessLabel.setMargin(0)

        # Switch Icon Image
        self.switchOFFImage = QPixmap(self.bundle_dir + "/Pics/OFF.png")
        self.switchONImage = QPixmap(self.bundle_dir + "/Pics/ON.png")
        self.wirelessButton = QPushButton(QIcon(self.switchOFFImage), 'OFF', self)
        self.wirelessButton.setIconSize(QSize(52,24))
        self.wirelessButton.setStyleSheet("QPushButton {background-color:white; border: none;}")
        self.wirelessButton.clicked.connect(self.wirelessButtonClicked)
        row2RightSpacer = QWidget()
        row2RightSpacer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        connectionSettingBottomSpacer = QWidget()
        connectionSettingBottomSpacer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        connectionSettingRow1Layout = QHBoxLayout()
        connectionSettingRow2Layout = QHBoxLayout()
        connectionSettingRow1Layout.addWidget(self.connectionMethodComboBox)
        connectionSettingRow1Layout.addWidget(self.refreshButton)
        connectionSettingRow1Layout.addWidget(self.connectionBaudrateComboBox)
        connectionSettingRow2Layout.addWidget(wirelessLabel)
        connectionSettingRow2Layout.addWidget(self.wirelessButton)
        connectionSettingRow2Layout.addWidget(row2RightSpacer)

        connectionSettingLayout = QVBoxLayout()
        connectionSettingLayout.addWidget(connectionSettingTopSpacer)
        connectionSettingLayout.addLayout(connectionSettingRow1Layout)
        connectionSettingLayout.addWidget(connectionSettingMidSpacer)
        connectionSettingLayout.addLayout(connectionSettingRow2Layout)
        connectionSettingLayout.addWidget(connectionSettingBottomSpacer)
        self.layout.addLayout(connectionSettingLayout)

        spacer2 = QWidget()
        spacer2.setMinimumWidth(20)
        self.layout.addWidget(spacer2)

        # Connect Button
        connButtonTopSpacer = QWidget()
        connButtonTopSpacer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.connectButton = QPushButton("Connect", self)
        self.connectButton.setStyleSheet("QPushButton {background-color:green; color: black; border: none;max-width:70;}")
        self.connectButton.setMinimumSize(80,50)
        self.connectButton.clicked.connect(self.connectionResp)
        connButtonBottomSpacer = QWidget()
        connButtonBottomSpacer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        connButtonLayout = QVBoxLayout()
        connButtonLayout.addWidget(connButtonTopSpacer)
        connButtonLayout.addWidget(self.connectButton)
        connButtonLayout.addWidget(connButtonBottomSpacer)
        self.layout.addLayout(connButtonLayout)

        rightSpacer = QLabel()
        rightSpacer.resize(300,200)
        self.layout.addWidget(rightSpacer)

        self.setLayout(self.layout)
        self.setStyleSheet("background-color:white;")

    def connectionResp(self):
        self.connectionStatusChangedSignal.emit()

    def checkDeviceList(self):
        comlist = serial.tools.list_ports.comports()
        connected = []
        for element in comlist:
            connected.append(element.device)
        return connected

    def preSetDevice(self):
        if len(self.deviceList) > 0:
            if '/dev/cu.SLAB_USBtoUART' in self.deviceList:
                self.connectionMethodComboBox.setCurrentIndex(self.deviceList.index('/dev/cu.SLAB_USBtoUART'))

    def refreshButtonClicked(self):
        devList = self.checkDeviceList()
        self.deviceList = devList
        self.connectionMethodComboBox.clear()
        self.connectionMethodComboBox.addItems(devList)
        self.preSetDevice()

    def wirelessButtonClicked(self):
        if self.wirelessButton.text() == "OFF":
            self.wirelessButton.setText("ON")
            self.wirelessButton.setIcon(QIcon(self.switchONImage))
        elif self.wirelessButton.text() == "ON":
            self.wirelessButton.setText("OFF")
            self.wirelessButton.setIcon(QIcon(self.switchOFFImage))


class StatusHeaderWidget(QWidget):
    connectionStatusChangedSignal = pyqtSignal()
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.initUI()
        self.connectionStatus = True

    def initUI(self):
        self.bundle_dir = os.path.dirname(os.path.abspath(__file__))
        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        #
        # Empty Spacer
        leftSpacer = QLabel()
        leftSpacer.resize(300,200)
        # Logo Image
        logoImage = QPixmap(self.bundle_dir + "/Pics/icon.png")
        logoImage = logoImage.scaled(80,80)
        logoImageLabel = QLabel()
        logoImageLabel.setPixmap(logoImage)
        # Logo Text
        textTopSpacer = QWidget()
        textTopSpacer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        logoTextLabel1 = QLabel("ATFL")
        logoTextLabel1.setFont(QFont("Times", 36, QFont.Bold))
        logoTextLabel2 = QLabel("Configurator")
        logoTextLabel2.setFont(QFont("Times", 18, QFont.Bold))
        logoTextLabel3 = QLabel("Version 0.0")
        logoTextLabel3.setFont(QFont("Times", 16, QFont.StyleItalic))
        textBottomSpacer = QWidget()
        textBottomSpacer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        logoTextLayout = QVBoxLayout()
        logoTextLayout.addWidget(textTopSpacer)
        logoTextLayout.addWidget(logoTextLabel1)
        logoTextLayout.addWidget(logoTextLabel2)
        logoTextLayout.addWidget(logoTextLabel3)
        logoTextLayout.addWidget(textBottomSpacer)

        logoLayout = QHBoxLayout()
        logoLayout.addWidget(leftSpacer)
        logoLayout.addWidget(logoImageLabel)
        logoLayout.addLayout(logoTextLayout)
        self.layout.addLayout(logoLayout)

        spacer1 = QWidget()
        spacer1.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.layout.addWidget(spacer1)

        # Sensor Pannel
        sensorPanelLayout = QVBoxLayout()
        sensorPanelTopSpacer = QWidget()
        sensorPanelTopSpacer.setMinimumHeight(10)

        sensorLabelLayout = QHBoxLayout()
        self.accLabel = QLabel("ACC")
        self.accLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:gray; min-width:50; min-height:70; border:1px solid gray;}")
        sensorLabelLayout.addWidget(self.accLabel)

        self.gyroLabel = QLabel("GYRO")
        self.gyroLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:gray; min-width:50; min-height:70; border:1px solid gray;}")
        sensorLabelLayout.addWidget(self.gyroLabel)

        self.campLabel = QLabel("COMP")
        self.campLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:gray; min-width:50; min-height:70; border:1px solid gray;}")
        sensorLabelLayout.addWidget(self.campLabel)

        self.baroLabel = QLabel("BARO")
        self.baroLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:gray; min-width:50; min-height:70; border:1px solid gray;}")
        sensorLabelLayout.addWidget(self.baroLabel)

        self.gpsLabel = QLabel("GPS")
        self.gpsLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:gray; min-width:50; min-height:70; border:1px solid gray;}")
        sensorLabelLayout.addWidget(self.gpsLabel)

        self.sonarLabel = QLabel("SONAR")
        self.sonarLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:gray; min-width:50; min-height:70; border:1px solid gray;}")
        sensorLabelLayout.addWidget(self.sonarLabel)

        self.pitotLabel = QLabel("PITOT")
        self.pitotLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:gray; min-width:50; min-height:70; border:1px solid gray;}")
        sensorLabelLayout.addWidget(self.pitotLabel)

        self.opticalLabel = QLabel("OPTICAL")
        self.opticalLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:gray; min-width:50; min-height:70; border:1px solid gray;}")
        sensorLabelLayout.addWidget(self.opticalLabel)

        sensorPanelBottomSpacer = QWidget()
        sensorPanelBottomSpacer.setMinimumHeight(10)

        sensorPanelLayout.addWidget(sensorPanelTopSpacer)
        sensorPanelLayout.addLayout(sensorLabelLayout)
        sensorPanelLayout.addWidget(sensorPanelBottomSpacer)
        self.layout.addLayout(sensorPanelLayout)

        # Spacer after Sensor Panel
        spacer2 = QWidget()
        spacer2.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.layout.addWidget(spacer2)

        # Connect Button
        connButtonTopSpacer = QWidget()
        connButtonTopSpacer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.connectButton = QPushButton("Disconnect", self)
        self.connectButton.setStyleSheet("QPushButton {background-color:red; color: black; border: none;}")
        self.connectButton.setMinimumSize(80,50)
        self.connectButton.clicked.connect(self.connectionResp)
        connButtonBottomSpacer = QWidget()
        connButtonBottomSpacer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        connButtonLayout = QVBoxLayout()
        connButtonLayout.addWidget(connButtonTopSpacer)
        connButtonLayout.addWidget(self.connectButton)
        connButtonLayout.addWidget(connButtonBottomSpacer)
        self.layout.addLayout(connButtonLayout)

        rightSpacer = QLabel()
        rightSpacer.resize(300,200)
        self.layout.addWidget(rightSpacer)

        self.setLayout(self.layout)
        self.setStyleSheet("background-color:white;")

    def connectionResp(self):
        self.connectionStatusChangedSignal.emit()

    def update(self, sensor_status_dict):
        if sensor_status_dict['acc'] == 0:
            self.accLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:gray; min-width:50; min-height:70; border:1px solid gray;}")
        elif sensor_status_dict['acc'] == 1:
            self.accLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:green; min-width:50; min-height:70; border:1px solid gray;}")
        elif sensor_status_dict['acc'] == 2:
            self.accLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:red; min-width:50; min-height:70; border:1px solid gray;}")

        if sensor_status_dict['gyro'] == 0:
            self.gyroLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:gray; min-width:50; min-height:70; border:1px solid gray;}")
        elif sensor_status_dict['gyro'] == 1:
            self.gyroLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:green; min-width:50; min-height:70; border:1px solid gray;}")
        elif sensor_status_dict['gyro'] == 2:
            self.gyroLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:red; min-width:50; min-height:70; border:1px solid gray;}")

        if sensor_status_dict['comp'] == 0:
            self.campLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:gray; min-width:50; min-height:70; border:1px solid gray;}")
        elif sensor_status_dict['comp'] == 1:
            self.campLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:green; min-width:50; min-height:70; border:1px solid gray;}")
        elif sensor_status_dict['comp'] == 2:
            self.campLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:red; min-width:50; min-height:70; border:1px solid gray;}")

        if sensor_status_dict['gps'] == 0:
            self.gpsLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:gray; min-width:50; min-height:70; border:1px solid gray;}")
        elif sensor_status_dict['gps'] == 1:
            self.gpsLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:green; min-width:50; min-height:70; border:1px solid gray;}")
        elif sensor_status_dict['gps'] == 2:
            self.gpsLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:red; min-width:50; min-height:70; border:1px solid gray;}")

        if sensor_status_dict['range'] == 0:
            self.sonarLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:gray; min-width:50; min-height:70; border:1px solid gray;}")
        elif sensor_status_dict['range'] == 1:
            self.sonarLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:green; min-width:50; min-height:70; border:1px solid gray;}")
        elif sensor_status_dict['range'] == 2:
            self.sonarLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:red; min-width:50; min-height:70; border:1px solid gray;}")

        if sensor_status_dict['baro'] == 0:
            self.baroLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:gray; min-width:50; min-height:70; border:1px solid gray;}")
        elif sensor_status_dict['baro'] == 1:
            self.baroLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:green; min-width:50; min-height:70; border:1px solid gray;}")
        elif sensor_status_dict['baro'] == 2:
            self.baroLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:red; min-width:50; min-height:70; border:1px solid gray;}")

        if sensor_status_dict['pitot'] == 0:
            self.pitotLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:gray; min-width:50; min-height:70; border:1px solid gray;}")
        elif sensor_status_dict['pitot'] == 1:
            self.pitotLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:green; min-width:50; min-height:70; border:1px solid gray;}")
        elif sensor_status_dict['pitot'] == 2:
            self.pitotLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:red; min-width:50; min-height:70; border:1px solid gray;}")

        if sensor_status_dict['optical'] == 0:
            self.opticalLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:gray; min-width:50; min-height:70; border:1px solid gray;}")
        elif sensor_status_dict['optical'] == 1:
            self.opticalLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:green; min-width:50; min-height:70; border:1px solid gray;}")
        elif sensor_status_dict['optical'] == 2:
            self.opticalLabel.setStyleSheet("QLabel {qproperty-alignment: AlignCenter; background-color:red; min-width:50; min-height:70; border:1px solid gray;}")
