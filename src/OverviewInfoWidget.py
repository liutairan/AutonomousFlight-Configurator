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
from functools import partial
# from apscheduler.schedulers.background import BackgroundScheduler
from random import *
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
    QListWidget, QListWidgetItem, QAbstractItemView, QWidget, QAction,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QHeaderView, QLabel, QTreeWidget, QTreeWidgetItem, QToolBar, QLineEdit,
    QCompleter, QSizePolicy, QComboBox, QMessageBox, QDialog, QDialogButtonBox,
    QFileDialog, QGridLayout, QFormLayout, QGroupBox)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QTimer

class OverviewInfoWidget(QWidget):
    overviewInfoSignal = pyqtSignal(int)
    def __init__(self, parent=None, qsObj=None):
        super(QWidget, self).__init__(parent)
        self.initUI()
        self.running = False
        self.qsObj = qsObj
        self.initVariables()
        self.setUpdateTimer()

    def initUI(self):
        self.bundle_dir = os.path.dirname(os.path.abspath(__file__))
        # self.layout = QHBoxLayout()
        self.layout = QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)

        # Attitude Group
        attitudeGroupBox = QGroupBox(self)
        self.layout.addWidget(attitudeGroupBox, 0, 0)
        attitudeGroupBoxLayout = QVBoxLayout()
        self.attitudeLabelList = []
        self.attitudeFieldList = ["Heading", "Pitch", "Roll"]
        for field in self.attitudeFieldList:
            self.attitudeLabelList.append(QLabel(field))
        for label in self.attitudeLabelList:
            attitudeGroupBoxLayout.addWidget(label)
        attitudeGroupBoxLayout.addStretch(1)
        attitudeGroupBox.setLayout(attitudeGroupBoxLayout)

        # Arming Info Group
        armingInfoGroupBox = QGroupBox(self)
        self.layout.addWidget(armingInfoGroupBox, 1, 0)
        armingInfoGroupBoxLayout = QVBoxLayout()
        self.armingInfoLabelList = {}
        self.armingFlagFieldList = ["OK_TO_ARM", "PREVENT_ARMING", "ARMED",
                                "WAS_EVER_ARMED", "BLOCK_UAV_NOT_LEVEL",
                                "BLOCK_SENSORS_CALIB", "BLOCK_SYSTEM_OVERLOAD",
                                "BLOCK_NAV_SAFETY", "BLOCK_COMPASS_NOT_CALIB",
                                "BLOCK_ACC_NOT_CALIB", "BLOCK_HARDWARE_FAILURE"]
        self.armingflags = {'OK_TO_ARM':0,
                       'PREVENT_ARMING':0,
                       'ARMED':0,
                       'WAS_EVER_ARMED':0,
                       'BLOCK_UAV_NOT_LEVEL':0,
                       'BLOCK_SENSORS_CALIB':0,
                       'BLOCK_SYSTEM_OVERLOAD':0,
                       'BLOCK_NAV_SAFETY':0,
                       'BLOCK_COMPASS_NOT_CALIB':0,
                       'BLOCK_ACC_NOT_CALIB':0,
                       'UNUSED':0,
                       'BLOCK_HARDWARE_FAILURE':0}
        # for key,value in self.armingflags.items():
        #     self.armingInfoLabelList.append(QLabel(key))
        for field in self.armingFlagFieldList:
            self.armingInfoLabelList[field] = QLabel(field)
            armingInfoGroupBoxLayout.addWidget(self.armingInfoLabelList[field])
        # for label in self.armingInfoLabelList:
        #     armingInfoGroupBoxLayout.addWidget(label)
        armingInfoGroupBoxLayout.addStretch(1)
        armingInfoGroupBox.setLayout(armingInfoGroupBoxLayout)

        # Battery Info Group
        batteryInfoGroupBox = QGroupBox(self)
        self.layout.addWidget(batteryInfoGroupBox, 0, 1)
        batteryInfoGroupBoxLayout = QVBoxLayout()
        batteryFieldList = ["Battery detected cell count",
                            "Battery voltage",
                            "Battery left",
                            "Battery remaining capacity",
                            "Battery full when plugged",
                            "Battery use cap thresholds",
                            "Current draw",
                            "Capacity drawn",
                            "Capacity drawn",
                            "RSSI"]
        self.batteryInfoLabelList = []
        for field in batteryFieldList:
            self.batteryInfoLabelList.append(QLabel(field))
        for label in self.batteryInfoLabelList:
            batteryInfoGroupBoxLayout.addWidget(label)
        batteryInfoGroupBoxLayout.addStretch(1)
        batteryInfoGroupBox.setLayout(batteryInfoGroupBoxLayout)

        # System Info Group
        systemInfoGroupBox = QGroupBox(self)
        self.layout.addWidget(systemInfoGroupBox, 1, 1)
        systemInfoGroupBoxLayout = QVBoxLayout()
        self.systemFieldList = ["Packet error",
                           "I2C error",
                           "Cycle time",
                           "CPU load",
                           "MSP Version",
                           "MSP Load",
                           "MSP round trip",
                           "HW round trip",
                           "Drop ratio"]
        self.systemInfoLabelDict = {}
        for field in self.systemFieldList:
            self.systemInfoLabelDict[field] = QLabel(field)
            systemInfoGroupBoxLayout.addWidget(self.systemInfoLabelDict[field])
        # for field in self.systemFieldList:
        #     self.systemInfoLabelList.append(QLabel(field))
        # for label in self.systemInfoLabelList:
        #     systemInfoGroupBoxLayout.addWidget(label)
        systemInfoGroupBoxLayout.addStretch(1)
        systemInfoGroupBox.setLayout(systemInfoGroupBoxLayout)

        # GPS Info Group
        gpsInfoGroupBox = QGroupBox(self)
        self.layout.addWidget(gpsInfoGroupBox, 0, 2)
        gpsInfoGroupBoxLayout = QVBoxLayout()
        self.gpsFieldList = ["Fix type",
                             "Sats",
                             "Latitude",
                             "Longitude",
                             "Altitude",
                             "Speed",
                             "HDOP",
                             "EPH",
                             "EPV",
                             "Update Frequency"]
        self.gpsInfoLabelDict = {}
        for field in self.gpsFieldList:
            self.gpsInfoLabelDict[field] = QLabel(field)
            gpsInfoGroupBoxLayout.addWidget(self.gpsInfoLabelDict[field])
        # for field in gpsFieldList:
        #     self.gpsInfoLabelList.append(QLabel(field))
        # for label in self.gpsInfoLabelList:
        #     gpsInfoGroupBoxLayout.addWidget(label)
        gpsInfoGroupBoxLayout.addStretch(1)
        gpsInfoGroupBox.setLayout(gpsInfoGroupBoxLayout)

        # Set Main Layout of this page
        self.setLayout(self.layout)

    # Use QTimer
    def initVariables(self):
        self.step = {}
        self.step['attitude'] = 0.01
        self.step['arming flag'] = 0.01
        self.step['battery'] = 0.01
        self.step['communication'] = 0.1
        self.step['gps'] = 0.1

    # Use QTimer
    def setUpdateTimer(self):
        ## Start a timer to rapidly update the plot
        self.sched = {}

        self.sched['attitude'] = QTimer()
        self.sched['attitude'].timeout.connect(partial(self.dataRequest, 0))

        self.sched['arming flag'] = QTimer()
        self.sched['arming flag'].timeout.connect(partial(self.dataRequest, 1))

        self.sched['battery'] = QTimer()
        self.sched['battery'].timeout.connect(partial(self.dataRequest, 2))

        self.sched['communication'] = QTimer()
        self.sched['communication'].timeout.connect(partial(self.dataRequest, 3))

        self.sched['gps'] = QTimer()
        self.sched['gps'].timeout.connect(partial(self.dataRequest, 4))

    # Use QTimer
    def dataRequest(self, ind):
        # ind is the index of fields to be updated,
        #    ind = 0, 1, 2, 3, 4
        #    ind = 0: attitude
        #    ind = 1:
        #    ind = 2:
        #    ind = 3:
        #    ind = 4:
        self.overviewInfoSignal.emit(ind)

    # Use QTimer, start all the timers.
    def start(self):
        self.sched['attitude'].start(int(1.0/self.step['attitude']))
        self.sched['arming flag'].start(int(1.0/self.step['arming flag']))
        self.sched['battery'].start(int(1.0/self.step['battery']))
        self.sched['communication'].start(int(1.0/self.step['communication']))
        self.sched['gps'].start(int(1.0/self.step['gps']))

    # Use QTimer, stop all the timers.
    def stop(self):
        self.sched['attitude'].stop()
        self.sched['arming flag'].stop()
        self.sched['battery'].stop()
        self.sched['communication'].stop()
        self.sched['gps'].stop()

    # Update attitude labels
    def updateAttitudeLabels(self):
        self.attitudeLabelList[0].setText("Heading: " + str(self.qsObj.msp_attitude['heading']) + " deg")
        self.attitudeLabelList[1].setText("Pitch: " + str(self.qsObj.msp_attitude['angy']) + " deg")
        self.attitudeLabelList[2].setText("Roll: " + str(self.qsObj.msp_attitude['angx']) + " deg")

    # Update arming flag labels
    def updateArmingFlagLabels(self):
        for field in self.armingFlagFieldList:
            self.armingflags[field] = self.qsObj.parsed_armingflags[field]
            if self.armingflags[field] == "0":
                self.armingInfoLabelList[field].setStyleSheet("QLabel {color:green}")
            elif self.armingflags[field] == "1":
                self.armingInfoLabelList[field].setStyleSheet("QLabel {color:red}")

    # Update battery labels
    def updateBatteryLabels(self):
        pass

    # Update communication labels
    def updateCommunicationLabels(self):
        for field in self.systemFieldList:
            data = 0
            if field == "Cycle time":
                data = self.qsObj.msp_status_ex['cycleTime']
            elif field == "I2C error":
                data = self.qsObj.msp_status_ex['i2cError']
            elif field == "CPU load":
                data = self.qsObj.msp_status_ex['averageSystemLoadPercent']
            else:
                pass
            self.systemInfoLabelDict[field].setText(field + ": " + str(data))

    # Update GPS labels
    def updateGPSLabels(self):
        msp_raw_gps = {'gps_fix':0, 'gps_numsat':0, 'gps_lat':0, 'gps_lon':0, 'gps_altitude':0, 'gps_speed':0, 'gps_ground_course':0, 'gps_hdop':0}
        for field in self.gpsFieldList:
            data = None
            if field == "Fix type":
                if self.qsObj.msp_raw_gps['gps_fix'] == 0:
                    data = "No Valid Fix"
                elif self.qsObj.msp_raw_gps['gps_fix'] == 1:
                    data = "2D Fix"
                elif self.qsObj.msp_raw_gps['gps_fix'] == 2:
                    data = "3D Fix"
                else:
                    pass
            elif field == "Sats":
                data = str(self.qsObj.msp_raw_gps['gps_numsat'])
            elif field == "Latitude":
                data = str(float(self.qsObj.msp_raw_gps['gps_lat'])/10000000.0) + " deg"
            elif field == "Longitude":
                data = str(float(self.qsObj.msp_raw_gps['gps_lon'])/10000000.0) + " deg"
            elif field == "Altitude":
                data = str(self.qsObj.msp_raw_gps['gps_altitude']) + " m"
            elif field == "Speed":
                data = str(self.qsObj.msp_raw_gps['gps_speed']) + " cm/s"
            elif field == "HDOP":
                data = str(0.00)
            elif field == "EPH":
                data = " m"
            elif field == "EPV":
                data = " m"
            elif field == "Update Frequency":
                data = " Hz"
            self.gpsInfoLabelDict[field].setText(field + ": " + data)
