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
# from apscheduler.schedulers.background import BackgroundScheduler
from random import *
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
    QListWidget, QListWidgetItem, QAbstractItemView, QWidget, QAction,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QHeaderView, QLabel, QTreeWidget, QTreeWidgetItem, QToolBar, QLineEdit,
    QCompleter, QSizePolicy, QComboBox, QMessageBox, QDialog, QDialogButtonBox,
    QFileDialog, QGridLayout, QFormLayout, QSlider, QScrollArea, QGroupBox,
    QSpinBox, QDoubleSpinBox)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QSize

from SettingFileIO import *

class ParameterSettingWidget(QWidget):
    parameterSaveSignal = pyqtSignal(list)
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
        # PID Tuning Group
        pidTuningGroupBox = QGroupBox("PID Tuning", self)
        mainConfigureCol1Layout.addWidget(pidTuningGroupBox)
        self.pidTuningGroupBoxLayout = QGridLayout()
        self.pidTuningGroupBoxInit()
        # self.pidTuningGroupBoxLayout.addStretch(1)
        pidTuningGroupBox.setLayout(self.pidTuningGroupBoxLayout)

        # Filtering Group
        filteringGroupBox = QGroupBox("Filtering", self)
        mainConfigureCol1Layout.addWidget(filteringGroupBox)
        self.filteringGroupBoxLayout = QGridLayout()
        self.filteringGroupBoxInit()
        filteringGroupBox.setLayout(self.filteringGroupBoxLayout)

        # Miscellaneous Group
        miscellaneousGroupBox = QGroupBox("Miscellaneous", self)
        mainConfigureCol1Layout.addWidget(miscellaneousGroupBox)
        self.miscellaneousGroupBoxLayout = QGridLayout()
        self.miscellaneousGroupBoxInit()
        miscellaneousGroupBox.setLayout(self.miscellaneousGroupBoxLayout)

        mainConfigureCol1Layout.addStretch(1)

        # Second column
        # Basic Navigation Settings Group
        basicNavSettingGroupBox = QGroupBox("Basic Navigation Settings", self)
        mainConfigureCol2Layout.addWidget(basicNavSettingGroupBox)
        self.basicNavSettingGroupBoxLayout = QGridLayout()
        self.basicNavSettingGroupBoxInit()
        basicNavSettingGroupBox.setLayout(self.basicNavSettingGroupBoxLayout)

        # RTH and Landing Settings Group
        rthLandingSettingGroupBox = QGroupBox("RTH and Landing Settings", self)
        mainConfigureCol2Layout.addWidget(rthLandingSettingGroupBox)
        self.rthLandingSettingGroupBoxLayout = QGridLayout()
        self.rthLandingSettingGroupBoxInit()
        rthLandingSettingGroupBox.setLayout(self.rthLandingSettingGroupBoxLayout)

        # Position Estimator Group
        posEstGroupBox = QGroupBox("Position Estimator", self)
        mainConfigureCol2Layout.addWidget(posEstGroupBox)
        self.posEstGroupBoxLayout = QGridLayout()
        self.posEstGroupBoxInit()
        posEstGroupBox.setLayout(self.posEstGroupBoxLayout)

        mainConfigureCol2Layout.addStretch(1)

        self.setLayout(self.layout)

    def initValues(self):
        self.loadValuesFromDefault()
        # self.setUIDefaultValues()
        self.userSettingData = dict(self.defaultSettingData)
        self.setUIValues()

    def setUIDefaultValues(self):
        # PID Tuning
        self.pidTuningSettings['Roll'][0].setValue(self.defaultSettingData['PID Tuning']['Roll']['P'])
        self.pidTuningSettings['Roll'][1].setValue(self.defaultSettingData['PID Tuning']['Roll']['I'])
        self.pidTuningSettings['Roll'][2].setValue(self.defaultSettingData['PID Tuning']['Roll']['D'])
        self.pidTuningSettings['Pitch'][0].setValue(self.defaultSettingData['PID Tuning']['Pitch']['P'])
        self.pidTuningSettings['Pitch'][1].setValue(self.defaultSettingData['PID Tuning']['Pitch']['I'])
        self.pidTuningSettings['Pitch'][2].setValue(self.defaultSettingData['PID Tuning']['Pitch']['D'])
        self.pidTuningSettings['Yaw'][0].setValue(self.defaultSettingData['PID Tuning']['Yaw']['P'])
        self.pidTuningSettings['Yaw'][1].setValue(self.defaultSettingData['PID Tuning']['Yaw']['I'])
        self.pidTuningSettings['Yaw'][2].setValue(self.defaultSettingData['PID Tuning']['Yaw']['D'])
        self.pidTuningSettings['Position Z'][0].setValue(self.defaultSettingData['PID Tuning']['Position Z']['P'])
        self.pidTuningSettings['Position Z'][1].setValue(self.defaultSettingData['PID Tuning']['Position Z']['I'])
        self.pidTuningSettings['Position Z'][2].setValue(self.defaultSettingData['PID Tuning']['Position Z']['D'])
        self.pidTuningSettings['Velocity Z'][0].setValue(self.defaultSettingData['PID Tuning']['Velocity Z']['P'])
        self.pidTuningSettings['Velocity Z'][1].setValue(self.defaultSettingData['PID Tuning']['Velocity Z']['I'])
        self.pidTuningSettings['Velocity Z'][2].setValue(self.defaultSettingData['PID Tuning']['Velocity Z']['D'])
        self.pidTuningSettings['Heading'][0].setValue(self.defaultSettingData['PID Tuning']['Heading']['P'])
        self.pidTuningSettings['Heading'][1].setValue(self.defaultSettingData['PID Tuning']['Heading']['I'])
        self.pidTuningSettings['Heading'][2].setValue(self.defaultSettingData['PID Tuning']['Heading']['D'])
        self.pidTuningSettings['Position XY'][0].setValue(self.defaultSettingData['PID Tuning']['Position XY']['P'])
        self.pidTuningSettings['Position XY'][1].setValue(self.defaultSettingData['PID Tuning']['Position XY']['I'])
        self.pidTuningSettings['Position XY'][2].setValue(self.defaultSettingData['PID Tuning']['Position XY']['D'])
        self.pidTuningSettings['Velocity XY'][0].setValue(self.defaultSettingData['PID Tuning']['Velocity XY']['P'])
        self.pidTuningSettings['Velocity XY'][1].setValue(self.defaultSettingData['PID Tuning']['Velocity XY']['I'])
        self.pidTuningSettings['Velocity XY'][2].setValue(self.defaultSettingData['PID Tuning']['Velocity XY']['D'])
        self.pidTuningSettings['Surface'][0].setValue(self.defaultSettingData['PID Tuning']['Surface']['P'])
        self.pidTuningSettings['Surface'][1].setValue(self.defaultSettingData['PID Tuning']['Surface']['I'])
        self.pidTuningSettings['Surface'][2].setValue(self.defaultSettingData['PID Tuning']['Surface']['D'])
        self.pidTuningSettings['Level'][0].setValue(self.defaultSettingData['PID Tuning']['Level']['Strength'])
        self.pidTuningSettings['Level'][1].setValue(self.defaultSettingData['PID Tuning']['Level']['LPF cutoff'])
        self.pidTuningSettings['Level'][2].setValue(self.defaultSettingData['PID Tuning']['Level']['Transition'])
        self.pidTuningSettings['Roll rate'].setValue(self.defaultSettingData['PID Tuning']['Roll rate'])
        self.pidTuningSettings['Pitch rate'].setValue(self.defaultSettingData['PID Tuning']['Pitch rate'])
        self.pidTuningSettings['Yaw rate'].setValue(self.defaultSettingData['PID Tuning']['Yaw rate'])
        self.pidTuningSettings['Manual Roll rate'].setValue(self.defaultSettingData['PID Tuning']['Manual Roll rate'])
        self.pidTuningSettings['Manual Pitch rate'].setValue(self.defaultSettingData['PID Tuning']['Manual Pitch rate'])
        self.pidTuningSettings['Manual Yaw rate'].setValue(self.defaultSettingData['PID Tuning']['Manual Yaw rate'])
        self.pidTuningSettings['MagHold rate'].setValue(self.defaultSettingData['PID Tuning']['MagHold rate'])

        # Filtering
        self.filteringSettings['Gyro LPF cutoff frequency'].setValue(self.defaultSettingData['Filtering']['Gyro LPF cutoff frequency'])
        self.filteringSettings['Accelerometer LPF cutoff frequency'].setValue(self.defaultSettingData['Filtering']['Accelerometer LPF cutoff frequency'])
        self.filteringSettings['First gyro notch filter frequency'].setValue(self.defaultSettingData['Filtering']['First gyro notch filter frequency'])
        self.filteringSettings['First gyro notch filter cutoff frequency'].setValue(self.defaultSettingData['Filtering']['First gyro notch filter cutoff frequency'])
        self.filteringSettings['Second gyro notch filter frequency'].setValue(self.defaultSettingData['Filtering']['Second gyro notch filter frequency'])
        self.filteringSettings['Second gyro notch filter cutoff frequency'].setValue(self.defaultSettingData['Filtering']['Second gyro notch filter cutoff frequency'])
        self.filteringSettings['D-term LPF cutoff frequency'].setValue(self.defaultSettingData['Filtering']['D-term LPF cutoff frequency'])
        self.filteringSettings['Yaw LPF cutoff frequency'].setValue(self.defaultSettingData['Filtering']['Yaw LPF cutoff frequency'])
        self.filteringSettings['D-term notch filter frequency'].setValue(self.defaultSettingData['Filtering']['D-term notch filter frequency'])
        self.filteringSettings['D-term notch filter cutoff frequency'].setValue(self.defaultSettingData['Filtering']['D-term notch filter cutoff frequency'])

        # Miscellaneous
        self.miscellaneousSettings['Yaw jump prevention'].setValue(self.defaultSettingData['Miscellaneous']['Yaw jump prevention'])
        self.miscellaneousSettings['Yaw P limit'].setValue(self.defaultSettingData['Miscellaneous']['Yaw P limit'])
        self.miscellaneousSettings['Roll/Pitch I-term ignore rate'].setValue(self.defaultSettingData['Miscellaneous']['Roll/Pitch I-term ignore rate'])
        self.miscellaneousSettings['Yaw I-term ignore rate'].setValue(self.defaultSettingData['Miscellaneous']['Yaw I-term ignore rate'])
        self.miscellaneousSettings['Roll/Pitch acceleration limit'].setValue(self.defaultSettingData['Miscellaneous']['Roll/Pitch acceleration limit'])
        self.miscellaneousSettings['Yaw acceleration limit'].setValue(self.defaultSettingData['Miscellaneous']['Yaw acceleration limit'])
        self.miscellaneousSettings['TPA'].setValue(self.defaultSettingData['Miscellaneous']['TPA'])
        self.miscellaneousSettings['TPA Breakpoint'].setValue(self.defaultSettingData['Miscellaneous']['TPA Breakpoint'])

        # Basic Navigation
        self.basicNavSettings['User Control Mode'].clear()
        self.basicNavSettings['User Control Mode'].addItems(self.defaultSettingData['Basic Nav Settings']['User Control Mode Options'])
        self.basicNavSettings['User Control Mode'].setCurrentIndex(self.defaultSettingData['Basic Nav Settings']['User Control Mode'])
        self.basicNavSettings['Max navigation speed'].setValue(self.defaultSettingData['Basic Nav Settings']['Max navigation speed'])
        self.basicNavSettings['Max cruise speed'].setValue(self.defaultSettingData['Basic Nav Settings']['Max cruise speed'])
        self.basicNavSettings['Max navigation climb rate'].setValue(self.defaultSettingData['Basic Nav Settings']['Max navigation climb rate'])
        self.basicNavSettings['Max ALTHOLD climb rate'].setValue(self.defaultSettingData['Basic Nav Settings']['Max ALTHOLD climb rate'])
        self.basicNavSettings['Multirotor max banking angle'].setValue(self.defaultSettingData['Basic Nav Settings']['Multirotor max banking angle'])
        if self.defaultSettingData['Basic Nav Settings']['Use mid throttle for ALTHOLD'] == True:
            self.basicNavSettings['Use mid throttle for ALTHOLD switch'] = True
            self.basicNavSettings['Use mid throttle for ALTHOLD'].setIcon(QIcon(self.switchONImage))
        elif self.defaultSettingData['Basic Nav Settings']['Use mid throttle for ALTHOLD'] == False:
            self.basicNavSettings['Use mid throttle for ALTHOLD switch'] = False
            self.basicNavSettings['Use mid throttle for ALTHOLD'].setIcon(QIcon(self.switchOFFImage))
        self.basicNavSettings['Hover throttle'].setValue(self.defaultSettingData['Basic Nav Settings']['Hover throttle'])

        # RTH and Landing Settings
        self.rthLandingSettings['RTH Altitude Mode'].clear()
        self.rthLandingSettings['RTH Altitude Mode'].addItems(self.defaultSettingData['RTH and Landing Settings']['RTH Altitude Mode Options'])
        self.rthLandingSettings['RTH Altitude Mode'].setCurrentIndex(self.defaultSettingData['RTH and Landing Settings']['RTH Altitude Mode'])
        self.rthLandingSettings['RTH Altitude'].setValue(self.defaultSettingData['RTH and Landing Settings']['RTH Altitude'])
        if self.defaultSettingData['RTH and Landing Settings']['Climb before RTH'] == True:
            self.rthLandingSettings['Climb before RTH switch'] = True
            self.rthLandingSettings['Climb before RTH'].setIcon(QIcon(self.switchONImage))
        elif self.defaultSettingData['RTH and Landing Settings']['Climb before RTH'] == False:
            self.rthLandingSettings['Climb before RTH switch'] = False
            self.rthLandingSettings['Climb before RTH'].setIcon(QIcon(self.switchOFFImage))
        if self.defaultSettingData['RTH and Landing Settings']['Climb regardless of position sensor health'] == True:
            self.rthLandingSettings['Climb regardless switch'] = True
            self.rthLandingSettings['Climb regardless'].setIcon(QIcon(self.switchONImage))
        elif self.defaultSettingData['RTH and Landing Settings']['Climb regardless of position sensor health'] == False:
            self.rthLandingSettings['Climb regardless switch'] = False
            self.rthLandingSettings['Climb regardless'].setIcon(QIcon(self.switchOFFImage))
        if self.defaultSettingData['RTH and Landing Settings']['Tail first'] == True:
            self.rthLandingSettings['Tail first switch'] = True
            self.rthLandingSettings['Tail first'].setIcon(QIcon(self.switchONImage))
        elif self.defaultSettingData['RTH and Landing Settings']['Tail first'] == False:
            self.rthLandingSettings['Tail first switch'] = False
            self.rthLandingSettings['Tail first'].setIcon(QIcon(self.switchOFFImage))
        self.rthLandingSettings['Land after RTH'].clear()
        self.rthLandingSettings['Land after RTH'].addItems(self.defaultSettingData['RTH and Landing Settings']['Land after RTH Options'])
        self.rthLandingSettings['Land after RTH'].setCurrentIndex(self.defaultSettingData['RTH and Landing Settings']['Land after RTH'])
        self.rthLandingSettings['Landing vertical speed'].setValue(self.defaultSettingData['RTH and Landing Settings']['Landing vertical speed'])
        self.rthLandingSettings['Min vertical landing speed at altitude'].setValue(self.defaultSettingData['RTH and Landing Settings']['Min vertical landing speed at altitude'])
        self.rthLandingSettings['Vertical landing speed slowdown at altitude'].setValue(self.defaultSettingData['RTH and Landing Settings']['Vertical landing speed slowdown at altitude'])
        self.rthLandingSettings['Min RTH distance'].setValue(self.defaultSettingData['RTH and Landing Settings']['Min RTH distance'])
        self.rthLandingSettings['RTH abort threshold'].setValue(self.defaultSettingData['RTH and Landing Settings']['RTH abort threshold'])
        self.rthLandingSettings['Emergency landing speed'].setValue(self.defaultSettingData['RTH and Landing Settings']['Emergency landing speed'])

        # Position Estimator
        self.posEstSettings['Vertical Position Baro Weight'].setValue(self.defaultSettingData['Position Estimator']['Vertical Position Baro Weight'])
        self.posEstSettings['Vertical Position GPS Weight'].setValue(self.defaultSettingData['Position Estimator']['Vertical Position GPS Weight'])
        self.posEstSettings['Vertical Speed GPS Weight'].setValue(self.defaultSettingData['Position Estimator']['Vertical Speed GPS Weight'])
        self.posEstSettings['Horizontal Position GPS Weight'].setValue(self.defaultSettingData['Position Estimator']['Horizontal Position GPS Weight'])
        self.posEstSettings['Horizontal Speed GPS Weight'].setValue(self.defaultSettingData['Position Estimator']['Horizontal Speed GPS Weight'])
        self.posEstSettings['Min GPS sats for valid fix'].setValue(self.defaultSettingData['Position Estimator']['Min GPS sats for valid fix'])
        if self.defaultSettingData['Position Estimator']['Use GPS data for velocity calculation'] == True:
            self.posEstSettings['Use GPS data for velocity calculation switch'] = True
            self.posEstSettings['Use GPS data for velocity calculation'].setIcon(QIcon(self.switchONImage))
        elif self.defaultSettingData['Position Estimator']['Use GPS data for velocity calculation'] == False:
            self.posEstSettings['Use GPS data for velocity calculation switch'] = False
            self.posEstSettings['Use GPS data for velocity calculation'].setIcon(QIcon(self.switchOFFImage))

    def setUIValues(self):
        # PID Tuning
        self.pidTuningSettings['Roll'][0].setValue(self.userSettingData['PID Tuning']['Roll']['P'])
        self.pidTuningSettings['Roll'][1].setValue(self.userSettingData['PID Tuning']['Roll']['I'])
        self.pidTuningSettings['Roll'][2].setValue(self.userSettingData['PID Tuning']['Roll']['D'])
        self.pidTuningSettings['Pitch'][0].setValue(self.userSettingData['PID Tuning']['Pitch']['P'])
        self.pidTuningSettings['Pitch'][1].setValue(self.userSettingData['PID Tuning']['Pitch']['I'])
        self.pidTuningSettings['Pitch'][2].setValue(self.userSettingData['PID Tuning']['Pitch']['D'])
        self.pidTuningSettings['Yaw'][0].setValue(self.userSettingData['PID Tuning']['Yaw']['P'])
        self.pidTuningSettings['Yaw'][1].setValue(self.userSettingData['PID Tuning']['Yaw']['I'])
        self.pidTuningSettings['Yaw'][2].setValue(self.userSettingData['PID Tuning']['Yaw']['D'])
        self.pidTuningSettings['Position Z'][0].setValue(self.userSettingData['PID Tuning']['Position Z']['P'])
        self.pidTuningSettings['Position Z'][1].setValue(self.userSettingData['PID Tuning']['Position Z']['I'])
        self.pidTuningSettings['Position Z'][2].setValue(self.userSettingData['PID Tuning']['Position Z']['D'])
        self.pidTuningSettings['Velocity Z'][0].setValue(self.userSettingData['PID Tuning']['Velocity Z']['P'])
        self.pidTuningSettings['Velocity Z'][1].setValue(self.userSettingData['PID Tuning']['Velocity Z']['I'])
        self.pidTuningSettings['Velocity Z'][2].setValue(self.userSettingData['PID Tuning']['Velocity Z']['D'])
        self.pidTuningSettings['Heading'][0].setValue(self.userSettingData['PID Tuning']['Heading']['P'])
        self.pidTuningSettings['Heading'][1].setValue(self.userSettingData['PID Tuning']['Heading']['I'])
        self.pidTuningSettings['Heading'][2].setValue(self.userSettingData['PID Tuning']['Heading']['D'])
        self.pidTuningSettings['Position XY'][0].setValue(self.userSettingData['PID Tuning']['Position XY']['P'])
        self.pidTuningSettings['Position XY'][1].setValue(self.userSettingData['PID Tuning']['Position XY']['I'])
        self.pidTuningSettings['Position XY'][2].setValue(self.userSettingData['PID Tuning']['Position XY']['D'])
        self.pidTuningSettings['Velocity XY'][0].setValue(self.userSettingData['PID Tuning']['Velocity XY']['P'])
        self.pidTuningSettings['Velocity XY'][1].setValue(self.userSettingData['PID Tuning']['Velocity XY']['I'])
        self.pidTuningSettings['Velocity XY'][2].setValue(self.userSettingData['PID Tuning']['Velocity XY']['D'])
        self.pidTuningSettings['Surface'][0].setValue(self.userSettingData['PID Tuning']['Surface']['P'])
        self.pidTuningSettings['Surface'][1].setValue(self.userSettingData['PID Tuning']['Surface']['I'])
        self.pidTuningSettings['Surface'][2].setValue(self.userSettingData['PID Tuning']['Surface']['D'])
        self.pidTuningSettings['Level'][0].setValue(self.userSettingData['PID Tuning']['Level']['Strength'])
        self.pidTuningSettings['Level'][1].setValue(self.userSettingData['PID Tuning']['Level']['LPF cutoff'])
        self.pidTuningSettings['Level'][2].setValue(self.userSettingData['PID Tuning']['Level']['Transition'])
        self.pidTuningSettings['Roll rate'].setValue(self.userSettingData['PID Tuning']['Roll rate'])
        self.pidTuningSettings['Pitch rate'].setValue(self.userSettingData['PID Tuning']['Pitch rate'])
        self.pidTuningSettings['Yaw rate'].setValue(self.userSettingData['PID Tuning']['Yaw rate'])
        self.pidTuningSettings['Manual Roll rate'].setValue(self.userSettingData['PID Tuning']['Manual Roll rate'])
        self.pidTuningSettings['Manual Pitch rate'].setValue(self.userSettingData['PID Tuning']['Manual Pitch rate'])
        self.pidTuningSettings['Manual Yaw rate'].setValue(self.userSettingData['PID Tuning']['Manual Yaw rate'])
        self.pidTuningSettings['MagHold rate'].setValue(self.userSettingData['PID Tuning']['MagHold rate'])

        # Filtering
        self.filteringSettings['Gyro LPF cutoff frequency'].setValue(self.userSettingData['Filtering']['Gyro LPF cutoff frequency'])
        self.filteringSettings['Accelerometer LPF cutoff frequency'].setValue(self.userSettingData['Filtering']['Accelerometer LPF cutoff frequency'])
        self.filteringSettings['First gyro notch filter frequency'].setValue(self.userSettingData['Filtering']['First gyro notch filter frequency'])
        self.filteringSettings['First gyro notch filter cutoff frequency'].setValue(self.userSettingData['Filtering']['First gyro notch filter cutoff frequency'])
        self.filteringSettings['Second gyro notch filter frequency'].setValue(self.userSettingData['Filtering']['Second gyro notch filter frequency'])
        self.filteringSettings['Second gyro notch filter cutoff frequency'].setValue(self.userSettingData['Filtering']['Second gyro notch filter cutoff frequency'])
        self.filteringSettings['D-term LPF cutoff frequency'].setValue(self.userSettingData['Filtering']['D-term LPF cutoff frequency'])
        self.filteringSettings['Yaw LPF cutoff frequency'].setValue(self.userSettingData['Filtering']['Yaw LPF cutoff frequency'])
        self.filteringSettings['D-term notch filter frequency'].setValue(self.userSettingData['Filtering']['D-term notch filter frequency'])
        self.filteringSettings['D-term notch filter cutoff frequency'].setValue(self.userSettingData['Filtering']['D-term notch filter cutoff frequency'])

        # Miscellaneous
        self.miscellaneousSettings['Yaw jump prevention'].setValue(self.userSettingData['Miscellaneous']['Yaw jump prevention'])
        self.miscellaneousSettings['Yaw P limit'].setValue(self.userSettingData['Miscellaneous']['Yaw P limit'])
        self.miscellaneousSettings['Roll/Pitch I-term ignore rate'].setValue(self.userSettingData['Miscellaneous']['Roll/Pitch I-term ignore rate'])
        self.miscellaneousSettings['Yaw I-term ignore rate'].setValue(self.userSettingData['Miscellaneous']['Yaw I-term ignore rate'])
        self.miscellaneousSettings['Roll/Pitch acceleration limit'].setValue(self.userSettingData['Miscellaneous']['Roll/Pitch acceleration limit'])
        self.miscellaneousSettings['Yaw acceleration limit'].setValue(self.userSettingData['Miscellaneous']['Yaw acceleration limit'])
        self.miscellaneousSettings['TPA'].setValue(self.userSettingData['Miscellaneous']['TPA'])
        self.miscellaneousSettings['TPA Breakpoint'].setValue(self.userSettingData['Miscellaneous']['TPA Breakpoint'])

        # Basic Navigation
        self.basicNavSettings['User Control Mode'].clear()
        self.basicNavSettings['User Control Mode'].addItems(self.userSettingData['Basic Nav Settings']['User Control Mode Options'])
        self.basicNavSettings['User Control Mode'].setCurrentIndex(self.userSettingData['Basic Nav Settings']['User Control Mode'])
        self.basicNavSettings['Max navigation speed'].setValue(self.userSettingData['Basic Nav Settings']['Max navigation speed'])
        self.basicNavSettings['Max cruise speed'].setValue(self.userSettingData['Basic Nav Settings']['Max cruise speed'])
        self.basicNavSettings['Max navigation climb rate'].setValue(self.userSettingData['Basic Nav Settings']['Max navigation climb rate'])
        self.basicNavSettings['Max ALTHOLD climb rate'].setValue(self.userSettingData['Basic Nav Settings']['Max ALTHOLD climb rate'])
        self.basicNavSettings['Multirotor max banking angle'].setValue(self.userSettingData['Basic Nav Settings']['Multirotor max banking angle'])
        if self.userSettingData['Basic Nav Settings']['Use mid throttle for ALTHOLD'] == True:
            self.basicNavSettings['Use mid throttle for ALTHOLD switch'] = True
            self.basicNavSettings['Use mid throttle for ALTHOLD'].setIcon(QIcon(self.switchONImage))
        elif self.userSettingData['Basic Nav Settings']['Use mid throttle for ALTHOLD'] == False:
            self.basicNavSettings['Use mid throttle for ALTHOLD switch'] = False
            self.basicNavSettings['Use mid throttle for ALTHOLD'].setIcon(QIcon(self.switchOFFImage))
        self.basicNavSettings['Hover throttle'].setValue(self.userSettingData['Basic Nav Settings']['Hover throttle'])

        # RTH and Landing Settings
        self.rthLandingSettings['RTH Altitude Mode'].clear()
        self.rthLandingSettings['RTH Altitude Mode'].addItems(self.userSettingData['RTH and Landing Settings']['RTH Altitude Mode Options'])
        self.rthLandingSettings['RTH Altitude Mode'].setCurrentIndex(self.userSettingData['RTH and Landing Settings']['RTH Altitude Mode'])
        self.rthLandingSettings['RTH Altitude'].setValue(self.userSettingData['RTH and Landing Settings']['RTH Altitude'])
        if self.userSettingData['RTH and Landing Settings']['Climb before RTH'] == True:
            self.rthLandingSettings['Climb before RTH switch'] = True
            self.rthLandingSettings['Climb before RTH'].setIcon(QIcon(self.switchONImage))
        elif self.userSettingData['RTH and Landing Settings']['Climb before RTH'] == False:
            self.rthLandingSettings['Climb before RTH switch'] = False
            self.rthLandingSettings['Climb before RTH'].setIcon(QIcon(self.switchOFFImage))
        if self.userSettingData['RTH and Landing Settings']['Climb regardless of position sensor health'] == True:
            self.rthLandingSettings['Climb regardless switch'] = True
            self.rthLandingSettings['Climb regardless'].setIcon(QIcon(self.switchONImage))
        elif self.userSettingData['RTH and Landing Settings']['Climb regardless of position sensor health'] == False:
            self.rthLandingSettings['Climb regardless switch'] = False
            self.rthLandingSettings['Climb regardless'].setIcon(QIcon(self.switchOFFImage))
        if self.userSettingData['RTH and Landing Settings']['Tail first'] == True:
            self.rthLandingSettings['Tail first switch'] = True
            self.rthLandingSettings['Tail first'].setIcon(QIcon(self.switchONImage))
        elif self.userSettingData['RTH and Landing Settings']['Tail first'] == False:
            self.rthLandingSettings['Tail first switch'] = False
            self.rthLandingSettings['Tail first'].setIcon(QIcon(self.switchOFFImage))
        self.rthLandingSettings['Land after RTH'].clear()
        self.rthLandingSettings['Land after RTH'].addItems(self.userSettingData['RTH and Landing Settings']['Land after RTH Options'])
        self.rthLandingSettings['Land after RTH'].setCurrentIndex(self.userSettingData['RTH and Landing Settings']['Land after RTH'])
        self.rthLandingSettings['Landing vertical speed'].setValue(self.userSettingData['RTH and Landing Settings']['Landing vertical speed'])
        self.rthLandingSettings['Min vertical landing speed at altitude'].setValue(self.userSettingData['RTH and Landing Settings']['Min vertical landing speed at altitude'])
        self.rthLandingSettings['Vertical landing speed slowdown at altitude'].setValue(self.userSettingData['RTH and Landing Settings']['Vertical landing speed slowdown at altitude'])
        self.rthLandingSettings['Min RTH distance'].setValue(self.userSettingData['RTH and Landing Settings']['Min RTH distance'])
        self.rthLandingSettings['RTH abort threshold'].setValue(self.userSettingData['RTH and Landing Settings']['RTH abort threshold'])
        self.rthLandingSettings['Emergency landing speed'].setValue(self.userSettingData['RTH and Landing Settings']['Emergency landing speed'])

        # Position Estimator
        self.posEstSettings['Vertical Position Baro Weight'].setValue(self.userSettingData['Position Estimator']['Vertical Position Baro Weight'])
        self.posEstSettings['Vertical Position GPS Weight'].setValue(self.userSettingData['Position Estimator']['Vertical Position GPS Weight'])
        self.posEstSettings['Vertical Speed GPS Weight'].setValue(self.userSettingData['Position Estimator']['Vertical Speed GPS Weight'])
        self.posEstSettings['Horizontal Position GPS Weight'].setValue(self.userSettingData['Position Estimator']['Horizontal Position GPS Weight'])
        self.posEstSettings['Horizontal Speed GPS Weight'].setValue(self.userSettingData['Position Estimator']['Horizontal Speed GPS Weight'])
        self.posEstSettings['Min GPS sats for valid fix'].setValue(self.userSettingData['Position Estimator']['Min GPS sats for valid fix'])
        if self.userSettingData['Position Estimator']['Use GPS data for velocity calculation'] == True:
            self.posEstSettings['Use GPS data for velocity calculation switch'] = True
            self.posEstSettings['Use GPS data for velocity calculation'].setIcon(QIcon(self.switchONImage))
        elif self.userSettingData['Position Estimator']['Use GPS data for velocity calculation'] == False:
            self.posEstSettings['Use GPS data for velocity calculation switch'] = False
            self.posEstSettings['Use GPS data for velocity calculation'].setIcon(QIcon(self.switchOFFImage))

    def saveandreboot(self):
        # Get values from UI: UI->userSettingData
        self.getUIValues()
        # userSettingData->qsObj
        self.setQSObj()
        # qsObj->Board write with MSP
        tbsList = []
        self.parameterSaveSignal.emit(tbsList)
        # Save EEPROM
        # Reboot
        pass

    # Read widget values and set self.userSettingData: UI->userSettingData
    def getUIValues(self):
        # PID Tuning
        self.userSettingData['PID Tuning']['Roll']['P'] = self.pidTuningSettings['Roll'][0].value()
        self.userSettingData['PID Tuning']['Roll']['I'] = self.pidTuningSettings['Roll'][1].value()
        self.userSettingData['PID Tuning']['Roll']['D'] = self.pidTuningSettings['Roll'][2].value()
        self.userSettingData['PID Tuning']['Pitch']['P'] = self.pidTuningSettings['Pitch'][0].value()
        self.userSettingData['PID Tuning']['Pitch']['I'] = self.pidTuningSettings['Pitch'][1].value()
        self.userSettingData['PID Tuning']['Pitch']['D'] = self.pidTuningSettings['Pitch'][2].value()
        self.userSettingData['PID Tuning']['Yaw']['P'] = self.pidTuningSettings['Yaw'][0].value()
        self.userSettingData['PID Tuning']['Yaw']['I'] = self.pidTuningSettings['Yaw'][1].value()
        self.userSettingData['PID Tuning']['Yaw']['D'] = self.pidTuningSettings['Yaw'][2].value()
        self.userSettingData['PID Tuning']['Position Z']['P'] = self.pidTuningSettings['Position Z'][0].value()
        self.userSettingData['PID Tuning']['Position Z']['I'] = self.pidTuningSettings['Position Z'][1].value()
        self.userSettingData['PID Tuning']['Position Z']['D'] = self.pidTuningSettings['Position Z'][2].value()
        self.userSettingData['PID Tuning']['Velocity Z']['P'] = self.pidTuningSettings['Velocity Z'][0].value()
        self.userSettingData['PID Tuning']['Velocity Z']['I'] = self.pidTuningSettings['Velocity Z'][1].value()
        self.userSettingData['PID Tuning']['Velocity Z']['D'] = self.pidTuningSettings['Velocity Z'][2].value()
        self.userSettingData['PID Tuning']['Heading']['P'] = self.pidTuningSettings['Heading'][0].value()
        self.userSettingData['PID Tuning']['Heading']['I'] = self.pidTuningSettings['Heading'][1].value()
        self.userSettingData['PID Tuning']['Heading']['D'] = self.pidTuningSettings['Heading'][2].value()
        self.userSettingData['PID Tuning']['Position XY']['P'] = self.pidTuningSettings['Position XY'][0].value()
        self.userSettingData['PID Tuning']['Position XY']['I'] = self.pidTuningSettings['Position XY'][1].value()
        self.userSettingData['PID Tuning']['Position XY']['D'] = self.pidTuningSettings['Position XY'][2].value()
        self.userSettingData['PID Tuning']['Velocity XY']['P'] = self.pidTuningSettings['Velocity XY'][0].value()
        self.userSettingData['PID Tuning']['Velocity XY']['I'] = self.pidTuningSettings['Velocity XY'][1].value()
        self.userSettingData['PID Tuning']['Velocity XY']['D'] = self.pidTuningSettings['Velocity XY'][2].value()
        self.userSettingData['PID Tuning']['Surface']['P'] = self.pidTuningSettings['Surface'][0].value()
        self.userSettingData['PID Tuning']['Surface']['I'] = self.pidTuningSettings['Surface'][1].value()
        self.userSettingData['PID Tuning']['Surface']['D'] = self.pidTuningSettings['Surface'][2].value()
        self.userSettingData['PID Tuning']['Level']['Strength'] = self.pidTuningSettings['Level'][0].value()
        self.userSettingData['PID Tuning']['Level']['LPF cutoff'] = self.pidTuningSettings['Level'][1].value()
        self.userSettingData['PID Tuning']['Level']['Transition'] = self.pidTuningSettings['Level'][2].value()
        self.userSettingData['PID Tuning']['Roll rate'] = self.pidTuningSettings['Roll rate'].value()
        self.userSettingData['PID Tuning']['Pitch rate'] = self.pidTuningSettings['Pitch rate'].value()
        self.userSettingData['PID Tuning']['Yaw rate'] = self.pidTuningSettings['Yaw rate'].value()
        self.userSettingData['PID Tuning']['Manual Roll rate'] = self.pidTuningSettings['Manual Roll rate'].value()
        self.userSettingData['PID Tuning']['Manual Pitch rate'] = self.pidTuningSettings['Manual Pitch rate'].value()
        self.userSettingData['PID Tuning']['Manual Yaw rate'] = self.pidTuningSettings['Manual Yaw rate'].value()
        self.userSettingData['PID Tuning']['MagHold rate'] = self.pidTuningSettings['MagHold rate'].value()

        # Filtering
        self.userSettingData['Filtering']['Gyro LPF cutoff frequency'] = self.filteringSettings['Gyro LPF cutoff frequency'].value()
        self.userSettingData['Filtering']['Accelerometer LPF cutoff frequency'] = self.filteringSettings['Accelerometer LPF cutoff frequency'].value()
        self.userSettingData['Filtering']['First gyro notch filter frequency'] = self.filteringSettings['First gyro notch filter frequency'].value()
        self.userSettingData['Filtering']['First gyro notch filter cutoff frequency'] = self.filteringSettings['First gyro notch filter cutoff frequency'].value()
        self.userSettingData['Filtering']['Second gyro notch filter frequency'] = self.filteringSettings['Second gyro notch filter frequency'].value()
        self.userSettingData['Filtering']['Second gyro notch filter cutoff frequency'] = self.filteringSettings['Second gyro notch filter cutoff frequency'].value()
        self.userSettingData['Filtering']['D-term LPF cutoff frequency'] = self.filteringSettings['D-term LPF cutoff frequency'].value()
        self.userSettingData['Filtering']['Yaw LPF cutoff frequency'] = self.filteringSettings['Yaw LPF cutoff frequency'].value()
        self.userSettingData['Filtering']['D-term notch filter frequency'] = self.filteringSettings['D-term notch filter frequency'].value()
        self.userSettingData['Filtering']['D-term notch filter cutoff frequency'] = self.filteringSettings['D-term notch filter cutoff frequency'].value()

        # Miscellaneous
        self.userSettingData['Miscellaneous']['Yaw jump prevention'] = self.miscellaneousSettings['Yaw jump prevention'].value()
        self.userSettingData['Miscellaneous']['Yaw P limit'] = self.miscellaneousSettings['Yaw P limit'].value()
        self.userSettingData['Miscellaneous']['Roll/Pitch I-term ignore rate'] = self.miscellaneousSettings['Roll/Pitch I-term ignore rate'].value()
        self.userSettingData['Miscellaneous']['Yaw I-term ignore rate'] = self.miscellaneousSettings['Yaw I-term ignore rate'].value()
        self.userSettingData['Miscellaneous']['Roll/Pitch acceleration limit'] = self.miscellaneousSettings['Roll/Pitch acceleration limit'].value()
        self.userSettingData['Miscellaneous']['Yaw acceleration limit'] = self.miscellaneousSettings['Yaw acceleration limit'].value()
        self.userSettingData['Miscellaneous']['TPA'] = self.miscellaneousSettings['TPA'].value()
        self.userSettingData['Miscellaneous']['TPA Breakpoint'] = self.miscellaneousSettings['TPA Breakpoint'].value()

        # Basic Navigation
        self.userSettingData['Basic Nav Settings']['User Control Mode'] = self.basicNavSettings['User Control Mode'].currentIndex()
        self.userSettingData['Basic Nav Settings']['Max navigation speed'] = self.basicNavSettings['Max navigation speed'].value()
        self.userSettingData['Basic Nav Settings']['Max cruise speed'] = self.basicNavSettings['Max cruise speed'].value()
        self.userSettingData['Basic Nav Settings']['Max navigation climb rate'] = self.basicNavSettings['Max navigation climb rate'].value()
        self.userSettingData['Basic Nav Settings']['Max ALTHOLD climb rate'] = self.basicNavSettings['Max ALTHOLD climb rate'].value()
        self.userSettingData['Basic Nav Settings']['Multirotor max banking angle'] = self.basicNavSettings['Multirotor max banking angle'].value()
        self.userSettingData['Basic Nav Settings']['Use mid throttle for ALTHOLD'] = self.basicNavSettings['Use mid throttle for ALTHOLD switch']
        self.userSettingData['Basic Nav Settings']['Hover throttle'] = self.basicNavSettings['Hover throttle'].value()

        # RTH and Landing Settings
        self.userSettingData['RTH and Landing Settings']['RTH Altitude Mode'] = self.rthLandingSettings['RTH Altitude Mode'].currentIndex()
        self.userSettingData['RTH and Landing Settings']['RTH Altitude'] = self.rthLandingSettings['RTH Altitude'].value()
        self.userSettingData['RTH and Landing Settings']['Climb before RTH'] = self.rthLandingSettings['Climb before RTH switch']
        self.userSettingData['RTH and Landing Settings']['Climb regardless of position sensor health'] = self.rthLandingSettings['Climb regardless switch']
        self.userSettingData['RTH and Landing Settings']['Tail first'] = self.rthLandingSettings['Tail first switch']
        self.userSettingData['RTH and Landing Settings']['Land after RTH'] = self.rthLandingSettings['Land after RTH'].currentIndex()
        self.userSettingData['RTH and Landing Settings']['Landing vertical speed'] = self.rthLandingSettings['Landing vertical speed'].value()
        self.userSettingData['RTH and Landing Settings']['Min vertical landing speed at altitude'] = self.rthLandingSettings['Min vertical landing speed at altitude'].value()
        self.userSettingData['RTH and Landing Settings']['Vertical landing speed slowdown at altitude'] = self.rthLandingSettings['Vertical landing speed slowdown at altitude'].value()
        self.userSettingData['RTH and Landing Settings']['Min RTH distance'] = self.rthLandingSettings['Min RTH distance'].value()
        self.userSettingData['RTH and Landing Settings']['RTH abort threshold'] = self.rthLandingSettings['RTH abort threshold'].value()
        self.userSettingData['RTH and Landing Settings']['Emergency landing speed'] = self.rthLandingSettings['Emergency landing speed'].value()

        # Position Estimator
        self.userSettingData['Position Estimator']['Vertical Position Baro Weight'] = self.posEstSettings['Vertical Position Baro Weight'].value()
        self.userSettingData['Position Estimator']['Vertical Position GPS Weight'] = self.posEstSettings['Vertical Position GPS Weight'].value()
        self.userSettingData['Position Estimator']['Vertical Speed GPS Weight'] = self.posEstSettings['Vertical Speed GPS Weight'].value()
        self.userSettingData['Position Estimator']['Horizontal Position GPS Weight'] = self.posEstSettings['Horizontal Position GPS Weight'].value()
        self.userSettingData['Position Estimator']['Horizontal Speed GPS Weight'] = self.posEstSettings['Horizontal Speed GPS Weight'].value()
        self.userSettingData['Position Estimator']['Min GPS sats for valid fix'] = self.posEstSettings['Min GPS sats for valid fix'].value()
        self.userSettingData['Position Estimator']['Use GPS data for velocity calculation'] = self.posEstSettings['Use GPS data for velocity calculation switch']

    def pidTuningGroupBoxInit(self):
        self.pidTuningSettings = {}
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Name"), 0, 0, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Proportional"), 0, 1, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Integral"), 0, 2, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Derivative"), 0, 3, 1, 1)

        self.pidTuningGroupBoxLayout.addWidget(QLabel("Basic/Acro"), 1, 0, 1, 4)

        self.pidTuningSettings['Roll'] = [QSpinBox(), QSpinBox(), QSpinBox()]
        for i in range(len(self.pidTuningSettings['Roll'])):
            self.pidTuningSettings['Roll'][i].setRange(0,200)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Roll"), 2, 0, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Roll'][0], 2, 1, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Roll'][1], 2, 2, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Roll'][2], 2, 3, 1, 1)

        self.pidTuningSettings['Pitch'] = [QSpinBox(), QSpinBox(), QSpinBox()]
        for i in range(len(self.pidTuningSettings['Pitch'])):
            self.pidTuningSettings['Pitch'][i].setRange(0,200)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Pitch"), 3, 0, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Pitch'][0], 3, 1, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Pitch'][1], 3, 2, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Pitch'][2], 3, 3, 1, 1)

        self.pidTuningSettings['Yaw'] = [QSpinBox(), QSpinBox(), QSpinBox()]
        for i in range(len(self.pidTuningSettings['Yaw'])):
            self.pidTuningSettings['Yaw'][i].setRange(0,200)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Yaw"), 4, 0, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Yaw'][0], 4, 1, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Yaw'][1], 4, 2, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Yaw'][2], 4, 3, 1, 1)

        self.pidTuningGroupBoxLayout.addWidget(QLabel("Barometer & Sonar/Altitude"), 5, 0, 1, 4)
        self.pidTuningSettings['Position Z'] = [QSpinBox(), QSpinBox(), QSpinBox()]
        for i in range(len(self.pidTuningSettings['Position Z'])):
            self.pidTuningSettings['Position Z'][i].setRange(0,200)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Position Z"), 6, 0, 1, 4)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Position Z'][0], 6, 1, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Position Z'][1], 6, 2, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Position Z'][2], 6, 3, 1, 1)

        self.pidTuningSettings['Velocity Z'] = [QSpinBox(), QSpinBox(), QSpinBox()]
        for i in range(len(self.pidTuningSettings['Velocity Z'])):
            self.pidTuningSettings['Velocity Z'][i].setRange(0,200)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Velocity Z"), 7, 0, 1, 4)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Velocity Z'][0], 7, 1, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Velocity Z'][1], 7, 2, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Velocity Z'][2], 7, 3, 1, 1)

        self.pidTuningGroupBoxLayout.addWidget(QLabel("Magnetometer/Heading"), 8, 0, 1, 4)
        self.pidTuningSettings['Heading'] = [QSpinBox(), QSpinBox(), QSpinBox()]
        for i in range(len(self.pidTuningSettings['Heading'])):
            self.pidTuningSettings['Heading'][i].setRange(0,200)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Heading"), 9, 0, 1, 4)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Heading'][0], 9, 1, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Heading'][1], 9, 2, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Heading'][2], 9, 3, 1, 1)

        self.pidTuningGroupBoxLayout.addWidget(QLabel("GPS Navigation"), 10, 0, 1, 4)
        self.pidTuningSettings['Position XY'] = [QSpinBox(), QSpinBox(), QSpinBox()]
        for i in range(len(self.pidTuningSettings['Position XY'])):
            self.pidTuningSettings['Position XY'][i].setRange(0,200)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Position XY"), 11, 0, 1, 4)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Position XY'][0], 11, 1, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Position XY'][1], 11, 2, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Position XY'][2], 11, 3, 1, 1)

        self.pidTuningSettings['Velocity XY'] = [QSpinBox(), QSpinBox(), QSpinBox()]
        for i in range(len(self.pidTuningSettings['Velocity XY'])):
            self.pidTuningSettings['Velocity XY'][i].setRange(0,200)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Velocity XY"), 12, 0, 1, 4)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Velocity XY'][0], 12, 1, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Velocity XY'][1], 12, 2, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Velocity XY'][2], 12, 3, 1, 1)

        self.pidTuningSettings['Surface'] = [QSpinBox(), QSpinBox(), QSpinBox()]
        for i in range(len(self.pidTuningSettings['Surface'])):
            self.pidTuningSettings['Surface'][i].setRange(0,200)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Surface"), 13, 0, 1, 4)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Surface'][0], 13, 1, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Surface'][1], 13, 2, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Surface'][2], 13, 3, 1, 1)

        self.pidTuningGroupBoxLayout.addWidget(QWidget(), 14, 0, 1, 4)

        self.pidTuningGroupBoxLayout.addWidget(QLabel("Angle/Horizon"), 15, 0, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Strength"), 15, 1, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("LPF cutoff (Hz)"), 15, 2, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Transition (Horizon)"), 15, 3, 1, 1)
        self.pidTuningSettings['Level'] = [QSpinBox(), QSpinBox(), QSpinBox()]
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Level"), 16, 0, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Level'][0], 16, 1, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Level'][1], 16, 2, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Level'][2], 16, 3, 1, 1)

        self.pidTuningGroupBoxLayout.addWidget(QWidget(), 17, 0, 1, 4)

        self.pidTuningSettings['Roll rate'] = QSpinBox()
        self.pidTuningSettings['Roll rate'].setRange(0,1000)
        self.pidTuningSettings['Roll rate'].setSingleStep(10)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Roll Rate"), 18, 0, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Roll rate'], 18, 1, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("degrees per second"), 18, 2, 1, 1)

        self.pidTuningSettings['Pitch rate'] = QSpinBox()
        self.pidTuningSettings['Pitch rate'].setRange(0,1000)
        self.pidTuningSettings['Pitch rate'].setSingleStep(10)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Pitch Rate"), 19, 0, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Pitch rate'], 19, 1, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("degrees per second"), 19, 2, 1, 1)

        self.pidTuningSettings['Yaw rate'] = QSpinBox()
        self.pidTuningSettings['Yaw rate'].setRange(0,1000)
        self.pidTuningSettings['Yaw rate'].setSingleStep(10)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Yaw Rate"), 20, 0, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Yaw rate'], 20, 1, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("degrees per second"), 20, 2, 1, 1)

        self.pidTuningSettings['Manual Roll rate'] = QSpinBox()
        self.pidTuningSettings['Manual Roll rate'].setRange(0,100)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Manual Roll Rate"), 21, 0, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Manual Roll rate'], 21, 1, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("%"), 21, 2, 1, 1)

        self.pidTuningSettings['Manual Pitch rate'] = QSpinBox()
        self.pidTuningSettings['Manual Pitch rate'].setRange(0,100)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Manual Pitch Rate"), 22, 0, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Manual Pitch rate'], 22, 1, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("%"), 22, 2, 1, 1)

        self.pidTuningSettings['Manual Yaw rate'] = QSpinBox()
        self.pidTuningSettings['Manual Yaw rate'].setRange(0,100)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("Manual Yaw Rate"), 23, 0, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['Manual Yaw rate'], 23, 1, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("%"), 23, 2, 1, 1)

        self.pidTuningSettings['MagHold rate'] = QSpinBox()
        self.pidTuningSettings['MagHold rate'].setRange(0,1000)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("MagHold Rate"), 24, 0, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(self.pidTuningSettings['MagHold rate'], 24, 1, 1, 1)
        self.pidTuningGroupBoxLayout.addWidget(QLabel("degrees per second"), 24, 2, 1, 1)

    def filteringGroupBoxInit(self):
        self.filteringSettings = {}

        self.filteringGroupBoxLayout.addWidget(QLabel("Gyro LPF cutoff frequency"), 0, 0, 1, 2)
        self.filteringSettings['Gyro LPF cutoff frequency'] = QSpinBox()
        self.filteringGroupBoxLayout.addWidget(self.filteringSettings['Gyro LPF cutoff frequency'], 0, 2, 1, 1)
        self.filteringGroupBoxLayout.addWidget(QLabel("Hz"), 0, 3, 1, 1)

        self.filteringGroupBoxLayout.addWidget(QLabel("Accelerometer LPF cutoff frequency"), 1, 0, 1, 2)
        self.filteringSettings['Accelerometer LPF cutoff frequency'] = QSpinBox()
        self.filteringGroupBoxLayout.addWidget(self.filteringSettings['Accelerometer LPF cutoff frequency'], 1, 2, 1, 1)
        self.filteringGroupBoxLayout.addWidget(QLabel("Hz"), 1, 3, 1, 1)

        self.filteringGroupBoxLayout.addWidget(QLabel("First gyro notch filter frequency"), 2, 0, 1, 2)
        self.filteringSettings['First gyro notch filter frequency'] = QSpinBox()
        self.filteringGroupBoxLayout.addWidget(self.filteringSettings['First gyro notch filter frequency'], 2, 2, 1, 1)
        self.filteringGroupBoxLayout.addWidget(QLabel("Hz"), 2, 3, 1, 1)

        self.filteringGroupBoxLayout.addWidget(QLabel("First gyro notch filter cutoff frequency"), 3, 0, 1, 2)
        self.filteringSettings['First gyro notch filter cutoff frequency'] = QSpinBox()
        self.filteringGroupBoxLayout.addWidget(self.filteringSettings['First gyro notch filter cutoff frequency'], 3, 2, 1, 1)
        self.filteringGroupBoxLayout.addWidget(QLabel("Hz"), 3, 3, 1, 1)

        self.filteringGroupBoxLayout.addWidget(QLabel("Second gyro notch filter frequency"), 4, 0, 1, 2)
        self.filteringSettings['Second gyro notch filter frequency'] = QSpinBox()
        self.filteringGroupBoxLayout.addWidget(self.filteringSettings['Second gyro notch filter frequency'], 4, 2, 1, 1)
        self.filteringGroupBoxLayout.addWidget(QLabel("Hz"), 4, 3, 1, 1)

        self.filteringGroupBoxLayout.addWidget(QLabel("Second gyro notch filter cutoff frequency"), 5, 0, 1, 2)
        self.filteringSettings['Second gyro notch filter cutoff frequency'] = QSpinBox()
        self.filteringGroupBoxLayout.addWidget(self.filteringSettings['Second gyro notch filter cutoff frequency'], 5, 2, 1, 1)
        self.filteringGroupBoxLayout.addWidget(QLabel("Hz"), 5, 3, 1, 1)

        self.filteringGroupBoxLayout.addWidget(QLabel("D-term LPF cutoff frequency"), 6, 0, 1, 2)
        self.filteringSettings['D-term LPF cutoff frequency'] = QSpinBox()
        self.filteringGroupBoxLayout.addWidget(self.filteringSettings['D-term LPF cutoff frequency'], 6, 2, 1, 1)
        self.filteringGroupBoxLayout.addWidget(QLabel("Hz"), 6, 3, 1, 1)

        self.filteringGroupBoxLayout.addWidget(QLabel("Yaw LPF cutoff frequency"), 7, 0, 1, 2)
        self.filteringSettings['Yaw LPF cutoff frequency'] = QSpinBox()
        self.filteringGroupBoxLayout.addWidget(self.filteringSettings['Yaw LPF cutoff frequency'], 7, 2, 1, 1)
        self.filteringGroupBoxLayout.addWidget(QLabel("Hz"), 7, 3, 1, 1)

        self.filteringGroupBoxLayout.addWidget(QLabel("D-term notch filter frequency"), 8, 0, 1, 2)
        self.filteringSettings['D-term notch filter frequency'] = QSpinBox()
        self.filteringGroupBoxLayout.addWidget(self.filteringSettings['D-term notch filter frequency'], 8, 2, 1, 1)
        self.filteringGroupBoxLayout.addWidget(QLabel("Hz"), 8, 3, 1, 1)

        self.filteringGroupBoxLayout.addWidget(QLabel("D-term notch filter cutoff frequency"), 9, 0, 1, 2)
        self.filteringSettings['D-term notch filter cutoff frequency'] = QSpinBox()
        self.filteringGroupBoxLayout.addWidget(self.filteringSettings['D-term notch filter cutoff frequency'], 9, 2, 1, 1)
        self.filteringGroupBoxLayout.addWidget(QLabel("Hz"), 9, 3, 1, 1)

    def miscellaneousGroupBoxInit(self):
        self.miscellaneousSettings = {}
        self.miscellaneousGroupBoxLayout.addWidget(QLabel("Yaw jump prevention"), 0, 0, 1, 2)
        self.miscellaneousSettings['Yaw jump prevention'] = QSpinBox()
        self.miscellaneousSettings['Yaw jump prevention'].setRange(0,400)
        self.miscellaneousGroupBoxLayout.addWidget(self.miscellaneousSettings['Yaw jump prevention'], 0, 2, 1, 1)
        self.miscellaneousGroupBoxLayout.addWidget(QLabel(" "), 0, 3, 1, 1)

        self.miscellaneousGroupBoxLayout.addWidget(QLabel("Yaw P limit"), 1, 0, 1, 2)
        self.miscellaneousSettings['Yaw P limit'] = QSpinBox()
        self.miscellaneousSettings['Yaw P limit'].setRange(0,1000)
        self.miscellaneousGroupBoxLayout.addWidget(self.miscellaneousSettings['Yaw P limit'], 1, 2, 1, 1)
        self.miscellaneousGroupBoxLayout.addWidget(QLabel(" "), 1, 3, 1, 1)

        self.miscellaneousGroupBoxLayout.addWidget(QLabel("Roll/Pitch I-term ignore rate"), 2, 0, 1, 2)
        self.miscellaneousSettings['Roll/Pitch I-term ignore rate'] = QSpinBox()
        self.miscellaneousSettings['Roll/Pitch I-term ignore rate'].setRange(0,1000)
        self.miscellaneousGroupBoxLayout.addWidget(self.miscellaneousSettings['Roll/Pitch I-term ignore rate'], 2, 2, 1, 1)
        self.miscellaneousGroupBoxLayout.addWidget(QLabel(" "), 2, 3, 1, 1)

        self.miscellaneousGroupBoxLayout.addWidget(QLabel("Yaw I-term ignore rate"), 3, 0, 1, 2)
        self.miscellaneousSettings['Yaw I-term ignore rate'] = QSpinBox()
        self.miscellaneousSettings['Yaw I-term ignore rate'].setRange(0,100)
        self.miscellaneousGroupBoxLayout.addWidget(self.miscellaneousSettings['Yaw I-term ignore rate'], 3, 2, 1, 1)
        self.miscellaneousGroupBoxLayout.addWidget(QLabel(" "), 3, 3, 1, 1)

        self.miscellaneousGroupBoxLayout.addWidget(QLabel("Roll/Pitch acceleration limit"), 4, 0, 1, 2)
        self.miscellaneousSettings['Roll/Pitch acceleration limit'] = QSpinBox()
        self.miscellaneousSettings['Roll/Pitch acceleration limit'].setRange(0,10000)
        self.miscellaneousGroupBoxLayout.addWidget(self.miscellaneousSettings['Roll/Pitch acceleration limit'], 4, 2, 1, 1)
        self.miscellaneousGroupBoxLayout.addWidget(QLabel("dps^2"), 4, 3, 1, 1)

        self.miscellaneousGroupBoxLayout.addWidget(QLabel("Yaw acceleration limit"), 5, 0, 1, 2)
        self.miscellaneousSettings['Yaw acceleration limit'] = QSpinBox()
        self.miscellaneousSettings['Yaw acceleration limit'].setRange(0,10000)
        self.miscellaneousGroupBoxLayout.addWidget(self.miscellaneousSettings['Yaw acceleration limit'], 5, 2, 1, 1)
        self.miscellaneousGroupBoxLayout.addWidget(QLabel("dps^2"), 5, 3, 1, 1)

        self.miscellaneousGroupBoxLayout.addWidget(QLabel("TPA"), 6, 0, 1, 2)
        self.miscellaneousSettings['TPA'] = QSpinBox()
        self.miscellaneousGroupBoxLayout.addWidget(self.miscellaneousSettings['TPA'], 6, 2, 1, 1)
        self.miscellaneousGroupBoxLayout.addWidget(QLabel("%"), 6, 3, 1, 1)

        self.miscellaneousGroupBoxLayout.addWidget(QLabel("TPA Breakpoint"), 7, 0, 1, 2)
        self.miscellaneousSettings['TPA Breakpoint'] = QSpinBox()
        self.miscellaneousSettings['TPA Breakpoint'].setRange(900,2100)
        self.miscellaneousGroupBoxLayout.addWidget(self.miscellaneousSettings['TPA Breakpoint'], 7, 2, 1, 1)
        self.miscellaneousGroupBoxLayout.addWidget(QLabel(" "), 7, 3, 1, 1)

    def basicNavSettingGroupBoxInit(self):
        self.basicNavSettings = {}

        self.basicNavSettings['User Control Mode'] = QComboBox()
        self.basicNavSettingGroupBoxLayout.addWidget(self.basicNavSettings['User Control Mode'], 0, 0, 1, 1)
        self.basicNavSettingGroupBoxLayout.addWidget(QLabel("User Control Mode"), 0, 1, 1, 2)

        self.basicNavSettings['Max navigation speed'] = QSpinBox()
        self.basicNavSettings['Max navigation speed'].setRange(0,1000)
        self.basicNavSettingGroupBoxLayout.addWidget(self.basicNavSettings['Max navigation speed'], 1, 0, 1, 1)
        self.basicNavSettingGroupBoxLayout.addWidget(QLabel("Max navigation speed [cm/s]"), 1, 1, 1, 2)

        self.basicNavSettings['Max cruise speed'] = QSpinBox()
        self.basicNavSettings['Max cruise speed'].setRange(0,1000)
        self.basicNavSettingGroupBoxLayout.addWidget(self.basicNavSettings['Max cruise speed'], 2, 0, 1, 1)
        self.basicNavSettingGroupBoxLayout.addWidget(QLabel("Max cruise speed [cm/s]"), 2, 1, 1, 2)

        self.basicNavSettings['Max navigation climb rate'] = QSpinBox()
        self.basicNavSettings['Max navigation climb rate'].setRange(0,1000)
        self.basicNavSettingGroupBoxLayout.addWidget(self.basicNavSettings['Max navigation climb rate'], 3, 0, 1, 1)
        self.basicNavSettingGroupBoxLayout.addWidget(QLabel("Max navigation climb rate [cm/s]"), 3, 1, 1, 2)

        self.basicNavSettings['Max ALTHOLD climb rate'] = QSpinBox()
        self.basicNavSettings['Max ALTHOLD climb rate'].setRange(0,1000)
        self.basicNavSettingGroupBoxLayout.addWidget(self.basicNavSettings['Max ALTHOLD climb rate'], 4, 0, 1, 1)
        self.basicNavSettingGroupBoxLayout.addWidget(QLabel("Max ALTHOLD climb rate [cm/s]"), 4, 1, 1, 2)

        self.basicNavSettings['Multirotor max banking angle'] = QSpinBox()
        self.basicNavSettings['Multirotor max banking angle'].setRange(0,50)
        self.basicNavSettingGroupBoxLayout.addWidget(self.basicNavSettings['Multirotor max banking angle'], 5, 0, 1, 1)
        self.basicNavSettingGroupBoxLayout.addWidget(QLabel("Multirotor max banking angle [deg]"), 5, 1, 1, 2)

        self.basicNavSettings['Use mid throttle for ALTHOLD'] = QPushButton(QIcon(self.switchOFFImage), None, self)
        self.basicNavSettings['Use mid throttle for ALTHOLD'].setIconSize(QSize(39,18))
        self.basicNavSettings['Use mid throttle for ALTHOLD'].setStyleSheet("QPushButton {border: none;}")
        self.basicNavSettings['Use mid throttle for ALTHOLD switch'] = False
        self.basicNavSettings['Use mid throttle for ALTHOLD'].clicked.connect(self.useMidThrottleSwitchClicked)
        self.basicNavSettingGroupBoxLayout.addWidget(self.basicNavSettings['Use mid throttle for ALTHOLD'], 6, 0, 1, 1)
        self.basicNavSettingGroupBoxLayout.addWidget(QLabel("Use mid throttle for ALTHOLD"), 6, 1, 1, 2)

        self.basicNavSettings['Hover throttle'] = QSpinBox()
        self.basicNavSettings['Hover throttle'].setRange(0,1700)
        self.basicNavSettingGroupBoxLayout.addWidget(self.basicNavSettings['Hover throttle'], 7, 0, 1, 1)
        self.basicNavSettingGroupBoxLayout.addWidget(QLabel("Hover throttle"), 7, 1, 1, 2)

    def rthLandingSettingGroupBoxInit(self):
        self.rthLandingSettings = {}
        self.rthLandingSettings['RTH Altitude Mode'] = QComboBox()
        self.rthLandingSettingGroupBoxLayout.addWidget(self.rthLandingSettings['RTH Altitude Mode'], 0, 0, 1, 1)
        self.rthLandingSettingGroupBoxLayout.addWidget(QLabel("RTH Altitude Mode"), 0, 1, 1, 2)

        self.rthLandingSettings['RTH Altitude'] = QSpinBox()
        self.rthLandingSettings['RTH Altitude'].setRange(0,10000)
        self.rthLandingSettingGroupBoxLayout.addWidget(self.rthLandingSettings['RTH Altitude'], 1, 0, 1, 1)
        self.rthLandingSettingGroupBoxLayout.addWidget(QLabel("RTH Altitude [cm]"), 1, 1, 1, 2)

        self.rthLandingSettings['Climb before RTH'] = QPushButton(QIcon(self.switchOFFImage), None, self)
        self.rthLandingSettings['Climb before RTH'].setIconSize(QSize(39,18))
        self.rthLandingSettings['Climb before RTH'].setStyleSheet("QPushButton {border: none;}")
        self.rthLandingSettings['Climb before RTH switch'] = False
        self.rthLandingSettings['Climb before RTH'].clicked.connect(self.climbBeforeRTHSwitchClicked)
        self.rthLandingSettingGroupBoxLayout.addWidget(self.rthLandingSettings['Climb before RTH'], 2, 0, 1, 1)
        self.rthLandingSettingGroupBoxLayout.addWidget(QLabel("Climb before RTH"), 2, 1, 1, 2)

        self.rthLandingSettings['Climb regardless'] = QPushButton(QIcon(self.switchOFFImage), None, self)
        self.rthLandingSettings['Climb regardless'].setIconSize(QSize(39,18))
        self.rthLandingSettings['Climb regardless'].setStyleSheet("QPushButton {border: none;}")
        self.rthLandingSettings['Climb regardless switch'] = False
        self.rthLandingSettings['Climb regardless'].clicked.connect(self.climbRegardlessSwitchClicked)
        self.rthLandingSettingGroupBoxLayout.addWidget(self.rthLandingSettings['Climb regardless'], 3, 0, 1, 1)
        self.rthLandingSettingGroupBoxLayout.addWidget(QLabel("Climb regardless of position sensor health"), 3, 1, 1, 2)

        self.rthLandingSettings['Tail first'] = QPushButton(QIcon(self.switchOFFImage), None, self)
        self.rthLandingSettings['Tail first'].setIconSize(QSize(39,18))
        self.rthLandingSettings['Tail first'].setStyleSheet("QPushButton {border: none;}")
        self.rthLandingSettings['Tail first switch'] = False
        self.rthLandingSettings['Tail first'].clicked.connect(self.tailFirstSwitchClicked)
        self.rthLandingSettingGroupBoxLayout.addWidget(self.rthLandingSettings['Tail first'], 4, 0, 1, 1)
        self.rthLandingSettingGroupBoxLayout.addWidget(QLabel("Tail first"), 4, 1, 1, 2)

        self.rthLandingSettings['Land after RTH'] = QComboBox()
        self.rthLandingSettingGroupBoxLayout.addWidget(self.rthLandingSettings['Land after RTH'], 5, 0, 1, 1)
        self.rthLandingSettingGroupBoxLayout.addWidget(QLabel("Land After RTH"), 5, 1, 1, 2)

        self.rthLandingSettings['Landing vertical speed'] = QSpinBox()
        self.rthLandingSettings['Landing vertical speed'].setRange(0,1000)
        self.rthLandingSettingGroupBoxLayout.addWidget(self.rthLandingSettings['Landing vertical speed'], 6, 0, 1, 1)
        self.rthLandingSettingGroupBoxLayout.addWidget(QLabel("Landing Vertical Speed [cm/s]"), 6, 1, 1, 2)

        self.rthLandingSettings['Min vertical landing speed at altitude'] = QSpinBox()
        self.rthLandingSettings['Min vertical landing speed at altitude'].setRange(0,1000)
        self.rthLandingSettingGroupBoxLayout.addWidget(self.rthLandingSettings['Min vertical landing speed at altitude'], 7, 0, 1, 1)
        self.rthLandingSettingGroupBoxLayout.addWidget(QLabel("Min Vertical Landing speed at altitude [cm]"), 7, 1, 1, 2)

        self.rthLandingSettings['Vertical landing speed slowdown at altitude'] = QSpinBox()
        self.rthLandingSettings['Vertical landing speed slowdown at altitude'].setRange(0,10000)
        self.rthLandingSettingGroupBoxLayout.addWidget(self.rthLandingSettings['Vertical landing speed slowdown at altitude'], 8, 0, 1, 1)
        self.rthLandingSettingGroupBoxLayout.addWidget(QLabel("Vertical landing speeds slowdown at altitude [cm]"), 8, 1, 1, 2)

        self.rthLandingSettings['Min RTH distance'] = QSpinBox()
        self.rthLandingSettings['Min RTH distance'].setRange(0,1000)
        self.rthLandingSettingGroupBoxLayout.addWidget(self.rthLandingSettings['Min RTH distance'], 9, 0, 1, 1)
        self.rthLandingSettingGroupBoxLayout.addWidget(QLabel("Min RTH distance [cm]"), 9, 1, 1, 2)

        self.rthLandingSettings['RTH abort threshold'] = QSpinBox()
        self.rthLandingSettings['RTH abort threshold'].setRange(0,100000)
        self.rthLandingSettingGroupBoxLayout.addWidget(self.rthLandingSettings['RTH abort threshold'], 10, 0, 1, 1)
        self.rthLandingSettingGroupBoxLayout.addWidget(QLabel("RTH abort threshold [cm]"), 10, 1, 1, 2)

        self.rthLandingSettings['Emergency landing speed'] = QSpinBox()
        self.rthLandingSettings['Emergency landing speed'].setRange(0,1000)
        self.rthLandingSettingGroupBoxLayout.addWidget(self.rthLandingSettings['Emergency landing speed'], 11, 0, 1, 1)
        self.rthLandingSettingGroupBoxLayout.addWidget(QLabel("Emergency landing speed [cm]"), 11, 1, 1, 2)

    def posEstGroupBoxInit(self):
        self.posEstSettings = {}
        self.posEstSettings['Vertical Position Baro Weight'] = QDoubleSpinBox()
        self.posEstSettings['Vertical Position Baro Weight'].setDecimals(2)
        self.posEstGroupBoxLayout.addWidget(self.posEstSettings['Vertical Position Baro Weight'], 0, 0, 1, 1)
        self.posEstGroupBoxLayout.addWidget(QLabel("Vertical Position Baro Weight"), 0, 1, 1, 2)

        self.posEstSettings['Vertical Position GPS Weight'] = QDoubleSpinBox()
        self.posEstSettings['Vertical Position GPS Weight'].setDecimals(2)
        self.posEstGroupBoxLayout.addWidget(self.posEstSettings['Vertical Position GPS Weight'], 1, 0, 1, 1)
        self.posEstGroupBoxLayout.addWidget(QLabel("Vertical Position GPS Weight"), 1, 1, 1, 2)

        self.posEstSettings['Vertical Speed GPS Weight'] = QDoubleSpinBox()
        self.posEstSettings['Vertical Speed GPS Weight'].setDecimals(2)
        self.posEstGroupBoxLayout.addWidget(self.posEstSettings['Vertical Speed GPS Weight'], 2, 0, 1, 1)
        self.posEstGroupBoxLayout.addWidget(QLabel("Vertical Speed GPS Weight"), 2, 1, 1, 2)

        self.posEstSettings['Horizontal Position GPS Weight'] = QDoubleSpinBox()
        self.posEstSettings['Horizontal Position GPS Weight'].setDecimals(2)
        self.posEstGroupBoxLayout.addWidget(self.posEstSettings['Horizontal Position GPS Weight'], 3, 0, 1, 1)
        self.posEstGroupBoxLayout.addWidget(QLabel("Horizontal Position GPS Weight"), 3, 1, 1, 2)

        self.posEstSettings['Horizontal Speed GPS Weight'] = QDoubleSpinBox()
        self.posEstSettings['Horizontal Speed GPS Weight'].setDecimals(2)
        self.posEstGroupBoxLayout.addWidget(self.posEstSettings['Horizontal Speed GPS Weight'], 4, 0, 1, 1)
        self.posEstGroupBoxLayout.addWidget(QLabel("Horizontal Speed GPS Weight"), 4, 1, 1, 2)

        self.posEstSettings['Min GPS sats for valid fix'] = QSpinBox()
        self.posEstSettings['Min GPS sats for valid fix'].setRange(0,100)
        self.posEstGroupBoxLayout.addWidget(self.posEstSettings['Min GPS sats for valid fix'], 5, 0, 1, 1)
        self.posEstGroupBoxLayout.addWidget(QLabel("Min GPS sats for valid fix"), 5, 1, 1, 2)

        self.posEstSettings['Use GPS data for velocity calculation'] = QPushButton(QIcon(self.switchOFFImage), None, self)
        self.posEstSettings['Use GPS data for velocity calculation'].setIconSize(QSize(39,18))
        self.posEstSettings['Use GPS data for velocity calculation'].setStyleSheet("QPushButton {border: none;}")
        self.posEstSettings['Use GPS data for velocity calculation switch'] = False
        self.posEstSettings['Use GPS data for velocity calculation'].clicked.connect(self.useGPSSwitchClicked)
        self.posEstGroupBoxLayout.addWidget(self.posEstSettings['Use GPS data for velocity calculation'], 6, 0, 1, 1)
        self.posEstGroupBoxLayout.addWidget(QLabel("Use GPS data for velocity calculation"), 6, 1, 1, 2)

    def useMidThrottleSwitchClicked(self):
        if self.basicNavSettings['Use mid throttle for ALTHOLD switch'] == False:
            self.basicNavSettings['Use mid throttle for ALTHOLD'].setIcon(QIcon(self.switchONImage))
            self.basicNavSettings['Use mid throttle for ALTHOLD switch'] = True
        elif self.basicNavSettings['Use mid throttle for ALTHOLD switch'] == True:
            self.basicNavSettings['Use mid throttle for ALTHOLD'].setIcon(QIcon(self.switchOFFImage))
            self.basicNavSettings['Use mid throttle for ALTHOLD switch'] = False

    def climbBeforeRTHSwitchClicked(self):
        if self.rthLandingSettings['Climb before RTH switch'] == False:
            self.rthLandingSettings['Climb before RTH'].setIcon(QIcon(self.switchONImage))
            self.rthLandingSettings['Climb before RTH switch'] = True
        elif self.rthLandingSettings['Climb before RTH switch'] == True:
            self.rthLandingSettings['Climb before RTH'].setIcon(QIcon(self.switchOFFImage))
            self.rthLandingSettings['Climb before RTH switch'] = False

    def climbRegardlessSwitchClicked(self):
        if self.rthLandingSettings['Climb regardless switch'] == False:
            self.rthLandingSettings['Climb regardless'].setIcon(QIcon(self.switchONImage))
            self.rthLandingSettings['Climb regardless switch'] = True
        elif self.rthLandingSettings['Climb regardless switch'] == True:
            self.rthLandingSettings['Climb regardless'].setIcon(QIcon(self.switchOFFImage))
            self.rthLandingSettings['Climb regardless switch'] = False

    def tailFirstSwitchClicked(self):
        if self.rthLandingSettings['Tail first switch'] == False:
            self.rthLandingSettings['Tail first'].setIcon(QIcon(self.switchONImage))
            self.rthLandingSettings['Tail first switch'] = True
        elif self.rthLandingSettings['Tail first switch'] == True:
            self.rthLandingSettings['Tail first'].setIcon(QIcon(self.switchOFFImage))
            self.rthLandingSettings['Tail first switch'] = False

    def useGPSSwitchClicked(self):
        if self.posEstSettings['Use GPS data for velocity calculation switch'] == False:
            self.posEstSettings['Use GPS data for velocity calculation'].setIcon(QIcon(self.switchONImage))
            self.posEstSettings['Use GPS data for velocity calculation switch'] = True
        elif self.posEstSettings['Use GPS data for velocity calculation switch'] == True:
            self.posEstSettings['Use GPS data for velocity calculation'].setIcon(QIcon(self.switchOFFImage))
            self.posEstSettings['Use GPS data for velocity calculation switch'] = False

    def loadValuesFromDefault(self):
        self.defaultSettingData = readDefaultSettingFile()

    def loadValuesFromUserSaved(self):
        self.userSettingData = readUserSettingFile()

    def loadValuesFromBoard(self):
        pass

    # Transfer values from qsObj to userSettingData
    def setValues(self):
        # PID Tuning
        for i in range(len(self.qsObj.msp_pidnames)):
            tempName = self.qsObj.msp_pidnames[i]
            if tempName == 'ROLL':
                self.userSettingData['PID Tuning']['Roll']['P'] = self.qsObj.msp_pid[3*i]
                self.userSettingData['PID Tuning']['Roll']['I'] = self.qsObj.msp_pid[3*i+1]
                self.userSettingData['PID Tuning']['Roll']['D'] = self.qsObj.msp_pid[3*i+2]
            elif tempName == 'PITCH':
                self.userSettingData['PID Tuning']['Pitch']['P'] = self.qsObj.msp_pid[3*i]
                self.userSettingData['PID Tuning']['Pitch']['I'] = self.qsObj.msp_pid[3*i+1]
                self.userSettingData['PID Tuning']['Pitch']['D'] = self.qsObj.msp_pid[3*i+2]
            elif tempName == 'YAW':
                self.userSettingData['PID Tuning']['Yaw']['P'] = self.qsObj.msp_pid[3*i]
                self.userSettingData['PID Tuning']['Yaw']['I'] = self.qsObj.msp_pid[3*i+1]
                self.userSettingData['PID Tuning']['Yaw']['D'] = self.qsObj.msp_pid[3*i+2]
            elif tempName == 'ALT':
                self.userSettingData['PID Tuning']['Position Z']['P'] = self.qsObj.msp_pid[3*i]
                self.userSettingData['PID Tuning']['Position Z']['I'] = self.qsObj.msp_pid[3*i+1]
                self.userSettingData['PID Tuning']['Position Z']['D'] = self.qsObj.msp_pid[3*i+2]
            elif tempName == 'Pos':
                self.userSettingData['PID Tuning']['Position XY']['P'] = self.qsObj.msp_pid[3*i]
                self.userSettingData['PID Tuning']['Position XY']['I'] = self.qsObj.msp_pid[3*i+1]
                self.userSettingData['PID Tuning']['Position XY']['D'] = self.qsObj.msp_pid[3*i+2]
            elif tempName == 'PosR':
                self.userSettingData['PID Tuning']['Velocity XY']['P'] = self.qsObj.msp_pid[3*i]
                self.userSettingData['PID Tuning']['Velocity XY']['I'] = self.qsObj.msp_pid[3*i+1]
                self.userSettingData['PID Tuning']['Velocity XY']['D'] = self.qsObj.msp_pid[3*i+2]
            elif tempName == 'NavR':
                self.userSettingData['PID Tuning']['Surface']['P'] = self.qsObj.msp_pid[3*i]
                self.userSettingData['PID Tuning']['Surface']['I'] = self.qsObj.msp_pid[3*i+1]
                self.userSettingData['PID Tuning']['Surface']['D'] = self.qsObj.msp_pid[3*i+2]
            elif tempName == 'LEVEL':
                self.userSettingData['PID Tuning']['Level']['Strength'] = self.qsObj.msp_pid[3*i]
                self.userSettingData['PID Tuning']['Level']['LPF cutoff'] = self.qsObj.msp_pid[3*i+1]
                self.userSettingData['PID Tuning']['Level']['Transition'] = self.qsObj.msp_pid[3*i+2]
            elif tempName == 'MAG':
                self.userSettingData['PID Tuning']['Heading']['P'] = self.qsObj.msp_pid[3*i]
                self.userSettingData['PID Tuning']['Heading']['I'] = self.qsObj.msp_pid[3*i+1]
                self.userSettingData['PID Tuning']['Heading']['D'] = self.qsObj.msp_pid[3*i+2]
            elif tempName == 'VEL':
                self.userSettingData['PID Tuning']['Velocity Z']['P'] = self.qsObj.msp_pid[3*i]
                self.userSettingData['PID Tuning']['Velocity Z']['I'] = self.qsObj.msp_pid[3*i+1]
                self.userSettingData['PID Tuning']['Velocity Z']['D'] = self.qsObj.msp_pid[3*i+2]
        self.userSettingData['PID Tuning']['Roll rate'] = self.qsObj.msp_rc_tuning['roll_rate']*10
        self.userSettingData['PID Tuning']['Pitch rate'] = self.qsObj.msp_rc_tuning['pitch_rate']*10
        self.userSettingData['PID Tuning']['Yaw rate'] = self.qsObj.msp_rc_tuning['yaw_rate']*10
        self.userSettingData['PID Tuning']['MagHold rate'] = self.qsObj.msp_inav_pid['heading_hold_rate_limit']
        # self.userSettingData['PID Tuning']['Manual Roll rate']
        # self.userSettingData['PID Tuning']['Manual Pitch rate']
        # self.userSettingData['PID Tuning']['Manual Yaw rate']

        # Filtering
        self.userSettingData['Filtering']['Gyro LPF cutoff frequency'] = self.qsObj.msp_filter_config['gyro_soft_lpf_hz']
        self.userSettingData['Filtering']['Accelerometer LPF cutoff frequency'] = self.qsObj.msp_inav_pid['acc_soft_lpf_hz']
        self.userSettingData['Filtering']['First gyro notch filter frequency'] = self.qsObj.msp_filter_config['gyro_soft_notch_hz_1']
        self.userSettingData['Filtering']['First gyro notch filter cutoff frequency'] = self.qsObj.msp_filter_config['gyro_soft_notch_cutoff_1']
        self.userSettingData['Filtering']['Second gyro notch filter frequency'] = self.qsObj.msp_filter_config['gyro_soft_notch_hz_2']
        self.userSettingData['Filtering']['Second gyro notch filter cutoff frequency'] = self.qsObj.msp_filter_config['gyro_soft_notch_cutoff_2']
        self.userSettingData['Filtering']['D-term LPF cutoff frequency'] = self.qsObj.msp_filter_config['dterm_lpf_hz']
        self.userSettingData['Filtering']['Yaw LPF cutoff frequency'] = self.qsObj.msp_filter_config['yaw_lpf_hz']
        self.userSettingData['Filtering']['D-term notch filter frequency'] = self.qsObj.msp_filter_config['dterm_soft_notch_hz']
        self.userSettingData['Filtering']['D-term notch filter cutoff frequency'] = self.qsObj.msp_filter_config['dterm_soft_notch_cutoff']
        #
        # Miscellaneous
        self.userSettingData['Miscellaneous']['Yaw jump prevention'] = self.qsObj.msp_inav_pid['yaw_jump_prevention_limit']
        self.userSettingData['Miscellaneous']['Yaw P limit'] = self.qsObj.msp_pid_advanced['yaw_p_limit']
        self.userSettingData['Miscellaneous']['Roll/Pitch I-term ignore rate'] = self.qsObj.msp_pid_advanced['roll_pitch_i_term_ignore_rate']
        self.userSettingData['Miscellaneous']['Yaw I-term ignore rate'] = self.qsObj.msp_pid_advanced['yaw_i_term_ignore_rate']
        self.userSettingData['Miscellaneous']['Roll/Pitch acceleration limit'] = self.qsObj.msp_pid_advanced['axis_acceleration_limit_roll_pitch']
        self.userSettingData['Miscellaneous']['Yaw acceleration limit'] = self.qsObj.msp_pid_advanced['axis_acceleration_limit_yaw']*10
        self.userSettingData['Miscellaneous']['TPA'] = self.qsObj.msp_rc_tuning['throttle_dyn_pid']
        self.userSettingData['Miscellaneous']['TPA Breakpoint']= self.qsObj.msp_rc_tuning['throttle_pa_breakpoint']
        #
        # Basic Navigation
        self.userSettingData['Basic Nav Settings']['User Control Mode'] = self.qsObj.msp_nav_poshold['user_control_mode']
        self.userSettingData['Basic Nav Settings']['Max navigation speed'] = self.qsObj.msp_nav_poshold['max_auto_speed']
        self.userSettingData['Basic Nav Settings']['Max cruise speed'] = self.qsObj.msp_nav_poshold['max_manual_speed']
        self.userSettingData['Basic Nav Settings']['Max navigation climb rate'] = self.qsObj.msp_nav_poshold['max_auto_climb_rate']
        self.userSettingData['Basic Nav Settings']['Max ALTHOLD climb rate'] = self.qsObj.msp_nav_poshold['max_manual_climb_rate']
        self.userSettingData['Basic Nav Settings']['Multirotor max banking angle'] = self.qsObj.msp_nav_poshold['mc_max_bank_angle']
        if self.qsObj.msp_nav_poshold['use_thr_mid_for_althold'] == 1:
            self.userSettingData['Basic Nav Settings']['Use mid throttle for ALTHOLD'] = True
        elif self.qsObj.msp_nav_poshold['use_thr_mid_for_althold'] == 0:
            self.userSettingData['Basic Nav Settings']['Use mid throttle for ALTHOLD'] = False
        self.userSettingData['Basic Nav Settings']['Hover throttle'] = self.qsObj.msp_nav_poshold['mc_hover_throttle']

        # RTH and Landing Settings
        self.userSettingData['RTH and Landing Settings']['RTH Altitude Mode'] = self.qsObj.msp_rth_and_land_config['rth_alt_control_mode']
        self.userSettingData['RTH and Landing Settings']['RTH Altitude'] = self.qsObj.msp_rth_and_land_config['rth_altitude']
        if self.qsObj.msp_rth_and_land_config['rth_climb_first'] == 1:
            self.userSettingData['RTH and Landing Settings']['Climb before RTH'] = True
        elif self.qsObj.msp_rth_and_land_config['rth_climb_first'] == 0:
            self.userSettingData['RTH and Landing Settings']['Climb before RTH'] = False
        if self.qsObj.msp_rth_and_land_config['rth_climb_ignore_emerg'] == 1:
            self.userSettingData['RTH and Landing Settings']['Climb regardless of position sensor health'] = True
        elif self.qsObj.msp_rth_and_land_config['rth_climb_ignore_emerg'] == 0:
            self.userSettingData['RTH and Landing Settings']['Climb regardless of position sensor health'] = False
        if self.qsObj.msp_rth_and_land_config['rth_tail_first'] == 1:
            self.userSettingData['RTH and Landing Settings']['Tail first'] = True
        elif self.qsObj.msp_rth_and_land_config['rth_tail_first'] == 0:
            self.userSettingData['RTH and Landing Settings']['Tail first'] = False
        self.userSettingData['RTH and Landing Settings']['Land after RTH'] = self.qsObj.msp_rth_and_land_config['rth_allow_landing']
        self.userSettingData['RTH and Landing Settings']['Landing vertical speed'] = self.qsObj.msp_rth_and_land_config['land_descent_rate']
        self.userSettingData['RTH and Landing Settings']['Min vertical landing speed at altitude'] = self.qsObj.msp_rth_and_land_config['land_slowdown_minalt']
        self.userSettingData['RTH and Landing Settings']['Vertical landing speed slowdown at altitude'] = self.qsObj.msp_rth_and_land_config['land_slowdown_maxalt']
        self.userSettingData['RTH and Landing Settings']['Min RTH distance'] = self.qsObj.msp_rth_and_land_config['min_rth_distance']
        self.userSettingData['RTH and Landing Settings']['RTH abort threshold'] = self.qsObj.msp_rth_and_land_config['rth_abort_threshold']
        self.userSettingData['RTH and Landing Settings']['Emergency landing speed'] = self.qsObj.msp_rth_and_land_config['emerg_descent_rate']

        # Position Estimator
        self.userSettingData['Position Estimator']['Vertical Position Baro Weight'] = self.qsObj.msp_position_estimation_config['w_z_baro_p']/100.0
        self.userSettingData['Position Estimator']['Vertical Position GPS Weight'] = self.qsObj.msp_position_estimation_config['w_z_gps_p']/100.0
        self.userSettingData['Position Estimator']['Vertical Speed GPS Weight'] = self.qsObj.msp_position_estimation_config['w_z_gps_v']/100.0
        self.userSettingData['Position Estimator']['Horizontal Position GPS Weight'] = self.qsObj.msp_position_estimation_config['w_xy_gps_p']/100.0
        self.userSettingData['Position Estimator']['Horizontal Speed GPS Weight'] = self.qsObj.msp_position_estimation_config['w_xy_gps_v']/100.0
        self.userSettingData['Position Estimator']['Min GPS sats for valid fix'] = self.qsObj.msp_position_estimation_config['gps_min_sats']
        if self.qsObj.msp_position_estimation_config['use_gps_velned'] == 1:
            self.userSettingData['Position Estimator']['Use GPS data for velocity calculation'] = True
        elif self.qsObj.msp_position_estimation_config['use_gps_velned'] == 0:
            self.userSettingData['Position Estimator']['Use GPS data for velocity calculation'] = False
        # Update UI values
        self.setUIValues()

    # Transfer userSettingData to qsObj
    def setQSObj(self):
        # userSettingData->qsObj
        # PID Tuning
        self.qsObj.msp_pidnames = ['ROLL', 'PITCH', 'YAW', 'ALT', 'Pos', 'PosR', 'NavR', 'LEVEL', 'MAG', 'VEL']
        for i in range(len(self.qsObj.msp_pidnames)):
            tempName = self.qsObj.msp_pidnames[i]
            if tempName == 'ROLL':
                self.qsObj.msp_pid[3*i] = self.userSettingData['PID Tuning']['Roll']['P']
                self.qsObj.msp_pid[3*i+1] = self.userSettingData['PID Tuning']['Roll']['I']
                self.qsObj.msp_pid[3*i+2] = self.userSettingData['PID Tuning']['Roll']['D']
            elif tempName == 'PITCH':
                self.qsObj.msp_pid[3*i] = self.userSettingData['PID Tuning']['Pitch']['P']
                self.qsObj.msp_pid[3*i+1] = self.userSettingData['PID Tuning']['Pitch']['I']
                self.qsObj.msp_pid[3*i+2] = self.userSettingData['PID Tuning']['Pitch']['D']
            elif tempName == 'YAW':
                self.qsObj.msp_pid[3*i] = self.userSettingData['PID Tuning']['Yaw']['P']
                self.qsObj.msp_pid[3*i+1] = self.userSettingData['PID Tuning']['Yaw']['I']
                self.qsObj.msp_pid[3*i+2] = self.userSettingData['PID Tuning']['Yaw']['D']
            elif tempName == 'ALT':
                self.qsObj.msp_pid[3*i] = self.userSettingData['PID Tuning']['Position Z']['P']
                self.qsObj.msp_pid[3*i+1] = self.userSettingData['PID Tuning']['Position Z']['I']
                self.qsObj.msp_pid[3*i+2] = self.userSettingData['PID Tuning']['Position Z']['D']
            elif tempName == 'Pos':
                self.qsObj.msp_pid[3*i] = self.userSettingData['PID Tuning']['Position XY']['P']
                self.qsObj.msp_pid[3*i+1] = self.userSettingData['PID Tuning']['Position XY']['I']
                self.qsObj.msp_pid[3*i+2] = self.userSettingData['PID Tuning']['Position XY']['D']
            elif tempName == 'PosR':
                self.qsObj.msp_pid[3*i] = self.userSettingData['PID Tuning']['Velocity XY']['P']
                self.qsObj.msp_pid[3*i+1] = self.userSettingData['PID Tuning']['Velocity XY']['I']
                self.qsObj.msp_pid[3*i+2] = self.userSettingData['PID Tuning']['Velocity XY']['D']
            elif tempName == 'NavR':
                self.qsObj.msp_pid[3*i] = self.userSettingData['PID Tuning']['Surface']['P']
                self.qsObj.msp_pid[3*i+1] = self.userSettingData['PID Tuning']['Surface']['I']
                self.qsObj.msp_pid[3*i+2] = self.userSettingData['PID Tuning']['Surface']['D']
            elif tempName == 'LEVEL':
                self.qsObj.msp_pid[3*i] = self.userSettingData['PID Tuning']['Level']['Strength']
                self.qsObj.msp_pid[3*i+1] = self.userSettingData['PID Tuning']['Level']['LPF cutoff']
                self.qsObj.msp_pid[3*i+2] = self.userSettingData['PID Tuning']['Level']['Transition']
            elif tempName == 'MAG':
                self.qsObj.msp_pid[3*i] = self.userSettingData['PID Tuning']['Heading']['P']
                self.qsObj.msp_pid[3*i+1] = self.userSettingData['PID Tuning']['Heading']['I']
                self.qsObj.msp_pid[3*i+2] = self.userSettingData['PID Tuning']['Heading']['D']
            elif tempName == 'VEL':
                self.qsObj.msp_pid[3*i] = self.userSettingData['PID Tuning']['Velocity Z']['P']
                self.qsObj.msp_pid[3*i+1] = self.userSettingData['PID Tuning']['Velocity Z']['I']
                self.qsObj.msp_pid[3*i+2] = self.userSettingData['PID Tuning']['Velocity Z']['D']
        self.qsObj.msp_rc_tuning['roll_rate'] = int(self.userSettingData['PID Tuning']['Roll rate']/10.0)
        self.qsObj.msp_rc_tuning['pitch_rate'] = int(self.userSettingData['PID Tuning']['Pitch rate']/10.0)
        self.qsObj.msp_rc_tuning['yaw_rate'] = int(self.userSettingData['PID Tuning']['Yaw rate']/10.0)
        self.qsObj.msp_inav_pid['heading_hold_rate_limit'] = self.userSettingData['PID Tuning']['MagHold rate']
        # self.userSettingData['PID Tuning']['Manual Roll rate']
        # self.userSettingData['PID Tuning']['Manual Pitch rate']
        # self.userSettingData['PID Tuning']['Manual Yaw rate']

        # Filtering
        self.qsObj.msp_filter_config['gyro_soft_lpf_hz'] = self.userSettingData['Filtering']['Gyro LPF cutoff frequency']
        self.qsObj.msp_inav_pid['acc_soft_lpf_hz'] = self.userSettingData['Filtering']['Accelerometer LPF cutoff frequency']
        self.qsObj.msp_filter_config['gyro_soft_notch_hz_1'] = self.userSettingData['Filtering']['First gyro notch filter frequency']
        self.qsObj.msp_filter_config['gyro_soft_notch_cutoff_1'] = self.userSettingData['Filtering']['First gyro notch filter cutoff frequency']
        self.qsObj.msp_filter_config['gyro_soft_notch_hz_2'] = self.userSettingData['Filtering']['Second gyro notch filter frequency']
        self.qsObj.msp_filter_config['gyro_soft_notch_cutoff_2'] = self.userSettingData['Filtering']['Second gyro notch filter cutoff frequency']
        self.qsObj.msp_filter_config['dterm_lpf_hz'] = self.userSettingData['Filtering']['D-term LPF cutoff frequency']
        self.qsObj.msp_filter_config['yaw_lpf_hz'] = self.userSettingData['Filtering']['Yaw LPF cutoff frequency']
        self.qsObj.msp_filter_config['dterm_soft_notch_hz'] = self.userSettingData['Filtering']['D-term notch filter frequency']
        self.qsObj.msp_filter_config['dterm_soft_notch_cutoff'] = self.userSettingData['Filtering']['D-term notch filter cutoff frequency']

        # Miscellaneous
        self.qsObj.msp_inav_pid['yaw_jump_prevention_limit'] = self.userSettingData['Miscellaneous']['Yaw jump prevention']
        self.qsObj.msp_pid_advanced['yaw_p_limit'] = self.userSettingData['Miscellaneous']['Yaw P limit']
        self.qsObj.msp_pid_advanced['roll_pitch_i_term_ignore_rate'] = self.userSettingData['Miscellaneous']['Roll/Pitch I-term ignore rate']
        self.qsObj.msp_pid_advanced['yaw_i_term_ignore_rate'] = self.userSettingData['Miscellaneous']['Yaw I-term ignore rate']
        self.qsObj.msp_pid_advanced['axis_acceleration_limit_roll_pitch'] = self.userSettingData['Miscellaneous']['Roll/Pitch acceleration limit']
        self.qsObj.msp_pid_advanced['axis_acceleration_limit_yaw'] = int(self.userSettingData['Miscellaneous']['Yaw acceleration limit']/10.0)
        self.qsObj.msp_rc_tuning['throttle_dyn_pid'] = self.userSettingData['Miscellaneous']['TPA']
        self.qsObj.msp_rc_tuning['throttle_pa_breakpoint'] = self.userSettingData['Miscellaneous']['TPA Breakpoint']

        # Basic Navigation
        self.qsObj.msp_nav_poshold['user_control_mode'] = self.userSettingData['Basic Nav Settings']['User Control Mode']
        self.qsObj.msp_nav_poshold['max_auto_speed'] = self.userSettingData['Basic Nav Settings']['Max navigation speed']
        self.qsObj.msp_nav_poshold['max_manual_speed'] = self.userSettingData['Basic Nav Settings']['Max cruise speed']
        self.qsObj.msp_nav_poshold['max_auto_climb_rate'] = self.userSettingData['Basic Nav Settings']['Max navigation climb rate']
        self.qsObj.msp_nav_poshold['max_manual_climb_rate'] = self.userSettingData['Basic Nav Settings']['Max ALTHOLD climb rate']
        self.qsObj.msp_nav_poshold['mc_max_bank_angle'] = self.userSettingData['Basic Nav Settings']['Multirotor max banking angle']
        if self.userSettingData['Basic Nav Settings']['Use mid throttle for ALTHOLD'] == True:
            self.qsObj.msp_nav_poshold['use_thr_mid_for_althold'] = 1
        elif self.userSettingData['Basic Nav Settings']['Use mid throttle for ALTHOLD'] == False:
            self.qsObj.msp_nav_poshold['use_thr_mid_for_althold'] = 0
        self.qsObj.msp_nav_poshold['mc_hover_throttle'] = self.userSettingData['Basic Nav Settings']['Hover throttle']

        # RTH and Landing Settings
        self.qsObj.msp_rth_and_land_config['rth_alt_control_mode'] = self.userSettingData['RTH and Landing Settings']['RTH Altitude Mode']
        self.qsObj.msp_rth_and_land_config['rth_altitude'] = self.userSettingData['RTH and Landing Settings']['RTH Altitude']
        if self.userSettingData['RTH and Landing Settings']['Climb before RTH'] == True:
            self.qsObj.msp_rth_and_land_config['rth_climb_first'] = 1
        elif self.userSettingData['RTH and Landing Settings']['Climb before RTH'] == False:
            self.qsObj.msp_rth_and_land_config['rth_climb_first'] = 0
        if self.userSettingData['RTH and Landing Settings']['Climb regardless of position sensor health'] == True:
            self.qsObj.msp_rth_and_land_config['rth_climb_ignore_emerg'] = 1
        elif self.userSettingData['RTH and Landing Settings']['Climb regardless of position sensor health'] == False:
            self.qsObj.msp_rth_and_land_config['rth_climb_ignore_emerg'] = 0
        if self.userSettingData['RTH and Landing Settings']['Tail first'] == True:
            self.qsObj.msp_rth_and_land_config['rth_tail_first'] = 1
        elif self.userSettingData['RTH and Landing Settings']['Tail first'] == False:
            self.qsObj.msp_rth_and_land_config['rth_tail_first'] = 0
        self.qsObj.msp_rth_and_land_config['rth_allow_landing'] = self.userSettingData['RTH and Landing Settings']['Land after RTH']
        self.qsObj.msp_rth_and_land_config['land_descent_rate'] = self.userSettingData['RTH and Landing Settings']['Landing vertical speed']
        self.qsObj.msp_rth_and_land_config['land_slowdown_minalt'] = self.userSettingData['RTH and Landing Settings']['Min vertical landing speed at altitude']
        self.qsObj.msp_rth_and_land_config['land_slowdown_maxalt'] = self.userSettingData['RTH and Landing Settings']['Vertical landing speed slowdown at altitude']
        self.qsObj.msp_rth_and_land_config['min_rth_distance'] = self.userSettingData['RTH and Landing Settings']['Min RTH distance']
        self.qsObj.msp_rth_and_land_config['rth_abort_threshold'] = self.userSettingData['RTH and Landing Settings']['RTH abort threshold']
        self.qsObj.msp_rth_and_land_config['emerg_descent_rate'] = self.userSettingData['RTH and Landing Settings']['Emergency landing speed']

        # Position Estimator
        self.qsObj.msp_position_estimation_config['w_z_baro_p'] = int(self.userSettingData['Position Estimator']['Vertical Position Baro Weight']*100)
        self.qsObj.msp_position_estimation_config['w_z_gps_p'] = int(self.userSettingData['Position Estimator']['Vertical Position GPS Weight']*100)
        self.qsObj.msp_position_estimation_config['w_z_gps_v'] = int(self.userSettingData['Position Estimator']['Vertical Speed GPS Weight']*100)
        self.qsObj.msp_position_estimation_config['w_xy_gps_p'] = int(self.userSettingData['Position Estimator']['Horizontal Position GPS Weight']*100)
        self.qsObj.msp_position_estimation_config['w_xy_gps_v'] = int(self.userSettingData['Position Estimator']['Horizontal Speed GPS Weight']*100)
        self.qsObj.msp_position_estimation_config['gps_min_sats'] = self.userSettingData['Position Estimator']['Min GPS sats for valid fix']
        if self.userSettingData['Position Estimator']['Use GPS data for velocity calculation'] == True:
            self.qsObj.msp_position_estimation_config['use_gps_velned'] = 1
        elif self.userSettingData['Position Estimator']['Use GPS data for velocity calculation'] == False:
            self.qsObj.msp_position_estimation_config['use_gps_velned'] = 0

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = ParameterSettingWidget()
    form.resize(1080,720)
    form.show()
    app.exec_()
