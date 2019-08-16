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
# from apscheduler.schedulers.background import BackgroundScheduler
from random import *
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
    QListWidget, QListWidgetItem, QAbstractItemView, QWidget, QAction,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QHeaderView, QLabel, QTreeWidget, QTreeWidgetItem, QToolBar, QLineEdit,
    QCompleter, QSizePolicy, QComboBox, QMessageBox, QDialog, QDialogButtonBox,
    QFileDialog, QGridLayout, QFormLayout, QGroupBox, QProgressBar)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QTimer, Qt

class MotorInfoWidget(QWidget):
    motorDataRequestSignal = pyqtSignal(int)
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

        # Motor Info Group
        motorGroupBox = QGroupBox(self)
        self.layout.addWidget(motorGroupBox, 0, 0)
        motorGroupBoxLayout = QGridLayout()
        self.motorLabelList = ["1", "2", "3", "4"]
        self.motorLabelWidgetList = []
        self.motorBarList = []
        for i in range(len(self.motorLabelList)):
            self.motorBarList.append(QProgressBar(self))
            self.motorBarList[i].setOrientation(Qt.Vertical)
            self.motorBarList[i].setMinimum(1000)
            self.motorBarList[i].setMaximum(2000)
            self.motorBarList[i].setTextVisible(True)
            self.motorBarList[i].setTextDirection(1)
            self.motorBarList[i].setValue(1000)
            motorGroupBoxLayout.addWidget(self.motorBarList[i], 0, 2*i+1, 3, 2)
            self.motorLabelWidgetList.append(QLabel(self.motorLabelList[i]))
            motorGroupBoxLayout.addWidget(self.motorLabelWidgetList[i], 3, 2*i+1, 1, 2)
        motorGroupBox.setLayout(motorGroupBoxLayout)

        # Set Main Layout of this page
        self.setLayout(self.layout)

    # Use QTimer
    def initVariables(self):
        self.step = {}
        self.step['motor'] = 0.5

    # Use QTimer
    def setUpdateTimer(self):
        ## Start a timer to rapidly update the plot
        self.sched = {}

        self.sched['motor'] = QTimer()
        self.sched['motor'].timeout.connect(partial(self.dataRequest, 0))

    # Use QTimer
    def dataRequest(self, ind):
        # ind is the index of fields to be updated,
        #    ind = 0, 1, 2, 3, 4
        #    ind = 0: motor
        self.motorDataRequestSignal.emit(ind)

    # Use QTimer, start all the timers.
    def start(self):
        self.sched['motor'].start(int(1.0/self.step['motor']))

    # Use QTimer, stop all the timers.
    def stop(self):
        self.sched['motor'].stop()

    # Update attitude labels
    def updateMotorValues(self):
        for i in range(len(self.motorLabelList)):
            self.motorBarList[i].setValue(self.qsObj.msp_motor[str(i+1)])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MotorInfoWidget()
    form.resize(1080,720)
    form.show()
    app.exec_()
