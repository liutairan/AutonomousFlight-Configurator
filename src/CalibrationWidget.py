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
    QFileDialog, QGridLayout, QFormLayout, QSlider, QScrollArea, QGroupBox,
    QSpinBox)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QSize

from SettingFileIO import *

class CalibrationWidget(QWidget):
    calibrationSaveSignal = pyqtSignal(list)
    accCalibrateSignal = pyqtSignal(int)
    magCalibrateSignal = pyqtSignal()
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

        accCalGroup = QGroupBox("ACC Calibration", self)
        self.scrollAreaLayout.addWidget(accCalGroup)
        self.accCalGroupLayout = QGridLayout()
        self.accCalGroupLayoutInit()
        accCalGroup.setLayout(self.accCalGroupLayout)

        magCalGroup = QGroupBox("MAG Calibration", self)
        self.scrollAreaLayout.addWidget(magCalGroup)
        self.magCalGroupLayout = QGridLayout()
        self.magCalGroupLayoutInit()
        magCalGroup.setLayout(self.magCalGroupLayout)

        self.scrollAreaLayout.addStretch(1)
        self.setLayout(self.layout)

    def initValues(self):
        self.loadValuesFromDefault()
        # self.setUIDefaultValues()
        self.userSettingData = dict(self.defaultSettingData)
        self.setUIValues()

    def setUIValues(self):
        calibrationMask = self.userSettingData['Calibration']['Acc Calibration Axis Flags']
        temp = format(calibrationMask, '08b')
        for i in range(6):
            if temp[7-i] == "1":
                self.calibrationACCSteps[str(i+1)].setIcon(QIcon(self.bundle_dir+"/Pics/pos"+str(i+1)+".svg"))
            else:
                self.calibrationACCSteps[str(i+1)].setIcon(QIcon(self.bundle_dir+"/Pics/pos"+str(i+1)+"_grey.svg"))
        self.accCal['X zero'].setValue(self.userSettingData['Calibration']['Acc X zero'])
        self.accCal['Y zero'].setValue(self.userSettingData['Calibration']['Acc Y zero'])
        self.accCal['Z zero'].setValue(self.userSettingData['Calibration']['Acc Z zero'])
        self.accCal['X gain'].setValue(self.userSettingData['Calibration']['Acc X gain'])
        self.accCal['Y gain'].setValue(self.userSettingData['Calibration']['Acc Y gain'])
        self.accCal['Z gain'].setValue(self.userSettingData['Calibration']['Acc Z gain'])
        self.magCal['X zero'].setValue(self.userSettingData['Calibration']['Mag X zero'])
        self.magCal['Y zero'].setValue(self.userSettingData['Calibration']['Mag Y zero'])
        self.magCal['Z zero'].setValue(self.userSettingData['Calibration']['Mag Z zero'])

    def saveandreboot(self):
        # Get values from UI: UI->userSettingData
        self.getUIValues()
        # userSettingData->qsObj
        self.setQSObj()
        # qsObj->Board write with MSP
        tbsList = []
        self.calibrationSaveSignal.emit(tbsList)
        pass

    def getUIValues(self):
        # Read widget values and set self.userSettingData: UI->userSettingData
        self.userSettingData['Calibration']['Acc X zero'] = self.accCal['X zero'].value()
        self.userSettingData['Calibration']['Acc Y zero'] = self.accCal['Y zero'].value()
        self.userSettingData['Calibration']['Acc Z zero'] = self.accCal['Z zero'].value()
        self.userSettingData['Calibration']['Acc X gain'] = self.accCal['X gain'].value()
        self.userSettingData['Calibration']['Acc Y gain'] = self.accCal['Y gain'].value()
        self.userSettingData['Calibration']['Acc Z gain'] = self.accCal['Z gain'].value()
        self.userSettingData['Calibration']['Mag X zero'] = self.magCal['X zero'].value()
        self.userSettingData['Calibration']['Mag Y zero'] = self.magCal['Y zero'].value()
        self.userSettingData['Calibration']['Mag Z zero'] = self.magCal['Z zero'].value()

    def setQSObj(self):
        # userSettingData->qsObj
        self.qsObj.msp_calibration_data['Acc X zero'] = self.userSettingData['Calibration']['Acc X zero']
        self.qsObj.msp_calibration_data['Acc Y zero'] = self.userSettingData['Calibration']['Acc Y zero']
        self.qsObj.msp_calibration_data['Acc Z zero'] = self.userSettingData['Calibration']['Acc Z zero']
        self.qsObj.msp_calibration_data['Acc X gain'] = self.userSettingData['Calibration']['Acc X gain']
        self.qsObj.msp_calibration_data['Acc Y gain'] = self.userSettingData['Calibration']['Acc Y gain']
        self.qsObj.msp_calibration_data['Acc Z gain'] = self.userSettingData['Calibration']['Acc Z gain']
        self.qsObj.msp_calibration_data['Mag X zero'] = self.userSettingData['Calibration']['Mag X zero']
        self.qsObj.msp_calibration_data['Mag Y zero'] = self.userSettingData['Calibration']['Mag Y zero']
        self.qsObj.msp_calibration_data['Mag Z zero'] = self.userSettingData['Calibration']['Mag Z zero']

    def accCalGroupLayoutInit(self):
        note = "Note: If the flightcontroller is mounted in another angle or upside down,\n" + \
               "do the calibration steps with the flightcontroller pointing as shown in \n" + \
               "the pictures, not the quad (otherwise calibration won´t work)."
        self.accCalGroupLayout.addWidget(QLabel(note), 0, 0, 1, 4)
        self.startACCCalButton = QPushButton("Start ACC Calibration", self)
        self.startACCCalButton.setStyleSheet("QPushButton {min-width: 100; min-height: 100}")
        self.startACCCalButton.clicked.connect(self.calibrateAcc)
        self.accCalGroupLayout.addWidget(self.startACCCalButton, 0, 4, 1, 2)
        self.calibrationACCSteps = {"1": QPushButton("Step 1", self),
                                    "2": QPushButton("Step 2", self),
                                    "3": QPushButton("Step 3", self),
                                    "4": QPushButton("Step 4", self),
                                    "5": QPushButton("Step 5", self),
                                    "6": QPushButton("Step 6", self)}
        # Order of bits 0, 1, 3, 4, 2, 4
        for i in range(6):
            self.calibrationACCSteps[str(i+1)].setStyleSheet("QPushButton {min-width: 100; min-height: 200}")
            self.calibrationACCSteps[str(i+1)].clicked.connect(partial(self.calibrationACCStepClicked, i+1))
            self.accCalGroupLayout.addWidget(self.calibrationACCSteps[str(i+1)], (int(i/3))*2+1, (i%3)*2, 2, 2)
            # self.calibrationACCSteps[str(i+1)].setIcon(QIcon(self.bundle_dir+"/Pics/pos"+str(i+1)+".svg"))
            self.calibrationACCSteps[str(i+1)].setIconSize(QSize(400,200))
        self.accCal = {}
        self.accCalGroupLayout.addWidget(QLabel("X zero"), 5, 0, 1, 1)
        self.accCal['X zero'] = QSpinBox()
        self.accCal['X zero'].setRange(-5000,5000)
        self.accCalGroupLayout.addWidget(self.accCal['X zero'], 5, 1, 1, 1)

        self.accCalGroupLayout.addWidget(QLabel("Y zero"), 5, 2, 1, 1)
        self.accCal['Y zero'] = QSpinBox()
        self.accCal['Y zero'].setRange(-5000,5000)
        self.accCalGroupLayout.addWidget(self.accCal['Y zero'], 5, 3, 1, 1)

        self.accCalGroupLayout.addWidget(QLabel("Z zero"), 5, 4, 1, 1)
        self.accCal['Z zero'] = QSpinBox()
        self.accCal['Z zero'].setRange(-5000,5000)
        self.accCalGroupLayout.addWidget(self.accCal['Z zero'], 5, 5, 1, 1)

        self.accCalGroupLayout.addWidget(QLabel("X gain"), 6, 0, 1, 1)
        self.accCal['X gain'] = QSpinBox()
        self.accCal['X gain'].setRange(-5000,5000)
        self.accCalGroupLayout.addWidget(self.accCal['X gain'], 6, 1, 1, 1)

        self.accCalGroupLayout.addWidget(QLabel("Y gain"), 6, 2, 1, 1)
        self.accCal['Y gain'] = QSpinBox()
        self.accCal['Y gain'].setRange(-5000,5000)
        self.accCalGroupLayout.addWidget(self.accCal['Y gain'], 6, 3, 1, 1)

        self.accCalGroupLayout.addWidget(QLabel("Z gain"), 6, 4, 1, 1)
        self.accCal['Z gain'] = QSpinBox()
        self.accCal['Z gain'].setRange(-5000,5000)
        self.accCalGroupLayout.addWidget(self.accCal['Z gain'], 6, 5, 1, 1)

    def magCalGroupLayoutInit(self):
        note = "After pressing the button you have 30 seconds to hold the copter in the air\n" + \
               "and rotate it so that each side (front, back, left, right, top and bottom)\n" + \
               "points down towards the earth."
        self.magCalGroupLayout.addWidget(QLabel(note), 0, 0, 1, 4)
        self.startMAGCalButton = QPushButton("Start MAG Calibration", self)
        self.startMAGCalButton.setStyleSheet("QPushButton {min-width: 100; min-height: 100}")
        self.startMAGCalButton.clicked.connect(self.calibrateMag)
        self.magCalGroupLayout.addWidget(self.startMAGCalButton, 0, 4, 1, 2)
        self.magCal = {}
        self.magCalGroupLayout.addWidget(QLabel("X"), 1, 0, 1, 1)
        self.magCal['X zero'] = QSpinBox()
        self.magCal['X zero'].setRange(-200,200)
        self.magCalGroupLayout.addWidget(self.magCal['X zero'], 1, 1, 1, 1)
        self.magCalGroupLayout.addWidget(QLabel("Y"), 1, 2, 1, 1)
        self.magCal['Y zero'] = QSpinBox()
        self.magCal['Y zero'].setRange(-200,200)
        self.magCalGroupLayout.addWidget(self.magCal['Y zero'], 1, 3, 1, 1)
        self.magCalGroupLayout.addWidget(QLabel("Z"), 1, 4, 1, 1)
        self.magCal['Z zero'] = QSpinBox()
        self.magCal['Z zero'].setRange(-1000,1000)
        self.magCalGroupLayout.addWidget(self.magCal['Z zero'], 1, 5, 1, 1)

    def calibrateAcc(self):
        self.accCalibrateSignal.emit(0)

    def calibrationACCStepClicked(self, i):
        # self.accCalibrateSignal.emit(i)
        pass

    def calibrateMag(self):
        self.magCalibrateSignal.emit()

    def loadValuesFromDefault(self):
        self.defaultSettingData = readDefaultSettingFile()

    def loadValuesFromUserSaved(self):
        self.userSettingData = readUserSettingFile()

    def setValues(self):
        self.userSettingData['Calibration']['Acc Calibration Axis Flags'] = self.qsObj.msp_calibration_data['accGetCalibrationAxisFlags']
        self.userSettingData['Calibration']['Acc X zero'] = self.qsObj.msp_calibration_data['Acc X zero']
        self.userSettingData['Calibration']['Acc Y zero'] = self.qsObj.msp_calibration_data['Acc Y zero']
        self.userSettingData['Calibration']['Acc Z zero'] = self.qsObj.msp_calibration_data['Acc Z zero']
        self.userSettingData['Calibration']['Acc X gain'] = self.qsObj.msp_calibration_data['Acc X gain']
        self.userSettingData['Calibration']['Acc Y gain'] = self.qsObj.msp_calibration_data['Acc Y gain']
        self.userSettingData['Calibration']['Acc Z gain'] = self.qsObj.msp_calibration_data['Acc Z gain']
        self.userSettingData['Calibration']['Mag X zero'] = self.qsObj.msp_calibration_data['Mag X zero']
        self.userSettingData['Calibration']['Mag Y zero'] = self.qsObj.msp_calibration_data['Mag Y zero']
        self.userSettingData['Calibration']['Mag Z zero'] = self.qsObj.msp_calibration_data['Mag Z zero']
        # Update UI values
        self.setUIValues()

    def processFeedback(self):
        self.setValues()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = CalibrationWidget()
    form.resize(1080,720)
    form.show()
    app.exec_()
