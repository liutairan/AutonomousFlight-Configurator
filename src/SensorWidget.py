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
import numpy as np
# from apscheduler.schedulers.background import BackgroundScheduler
from random import *
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
    QListWidget, QListWidgetItem, QAbstractItemView, QWidget, QAction,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QHeaderView, QLabel, QTreeWidget, QTreeWidgetItem, QToolBar, QLineEdit,
    QCompleter, QSizePolicy, QComboBox, QMessageBox, QDialog, QDialogButtonBox,
    QFileDialog, QGridLayout, QFormLayout, QSlider, QScrollArea, QGroupBox,
    QSizePolicy, QSpacerItem)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QTimer

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

class SensorWidget(QWidget):
    sensorDataRequestSignal = pyqtSignal(int)
    def __init__(self, parent=None, qsObj=None):
        super(QWidget, self).__init__(parent)
        self.initUI()
        self.running = False
        self.qsObj = qsObj
        self.initVariables()
        self.setUpdateTimer()

    def initUI(self):
        self.bundle_dir = os.path.dirname(os.path.abspath(__file__))
        # Switch Icon Image
        self.switchOFFImage = QPixmap(self.bundle_dir + "/Pics/OFF.png")
        self.switchONImage = QPixmap(self.bundle_dir + "/Pics/ON.png")

        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)

        self.scrollArea = QScrollArea()
        self.scrollAreaGroupBox = QGroupBox(self)
        self.scrollAreaLayout = QVBoxLayout()
        self.scrollAreaGroupBox.setLayout(self.scrollAreaLayout)
        self.scrollArea.setWidget(self.scrollAreaGroupBox)
        self.scrollArea.setWidgetResizable(True)
        self.layout.addWidget(self.scrollArea)

        #
        mainPlotPageLayout = QVBoxLayout()
        self.scrollAreaLayout.addLayout(mainPlotPageLayout)

        self.panelLayout = {}
        self.figure = {}
        self.canvas = {}
        self.label = {}
        self.labelLayout = {}
        # a figure instance to plot on
        self.figure['acc'] = plt.figure()
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas['acc'] = FigureCanvas(self.figure['acc'])
        self.canvas['acc'].setStyleSheet("QWidget {min-height:200; min-width:900; max-width:900}")
        self.label['acc'] = QLabel("Accelerometer - g")
        self.label['ax'] = QLabel("ACC-X")
        self.label['ax-value'] = QLabel("0.00")
        self.label['ax-value'].setStyleSheet("QLabel {color:blue}")
        self.label['ay'] = QLabel("ACC-Y")
        self.label['ay-value'] = QLabel("0.00")
        self.label['ay-value'].setStyleSheet("QLabel {color:orange}")
        self.label['az'] = QLabel("ACC-Z")
        self.label['az-value'] = QLabel("0.00")
        self.label['az-value'].setStyleSheet("QLabel {color:green}")
        self.labelLayout['acc'] = QGridLayout()
        self.labelLayout['acc'].addWidget(self.label['acc'], 0, 0, 1, 2)
        self.labelLayout['acc'].addWidget(self.label['ax'], 1, 0, 1, 1)
        self.labelLayout['acc'].addWidget(self.label['ax-value'], 1, 1, 1, 1)
        self.labelLayout['acc'].addWidget(self.label['ay'], 2, 0, 1, 1)
        self.labelLayout['acc'].addWidget(self.label['ay-value'], 2, 1, 1, 1)
        self.labelLayout['acc'].addWidget(self.label['az'], 3, 0, 1, 1)
        self.labelLayout['acc'].addWidget(self.label['az-value'], 3, 1, 1, 1)
        self.panelLayout['acc'] = QHBoxLayout()
        self.panelLayout['acc'].addWidget(self.canvas['acc'])
        self.panelLayout['acc'].addLayout(self.labelLayout['acc'])
        mainPlotPageLayout.addLayout(self.panelLayout['acc'])

        self.figure['gyro'] = plt.figure()
        self.canvas['gyro'] = FigureCanvas(self.figure['gyro'])
        self.canvas['gyro'].setStyleSheet("QWidget {min-height:200; min-width:900; max-width:900}")
        self.label['gyro'] = QLabel("Gyroscope - deg/s")
        self.label['gx'] = QLabel("GYRO-X")
        self.label['gx-value'] = QLabel("0.00")
        self.label['gx-value'].setStyleSheet("QLabel {color:blue}")
        self.label['gy'] = QLabel("GYRO-Y")
        self.label['gy-value'] = QLabel("0.00")
        self.label['gy-value'].setStyleSheet("QLabel {color:orange}")
        self.label['gz'] = QLabel("GYRO-Z")
        self.label['gz-value'] = QLabel("0.00")
        self.label['gz-value'].setStyleSheet("QLabel {color:green}")
        self.labelLayout['gyro'] = QGridLayout()
        self.labelLayout['gyro'].addWidget(self.label['gyro'], 0, 0, 1, 2)
        self.labelLayout['gyro'].addWidget(self.label['gx'], 1, 0, 1, 1)
        self.labelLayout['gyro'].addWidget(self.label['gx-value'], 1, 1, 1, 1)
        self.labelLayout['gyro'].addWidget(self.label['gy'], 2, 0, 1, 1)
        self.labelLayout['gyro'].addWidget(self.label['gy-value'], 2, 1, 1, 1)
        self.labelLayout['gyro'].addWidget(self.label['gz'], 3, 0, 1, 1)
        self.labelLayout['gyro'].addWidget(self.label['gz-value'], 3, 1, 1, 1)
        self.panelLayout['gyro'] = QHBoxLayout()
        self.panelLayout['gyro'].addWidget(self.canvas['gyro'])
        self.panelLayout['gyro'].addLayout(self.labelLayout['gyro'])
        mainPlotPageLayout.addLayout(self.panelLayout['gyro'])

        self.figure['mag'] = plt.figure()
        self.canvas['mag'] = FigureCanvas(self.figure['mag'])
        self.canvas['mag'].setStyleSheet("QWidget {min-height:200; min-width:900; max-width:900}")
        self.label['mag'] = QLabel("Magnetometer - Ga")
        self.label['mx'] = QLabel("MAG-X")
        self.label['mx-value'] = QLabel("0.00")
        self.label['mx-value'].setStyleSheet("QLabel {color:blue}")
        self.label['my'] = QLabel("MAG-Y")
        self.label['my-value'] = QLabel("0.00")
        self.label['my-value'].setStyleSheet("QLabel {color:orange}")
        self.label['mz'] = QLabel("MAG-Z")
        self.label['mz-value'] = QLabel("0.00")
        self.label['mz-value'].setStyleSheet("QLabel {color:green}")
        self.labelLayout['mag'] = QGridLayout()
        self.labelLayout['mag'].addWidget(self.label['mag'], 0, 0, 1, 2)
        self.labelLayout['mag'].addWidget(self.label['mx'], 1, 0, 1, 1)
        self.labelLayout['mag'].addWidget(self.label['mx-value'], 1, 1, 1, 1)
        self.labelLayout['mag'].addWidget(self.label['my'], 2, 0, 1, 1)
        self.labelLayout['mag'].addWidget(self.label['my-value'], 2, 1, 1, 1)
        self.labelLayout['mag'].addWidget(self.label['mz'], 3, 0, 1, 1)
        self.labelLayout['mag'].addWidget(self.label['mz-value'], 3, 1, 1, 1)
        self.panelLayout['mag'] = QHBoxLayout()
        self.panelLayout['mag'].addWidget(self.canvas['mag'])
        self.panelLayout['mag'].addLayout(self.labelLayout['mag'])
        mainPlotPageLayout.addLayout(self.panelLayout['mag'])

        self.figure['baro'] = plt.figure()
        self.canvas['baro'] = FigureCanvas(self.figure['baro'])
        self.canvas['baro'].setStyleSheet("QWidget {min-height:200; min-width:900; max-width:900}")
        self.label['baro-title'] = QLabel("Barometer - meters")
        self.label['alt'] = QLabel("ALT")
        self.label['alt-value'] = QLabel("0.00")
        self.label['alt-value'].setStyleSheet("QLabel {color:blue}")
        self.label['baro'] = QLabel("BARO")
        self.label['baro-value'] = QLabel("0.00")
        self.label['baro-value'].setStyleSheet("QLabel {color:orange}")
        self.labelLayout['baro'] = QGridLayout()
        self.labelLayout['baro'].addWidget(self.label['baro-title'], 0, 0, 1, 2)
        self.labelLayout['baro'].addWidget(self.label['alt'], 1, 0, 1, 1)
        self.labelLayout['baro'].addWidget(self.label['alt-value'], 1, 1, 1, 1)
        self.labelLayout['baro'].addWidget(self.label['baro'], 2, 0, 1, 1)
        self.labelLayout['baro'].addWidget(self.label['baro-value'], 2, 1, 1, 1)
        self.panelLayout['baro'] = QHBoxLayout()
        self.panelLayout['baro'].addWidget(self.canvas['baro'])
        self.panelLayout['baro'].addLayout(self.labelLayout['baro'])
        mainPlotPageLayout.addLayout(self.panelLayout['baro'])

        mainPlotPageLayout.addStretch(1)

        self.setLayout(self.layout)

    def initVariables(self):
        self.time = {}
        self.rtime = {}
        self.data = {}
        self.step = {}
        self.step['acc'] = 0.01
        self.step['gyro'] = 0.01
        self.step['mag'] = 0.01
        self.step['baro'] = 0.1
        self.time['acc'] = np.arange(0, 2, self.step['acc'])
        self.rtime['acc'] = 2
        self.data['acc'] = np.zeros((int(2.0/self.step['acc']),3))
        self.time['gyro'] = np.arange(0, 2, self.step['gyro'])
        self.rtime['gyro'] = 2
        self.data['gyro'] = np.zeros((int(2.0/self.step['gyro']),3))
        self.time['mag'] = np.arange(0, 2, self.step['mag'])
        self.rtime['mag'] = 2
        self.data['mag'] = np.zeros((int(2.0/self.step['mag']),3))
        self.time['baro'] = np.arange(0, 2, self.step['baro'])
        self.rtime['baro'] = 2
        self.data['baro'] = np.zeros((int(2.0/self.step['baro']),2))

    def rand(self, field, step):
        randData = np.random.random(1)
        randData *= 2e2
        self.rtime[field] = self.rtime[field] + step
        trackData = np.array([[1e3*np.sin(10*self.rtime[field]), 1e3*np.cos(10*self.rtime[field]), 1e3*np.sin(20*self.rtime[field])]])
        return trackData

    def updateACCPlot(self):
        # yn = self.rand('acc', self.step['acc'])
        self.rtime['acc'] = self.rtime['acc'] + self.step['acc']
        yn = np.array([[self.qsObj.msp_raw_imu['ax'], self.qsObj.msp_raw_imu['ay'], self.qsObj.msp_raw_imu['az']]])
        self.time['acc'] = np.append(self.time['acc'], self.rtime['acc'])
        self.data['acc'] = np.append(self.data['acc'], yn, axis=0)
        tbpy = self.data['acc'][-int(2.0/self.step['acc']):]
        tbpx = self.time['acc'][-int(2.0/self.step['acc']):]

        self.figure['acc'].clear()
        # create an axis
        ax1 = self.figure['acc'].add_subplot(111)
        # plot data
        ax1.plot(tbpx, tbpy, '-')
        ax1.set_ylim(-1000,1000)
        ax1.grid()
        self.figure['acc'].tight_layout()
        # refresh canvas
        self.canvas['acc'].draw()
        self.label['ax-value'].setText(str(yn[0][0]))
        self.label['ay-value'].setText(str(yn[0][1]))
        self.label['az-value'].setText(str(yn[0][2]))

    def updateGYROPlot(self):
        # yn = self.rand('gyro', self.step['gyro'])
        self.rtime['gyro'] = self.rtime['gyro'] + self.step['gyro']
        yn = np.array([[self.qsObj.msp_raw_imu['gx'], self.qsObj.msp_raw_imu['gy'], self.qsObj.msp_raw_imu['gz']]])
        self.time['gyro'] = np.append(self.time['gyro'], self.rtime['gyro'])
        self.data['gyro'] = np.append(self.data['gyro'], yn, axis=0)
        tbpy = self.data['gyro'][-int(2.0/self.step['gyro']):]
        tbpx = self.time['gyro'][-int(2.0/self.step['gyro']):]

        self.figure['gyro'].clear()

        # create an axis
        ax1 = self.figure['gyro'].add_subplot(111)
        # plot data
        ax1.plot(tbpx, tbpy, '-')
        ax1.set_ylim(-5000,5000)
        ax1.grid()
        self.figure['gyro'].tight_layout()
        # refresh canvas
        self.canvas['gyro'].draw()
        self.label['gx-value'].setText(str(yn[0][0]))
        self.label['gy-value'].setText(str(yn[0][1]))
        self.label['gz-value'].setText(str(yn[0][2]))

    def updateMAGPlot(self):
        self.rtime['mag'] = self.rtime['mag'] + self.step['mag']
        yn = np.array([[self.qsObj.msp_raw_imu['mx'], self.qsObj.msp_raw_imu['my'], self.qsObj.msp_raw_imu['mz']]])
        self.time['mag'] = np.append(self.time['mag'], self.rtime['mag'])
        self.data['mag'] = np.append(self.data['mag'], yn, axis=0)
        tbpy = self.data['mag'][-int(2.0/self.step['mag']):]
        tbpx = self.time['mag'][-int(2.0/self.step['mag']):]

        self.figure['mag'].clear()

        # create an axis
        ax1 = self.figure['mag'].add_subplot(111)
        # plot data
        ax1.plot(tbpx, tbpy, '-')
        ax1.set_ylim(-500,500)
        ax1.grid()
        self.figure['mag'].tight_layout()
        # refresh canvas
        self.canvas['mag'].draw()
        self.label['mx-value'].setText(str(yn[0][0]))
        self.label['my-value'].setText(str(yn[0][1]))
        self.label['mz-value'].setText(str(yn[0][2]))

    def updateBAROPlot(self):
        self.rtime['baro'] = self.rtime['baro'] + self.step['baro']
        yn = np.array([[self.qsObj.msp_altitude['estalt'], self.qsObj.msp_altitude['baro']]])
        self.time['baro'] = np.append(self.time['baro'], self.rtime['baro'])
        self.data['baro'] = np.append(self.data['baro'], yn, axis=0)
        tbpy = self.data['baro'][-int(2.0/self.step['baro']):]
        tbpx = self.time['baro'][-int(2.0/self.step['baro']):]

        self.figure['baro'].clear()

        # create an axis
        ax1 = self.figure['baro'].add_subplot(111)
        # plot data
        ax1.plot(tbpx, tbpy, '-')
        # ax1.set_ylim(-50000,50000)
        ax1.grid()
        self.figure['baro'].tight_layout()
        # refresh canvas
        self.canvas['baro'].draw()
        self.label['alt-value'].setText(str(yn[0][0]))
        self.label['baro-value'].setText(str(yn[0][1]))

    def dataRequest(self, ind):
        if ind == 0:
            self.sensorDataRequestSignal.emit(0)
        elif ind == 1:
            self.sensorDataRequestSignal.emit(1)

    def setUpdateTimer(self):
        ## Start a timer to rapidly update the plot
        self.sched = {}
        self.sched['acc'] = QTimer()
        self.sched['acc'].timeout.connect(partial(self.dataRequest, 0))

        self.sched['baro'] = QTimer()
        self.sched['baro'].timeout.connect(partial(self.dataRequest, 1))

        # self.sched['gyro'] = QTimer()
        # self.sched['gyro'].timeout.connect(partial(self.dataRequest, 1))

    def start(self):
        self.sched['acc'].start(int(1.0/self.step['acc']))
        self.sched['baro'].start(int(1.0/self.step['baro']))
        # self.sched['gyro'].start(int(1.0/self.step['gyro']))

    def stop(self):
        self.sched['acc'].stop()
        self.sched['baro'].stop()
        # self.sched['gyro'].stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = SensorWidget()
    form.resize(1080,720)
    form.show()
    app.exec_()
