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
    QSpinBox, QRadioButton, QDoubleSpinBox, QSpacerItem)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QPainter
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QSize
from PyQt5 import QtSvg
import svgwrite

from SettingFileIO import *

class TopologyWidget(QWidget):
    topologySaveSignal = pyqtSignal(list)
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
        mainConfigureLayout = QVBoxLayout()
        self.scrollAreaLayout.addLayout(mainConfigureLayout)

        # Topology
        topologyGroupBox = QGroupBox("Topology", self)
        mainConfigureLayout.addWidget(topologyGroupBox)
        self.topologyGroupBoxLayout = QGridLayout()
        self.topologyGroupBoxInit()
        topologyGroupBox.setLayout(self.topologyGroupBoxLayout)

        # Sketch
        sketchGroupBox = QGroupBox("Sketch", self)
        mainConfigureLayout.addWidget(sketchGroupBox)
        self.sketchGroupBoxLayout = QGridLayout()
        self.sketchGroupBoxInit()
        sketchGroupBox.setLayout(self.sketchGroupBoxLayout)

        self.scrollAreaLayout.addStretch(1)
        self.setLayout(self.layout)

    def topologyGroupBoxInit(self):
        self.topologySettings = {}

        self.topologyGroupBoxLayout.addWidget(QLabel("Telemetry Settings"), 0, 0, 1, 1)

        self.topologyGroupBoxLayout.addWidget(QLabel("Current Telemetry Address (Self)"), 1, 0, 1, 1)
        self.topologySettings['Current Telemetry Address'] = QComboBox()
        self.topologyGroupBoxLayout.addWidget(self.topologySettings['Current Telemetry Address'], 1, 1, 1, 1)

        self.topologyGroupBoxLayout.addWidget(QLabel("Source"), 2, 0, 1, 1)
        self.topologySettings['Telemetry Source Type'] = QComboBox()
        self.topologyGroupBoxLayout.addWidget(self.topologySettings['Telemetry Source Type'], 2, 1, 1, 1)
        self.topologySettings['Telemetry Source Address 0'] = QComboBox()
        self.topologyGroupBoxLayout.addWidget(self.topologySettings['Telemetry Source Address 0'], 2, 2, 1, 1)
        self.topologySettings['Telemetry Source Address 1'] = QComboBox()
        self.topologyGroupBoxLayout.addWidget(self.topologySettings['Telemetry Source Address 1'], 2, 3, 1, 1)
        self.topologySettings['Telemetry Source Address 2'] = QComboBox()
        self.topologyGroupBoxLayout.addWidget(self.topologySettings['Telemetry Source Address 2'], 2, 4, 1, 1)

        self.topologyGroupBoxLayout.addWidget(QLabel("Destination"), 3, 0, 1, 1)
        self.topologySettings['Telemetry Destination Type'] = QComboBox()
        self.topologyGroupBoxLayout.addWidget(self.topologySettings['Telemetry Destination Type'], 3, 1, 1, 1)
        self.topologySettings['Telemetry Destination Address 0'] = QComboBox()
        self.topologyGroupBoxLayout.addWidget(self.topologySettings['Telemetry Destination Address 0'], 3, 2, 1, 1)
        self.topologySettings['Telemetry Destination Address 1'] = QComboBox()
        self.topologyGroupBoxLayout.addWidget(self.topologySettings['Telemetry Destination Address 1'], 3, 3, 1, 1)
        self.topologySettings['Telemetry Destination Address 2'] = QComboBox()
        self.topologyGroupBoxLayout.addWidget(self.topologySettings['Telemetry Destination Address 2'], 3, 4, 1, 1)

        self.topologyGroupBoxLayout.addWidget(QLabel("\nRemote Control Settings"), 4, 0, 1, 1)

        self.topologyGroupBoxLayout.addWidget(QLabel("Current Remote Control Address (Self)"), 5, 0, 1, 1)
        self.topologySettings['Current Remote Control Address'] = QComboBox()
        self.topologyGroupBoxLayout.addWidget(self.topologySettings['Current Remote Control Address'], 5, 1, 1, 1)

        self.topologyGroupBoxLayout.addWidget(QLabel("Remote Control Source Address"), 6, 0, 1, 1)
        self.topologySettings['Remote Control Source Address'] = QComboBox()
        self.topologyGroupBoxLayout.addWidget(self.topologySettings['Remote Control Source Address'], 6, 1, 1, 1)

    def sketchGroupBoxInit(self):
        # Default settings
        self.sketchSettings = {}

        self.sketchGroupBoxLayout.addWidget(QLabel("d_{ji}"), 0, 0, 1, 1)
        self.sketchSettings['dji'] = QSpinBox()
        self.sketchSettings['dji'].setRange(0,20000)
        self.sketchSettings['dji'].setValue(100)
        self.sketchGroupBoxLayout.addWidget(self.sketchSettings['dji'], 0, 1, 1, 1)

        self.sketchGroupBoxLayout.addWidget(QLabel("d_{ki}"), 1, 0, 1, 1)
        self.sketchSettings['dki'] = QSpinBox()
        self.sketchSettings['dki'].setRange(0,20000)
        self.sketchSettings['dki'].setValue(100)
        self.sketchGroupBoxLayout.addWidget(self.sketchSettings['dki'], 1, 1, 1, 1)

        self.sketchGroupBoxLayout.addWidget(QLabel("d_{kj}"), 2, 0, 1, 1)
        self.sketchSettings['dkj'] = QSpinBox()
        self.sketchSettings['dkj'].setRange(0,20000)
        self.sketchSettings['dkj'].setValue(100)
        self.sketchGroupBoxLayout.addWidget(self.sketchSettings['dkj'], 2, 1, 1, 1)

        self.sketchSettings['draw'] = QPushButton("Draw")
        self.sketchSettings['draw'].clicked.connect(self.draw)
        self.sketchGroupBoxLayout.addWidget(self.sketchSettings['draw'], 3, 1, 1, 1)

        self.sketchSettings['sketch'] = QLabel()
        self.sketchGroupBoxLayout.addWidget(self.sketchSettings['sketch'], 0, 2, 11, 5)

        self.sketchGroupBoxLayout.addWidget(QLabel("Graph Type"), 4, 0, 1, 1)
        self.sketchSettings['Graph Type'] = QComboBox()
        graphTypeList = ["Undirected", "Directed"]
        self.sketchSettings['Graph Type'].addItems(graphTypeList)
        self.sketchGroupBoxLayout.addWidget(self.sketchSettings['Graph Type'], 4, 1, 1, 1)

        self.sketchGroupBoxLayout.addWidget(QLabel("Identity"), 5, 0, 1, 1)
        self.sketchSettings['Identity'] = QComboBox()
        identityList = ["Leader", "First Follower", "Normal Follower"]
        self.sketchSettings['Identity'].addItems(identityList)
        self.sketchGroupBoxLayout.addWidget(self.sketchSettings['Identity'], 5, 1, 1, 1)

        self.sketchGroupBoxLayout.addWidget(QLabel("Distance Gain"), 6, 0, 1, 1)
        self.sketchSettings['Distance Gain'] = QSpinBox()
        self.sketchSettings['Distance Gain'].setRange(0,1000)
        self.sketchSettings['Distance Gain'].setValue(1)
        self.sketchGroupBoxLayout.addWidget(self.sketchSettings['Distance Gain'], 6, 1, 1, 1)

        self.sketchGroupBoxLayout.addWidget(QLabel("Area Gain"), 7, 0, 1, 1)
        self.sketchSettings['Area Gain'] = QSpinBox()
        self.sketchSettings['Area Gain'].setRange(0,1000)
        self.sketchSettings['Area Gain'].setValue(1)
        self.sketchGroupBoxLayout.addWidget(self.sketchSettings['Area Gain'], 7, 1, 1, 1)

        self.sketchGroupBoxLayout.addWidget(QLabel("Lat Gain"), 8, 0, 1, 1)
        self.sketchSettings['Lat Gain'] = QSpinBox()
        self.sketchSettings['Lat Gain'].setRange(0,10000)
        self.sketchSettings['Lat Gain'].setValue(1000)
        self.sketchGroupBoxLayout.addWidget(self.sketchSettings['Lat Gain'], 8, 1, 1, 1)

        self.sketchGroupBoxLayout.addWidget(QLabel("Lon Gain"), 9, 0, 1, 1)
        self.sketchSettings['Lon Gain'] = QSpinBox()
        self.sketchSettings['Lon Gain'].setRange(0,10000)
        self.sketchSettings['Lon Gain'].setValue(1000)
        self.sketchGroupBoxLayout.addWidget(self.sketchSettings['Lon Gain'], 9, 1, 1, 1)

        self.sketchGroupBoxLayout.addWidget(QLabel("Flight Height"), 10, 0, 1, 1)
        self.sketchSettings['Flight Height'] = QSpinBox()
        self.sketchSettings['Flight Height'].setRange(200,2000)
        self.sketchSettings['Flight Height'].setValue(200)
        self.sketchGroupBoxLayout.addWidget(self.sketchSettings['Flight Height'], 10, 1, 1, 1)
        # Set Spacing
        verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.sketchGroupBoxLayout.addItem(verticalSpacer, 11, 0, Qt.AlignTop)
        # self.sketchGroupBoxLayout.setSpacing(2)
        # self.sketchGroupBoxLayout.setVerticalSpacing(2)
        # Draw
        self.draw()

    def draw(self):
        dji = self.sketchSettings['dji'].value()
        xi = 0
        yi = 0
        xj = dji
        yj = 0
        # Calculate
        dki = self.sketchSettings['dki'].value()
        dkj = self.sketchSettings['dkj'].value()
        xk = int(float(dki*dki-dkj*dkj)/float(2*dji) + float(dji)/2)
        yk = int(math.sqrt( float(2*math.pow(dji,2)*math.pow(dki,2)
                                + 2*math.pow(dji,2)*math.pow(dkj,2)
                                + 2*math.pow(dki,2)*math.pow(dkj,2)
                                - math.pow(dji,4)
                                - math.pow(dki,4)
                                - math.pow(dkj,4) ))/float(2*dji))
        points = [xi,yi,xj,yj,xk,yk]
        # Draw
        self.generateSVG(points)
        # Load
        self.sketchSettings['sketch'].setPixmap(QPixmap('topology.svg'))

    def generateSVG(self, pointList):
        dwg = svgwrite.Drawing('topology.svg', size=('20cm', '10cm'))
        unit_cm = svgwrite.cm
        left_border = 30
        up_border = 30

        xi = pointList[0]
        yi = pointList[1]
        xj = pointList[2]
        yj = pointList[3]
        xk = pointList[4]
        yk = pointList[5]
        pix = (left_border + xi)*unit_cm
        piy = (up_border + yi)*unit_cm
        pjx = (left_border + xj)*unit_cm
        pjy = (up_border + yj)*unit_cm
        pkx = (left_border + xk)*unit_cm
        pky = (up_border + yk)*unit_cm
        pitx = (left_border + xi - 15)*unit_cm
        pity = piy
        pjtx = (left_border + xj + 5)*unit_cm
        pjty = pjy
        pktx = pkx
        pkty = (up_border + yk + 20)*unit_cm
        # Draw Lines
        line_ji =  dwg.line((pix, piy), (pjx, pjy))
        line_ji.stroke('black', width=3).dasharray([5, 5])
        dwg.add(line_ji)
        line_ki =  dwg.line((pkx, pky), (pix, piy))
        line_ki.stroke('black', width=3)
        dwg.add(line_ki)
        line_kj =  dwg.line((pkx, pky), (pjx, pjy))
        line_kj.stroke('black', width=3)
        dwg.add(line_kj)
        # Draw labels
        dwg.add(dwg.text('1', insert=(pitx, pity), fill='red', font_size=30))
        dwg.add(dwg.text('2', insert=(pjtx, pjty), fill='red', font_size=30))
        dwg.add(dwg.text('3', insert=(pktx, pkty), fill='red', font_size=30))
        dwg.save()

    def saveandreboot(self):
        # Get values from UI: UI->userSettingData
        self.getUIValues()
        # userSettingData->qsObj
        self.setQSObj()
        # qsObj->Board write with MSP
        tbsList = []
        self.topologySaveSignal.emit(tbsList)

    # Read widget values and set self.userSettingData: UI->userSettingData
    def getUIValues(self):
        self.userSettingData['Topology']['Current Telemetry Address'] = self.topologySettings['Current Telemetry Address'].currentIndex()
        self.userSettingData['Topology']['Telemetry Source Type'] = self.topologySettings['Telemetry Source Type'].currentIndex()
        self.userSettingData['Topology']['Telemetry Destination Type'] = self.topologySettings['Telemetry Destination Type'].currentIndex()
        for i in range(3):
            self.userSettingData['Topology']['Telemetry Source Address'][i] = self.topologySettings['Telemetry Source Address '+str(i)].currentIndex()
            self.userSettingData['Topology']['Telemetry Destination Address'][i] = self.topologySettings['Telemetry Destination Address '+str(i)].currentIndex()

        self.userSettingData['Topology']['Current Remote Control Address'] = self.topologySettings['Current Remote Control Address'].currentIndex()
        self.userSettingData['Topology']['Remote Control Source Address'] = self.topologySettings['Remote Control Source Address'].currentIndex()

        # Formation Configure
        self.userSettingData['Topology']['d_ji'] = self.sketchSettings['dji'].value()
        self.userSettingData['Topology']['d_ki'] = self.sketchSettings['dki'].value()
        self.userSettingData['Topology']['d_kj'] = self.sketchSettings['dkj'].value()
        self.userSettingData['Topology']['Graph Type'] = self.sketchSettings['Graph Type'].currentIndex()
        self.userSettingData['Topology']['Identity'] = self.sketchSettings['Identity'].currentIndex()
        self.userSettingData['Topology']['Distance Gain'] = self.sketchSettings['Distance Gain'].value()
        self.userSettingData['Topology']['Area Gain'] = self.sketchSettings['Area Gain'].value()
        self.userSettingData['Topology']['Lat Gain'] = self.sketchSettings['Lat Gain'].value()
        self.userSettingData['Topology']['Lon Gain'] = self.sketchSettings['Lon Gain'].value()
        self.userSettingData['Topology']['Flight Height'] = self.sketchSettings['Flight Height'].value()

    # Transfer userSettingData to qsObj
    def setQSObj(self):
        # userSettingData->qsObj
        # Network Configure
        xbee_self_tele_addr_ind = self.userSettingData['Topology']['Current Telemetry Address']
        self.qsObj.msp_network_config['selfTeleAddressLow'] = int(self.userSettingData['Topology']['Address Options'][xbee_self_tele_addr_ind], 16)

        xbee_tele_source_1_addr_ind = self.userSettingData['Topology']['Telemetry Source Address'][0]
        self.qsObj.msp_network_config['teleSource1AddressLow'] = int(self.userSettingData['Topology']['Address Options'][xbee_tele_source_1_addr_ind], 16)
        xbee_tele_destination_1_addr_ind = self.userSettingData['Topology']['Telemetry Destination Address'][0]
        self.qsObj.msp_network_config['teleDestination1AddressLow'] = int(self.userSettingData['Topology']['Address Options'][xbee_tele_destination_1_addr_ind], 16)

        xbee_tele_source_2_addr_ind = self.userSettingData['Topology']['Telemetry Source Address'][1]
        self.qsObj.msp_network_config['teleSource2AddressLow'] = int(self.userSettingData['Topology']['Address Options'][xbee_tele_source_2_addr_ind], 16)
        xbee_tele_destination_2_addr_ind = self.userSettingData['Topology']['Telemetry Destination Address'][1]
        self.qsObj.msp_network_config['teleDestination2AddressLow'] = int(self.userSettingData['Topology']['Address Options'][xbee_tele_destination_2_addr_ind], 16)

        xbee_tele_source_3_addr_ind = self.userSettingData['Topology']['Telemetry Source Address'][2]
        self.qsObj.msp_network_config['teleSource3AddressLow'] = int(self.userSettingData['Topology']['Address Options'][xbee_tele_source_3_addr_ind], 16)
        xbee_tele_destination_3_addr_ind = self.userSettingData['Topology']['Telemetry Destination Address'][2]
        self.qsObj.msp_network_config['teleDestination3AddressLow'] = int(self.userSettingData['Topology']['Address Options'][xbee_tele_destination_3_addr_ind], 16)

        xbee_self_rc_addr_ind = self.userSettingData['Topology']['Current Remote Control Address']
        self.qsObj.msp_network_config['selfRemoteAddressLow'] = int(self.userSettingData['Topology']['Address Options'][xbee_self_rc_addr_ind], 16)

        xbee_rc_source_addr_ind = self.userSettingData['Topology']['Remote Control Source Address']
        self.qsObj.msp_network_config['remoteSourceAddressLow'] = int(self.userSettingData['Topology']['Address Options'][xbee_rc_source_addr_ind], 16)
        # Address
        # xbee_self_tele_addr_ind = self.userSettingData['Topology']['Current Telemetry Address']
        # self.qsObj.msp_xbee_self_telemetry_addr = int(self.userSettingData['Topology']['Address Options'][xbee_self_tele_addr_ind], 16)
        # for i in range(3):
        #     xbee_tele_source_addr_ind = self.userSettingData['Topology']['Telemetry Source Address'][i]
        #     self.qsObj.msp_xbee_telemetry_source_addr[i] = int(self.userSettingData['Topology']['Address Options'][xbee_tele_source_addr_ind], 16)
        #     xbee_tele_destination_addr_ind = self.userSettingData['Topology']['Telemetry Destination Address'][i]
        #     self.qsObj.msp_xbee_telemetry_source_addr[i] = int(self.userSettingData['Topology']['Address Options'][xbee_tele_destination_addr_ind], 16)
        # xbee_self_rc_addr_ind = self.userSettingData['Topology']['Current Remote Control Address']
        # self.qsObj.msp_xbee_self_rc_addr = int(self.userSettingData['Topology']['Address Options'][xbee_self_rc_addr_ind], 16)
        # xbee_rc_source_addr_ind = self.userSettingData['Topology']['Remote Control Source Address']
        # self.qsObj.msp_xbee_rc_source_addr = int(self.userSettingData['Topology']['Address Options'][xbee_rc_source_addr_ind], 16)
        # Formation Configure
        self.qsObj.msp_formation_config['flight_height'] = self.userSettingData['Topology']['Flight Height']
        self.qsObj.msp_formation_config['distance_gain'] = self.userSettingData['Topology']['Distance Gain']
        self.qsObj.msp_formation_config['area_gain'] = self.userSettingData['Topology']['Area Gain']
        self.qsObj.msp_formation_config['lat_gain'] = self.userSettingData['Topology']['Lat Gain']
        self.qsObj.msp_formation_config['lon_gain'] = self.userSettingData['Topology']['Lon Gain']
        self.qsObj.msp_formation_config['graph_type'] = self.userSettingData['Topology']['Graph Type']
        self.qsObj.msp_formation_config['identity'] = self.userSettingData['Topology']['Identity']
        self.qsObj.msp_formation_config['d_ji'] = self.userSettingData['Topology']['d_ji']
        self.qsObj.msp_formation_config['d_ki'] = self.userSettingData['Topology']['d_ki']
        self.qsObj.msp_formation_config['d_kj'] = self.userSettingData['Topology']['d_kj']
        dji = self.userSettingData['Topology']['d_ji']
        dki = self.userSettingData['Topology']['d_ki']
        dkj = self.userSettingData['Topology']['d_kj']
        self.qsObj.msp_formation_config['ad'] = int(math.sqrt(-math.pow(dji,4)
                                                              -math.pow(dki,4)
                                                              -math.pow(dkj,4)
                                                              +2.0*math.pow(dji,2)*math.pow(dki,2)
                                                              +2.0*math.pow(dji,2)*math.pow(dkj,2)
                                                              +2.0*math.pow(dki,2)*math.pow(dkj,2))/4.0)
        print(self.qsObj.msp_formation_config)





    def loadValuesFromDefault(self):
        self.defaultSettingData = readDefaultSettingFile()

    def loadValuesFromUserSaved(self):
        self.userSettingData = readUserSettingFile()

    def initValues(self):
        self.loadValuesFromDefault()
        # self.setUIDefaultValues()
        self.userSettingData = dict(self.defaultSettingData)
        self.setUIValues()

    # Set UI widget values with userSettingData
    def setUIValues(self):
        self.topologySettings['Current Telemetry Address'].clear()
        self.topologySettings['Current Telemetry Address'].addItems(self.userSettingData['Topology']['Address Options'])
        self.topologySettings['Current Telemetry Address'].setCurrentIndex(self.userSettingData['Topology']['Current Telemetry Address'])

        self.topologySettings['Telemetry Source Type'].clear()
        self.topologySettings['Telemetry Source Type'].addItems(self.userSettingData['Topology']['Telemetry Source Type Options'])
        self.topologySettings['Telemetry Source Type'].setCurrentIndex(self.userSettingData['Topology']['Telemetry Source Type'])

        self.topologySettings['Telemetry Destination Type'].clear()
        self.topologySettings['Telemetry Destination Type'].addItems(self.userSettingData['Topology']['Telemetry Destination Type Options'])
        self.topologySettings['Telemetry Destination Type'].setCurrentIndex(self.userSettingData['Topology']['Telemetry Destination Type'])

        for i in range(3):
            self.topologySettings['Telemetry Source Address '+str(i)].clear()
            self.topologySettings['Telemetry Source Address '+str(i)].addItems(self.userSettingData['Topology']['Address Options'])
            self.topologySettings['Telemetry Source Address '+str(i)].setCurrentIndex(self.userSettingData['Topology']['Telemetry Source Address'][i])
            self.topologySettings['Telemetry Destination Address '+str(i)].clear()
            self.topologySettings['Telemetry Destination Address '+str(i)].addItems(self.userSettingData['Topology']['Address Options'])
            self.topologySettings['Telemetry Destination Address '+str(i)].setCurrentIndex(self.userSettingData['Topology']['Telemetry Destination Address'][i])

        self.topologySettings['Current Remote Control Address'].clear()
        self.topologySettings['Current Remote Control Address'].addItems(self.userSettingData['Topology']['Address Options'])
        self.topologySettings['Current Remote Control Address'].setCurrentIndex(self.userSettingData['Topology']['Current Remote Control Address'])

        self.topologySettings['Remote Control Source Address'].clear()
        self.topologySettings['Remote Control Source Address'].addItems(self.userSettingData['Topology']['Address Options'])
        self.topologySettings['Remote Control Source Address'].setCurrentIndex(self.userSettingData['Topology']['Remote Control Source Address'])

        # Formation Configure
        self.sketchSettings['dji'].setValue(self.userSettingData['Topology']['d_ji'])
        self.sketchSettings['dki'].setValue(self.userSettingData['Topology']['d_ki'])
        self.sketchSettings['dkj'].setValue(self.userSettingData['Topology']['d_kj'])
        self.sketchSettings['Graph Type'].setCurrentIndex(self.userSettingData['Topology']['Graph Type'])
        self.sketchSettings['Identity'].setCurrentIndex(self.userSettingData['Topology']['Identity'])
        self.sketchSettings['Distance Gain'].setValue(self.userSettingData['Topology']['Distance Gain'])
        self.sketchSettings['Area Gain'].setValue(self.userSettingData['Topology']['Area Gain'])
        self.sketchSettings['Lat Gain'].setValue(self.userSettingData['Topology']['Lat Gain'])
        self.sketchSettings['Lon Gain'].setValue(self.userSettingData['Topology']['Lon Gain'])
        self.sketchSettings['Flight Height'].setValue(self.userSettingData['Topology']['Flight Height'])

    # Transfer values from qsObj to userSettingData
    def setValues(self):
        # From qsObj msp_formation_config to userSettingData
        # XBEE Self Telemetry Address
        # xbee_self_tele_addr = self.qsObj.msp_xbee_self_telemetry_addr
        xbee_self_tele_addr = self.qsObj.msp_network_config['selfTeleAddressLow']
        xbee_self_tele_addr_str = '{:08x}'.format(xbee_self_tele_addr).upper()
        xbee_self_tele_addr_ind = self.userSettingData['Topology']['Address Options'].index(xbee_self_tele_addr_str)
        self.userSettingData['Topology']['Current Telemetry Address'] = xbee_self_tele_addr_ind

        # self.userSettingData['Topology']['Telemetry Source Type']
        # self.userSettingData['Topology']['Telemetry Destination Type']
        # for i in range(3):
        #     # Telemetry Source Addresses
        #     xbee_tele_source_addr = self.qsObj.msp_xbee_telemetry_source_addr[i]
        #     xbee_tele_source_addr_str = '{:08x}'.format(xbee_tele_source_addr).upper()
        #     xbee_tele_source_addr_ind = self.userSettingData['Topology']['Address Options'].index(xbee_tele_source_addr_str)
        #     self.userSettingData['Topology']['Telemetry Source Address'][i] = xbee_tele_source_addr_ind
        #     # Telemetry Destination Addresses
        #     xbee_tele_destination_addr = self.qsObj.msp_xbee_telemetry_destination_addr[i]
        #     xbee_tele_destination_addr_str = '{:08x}'.format(xbee_tele_destination_addr).upper()
        #     xbee_tele_destination_addr_ind = self.userSettingData['Topology']['Address Options'].index(xbee_tele_destination_addr_str)
        #     self.userSettingData['Topology']['Telemetry Destination Address'][i] = xbee_tele_destination_addr_ind

        # Telemetry Source 1 Addresses
        xbee_tele_source_1_addr = self.qsObj.msp_network_config['teleSource1AddressLow']
        xbee_tele_source_1_addr_str = '{:08x}'.format(xbee_tele_source_1_addr).upper()
        xbee_tele_source_1_addr_ind = self.userSettingData['Topology']['Address Options'].index(xbee_tele_source_1_addr_str)
        self.userSettingData['Topology']['Telemetry Source Address'][0] = xbee_tele_source_1_addr_ind
        # Telemetry Destination 1 Addresses
        xbee_tele_destination_1_addr = self.qsObj.msp_network_config['teleDestination1AddressLow']
        xbee_tele_destination_1_addr_str = '{:08x}'.format(xbee_tele_destination_1_addr).upper()
        xbee_tele_destination_1_addr_ind = self.userSettingData['Topology']['Address Options'].index(xbee_tele_destination_1_addr_str)
        self.userSettingData['Topology']['Telemetry Destination Address'][0] = xbee_tele_destination_1_addr_ind

        # Telemetry Source 2 Addresses
        xbee_tele_source_2_addr = self.qsObj.msp_network_config['teleSource2AddressLow']
        xbee_tele_source_2_addr_str = '{:08x}'.format(xbee_tele_source_2_addr).upper()
        xbee_tele_source_2_addr_ind = self.userSettingData['Topology']['Address Options'].index(xbee_tele_source_2_addr_str)
        self.userSettingData['Topology']['Telemetry Source Address'][1] = xbee_tele_source_2_addr_ind
        # Telemetry Destination 2 Addresses
        xbee_tele_destination_2_addr = self.qsObj.msp_network_config['teleDestination2AddressLow']
        xbee_tele_destination_2_addr_str = '{:08x}'.format(xbee_tele_destination_2_addr).upper()
        xbee_tele_destination_2_addr_ind = self.userSettingData['Topology']['Address Options'].index(xbee_tele_destination_2_addr_str)
        self.userSettingData['Topology']['Telemetry Destination Address'][1] = xbee_tele_destination_2_addr_ind

        # Telemetry Source 3 Addresses
        xbee_tele_source_3_addr = self.qsObj.msp_network_config['teleSource3AddressLow']
        xbee_tele_source_3_addr_str = '{:08x}'.format(xbee_tele_source_3_addr).upper()
        xbee_tele_source_3_addr_ind = self.userSettingData['Topology']['Address Options'].index(xbee_tele_source_3_addr_str)
        self.userSettingData['Topology']['Telemetry Source Address'][2] = xbee_tele_source_3_addr_ind
        # Telemetry Destination 3 Addresses
        xbee_tele_destination_3_addr = self.qsObj.msp_network_config['teleDestination3AddressLow']
        xbee_tele_destination_3_addr_str = '{:08x}'.format(xbee_tele_destination_3_addr).upper()
        xbee_tele_destination_3_addr_ind = self.userSettingData['Topology']['Address Options'].index(xbee_tele_destination_3_addr_str)
        self.userSettingData['Topology']['Telemetry Destination Address'][2] = xbee_tele_destination_3_addr_ind

        # Remote Control Self Address
        # xbee_self_rc_addr = self.qsObj.msp_xbee_self_rc_addr
        xbee_self_rc_addr = self.qsObj.msp_network_config['selfRemoteAddressLow']
        xbee_self_rc_addr_str = '{:08x}'.format(xbee_self_rc_addr).upper()
        xbee_self_rc_addr_ind = self.userSettingData['Topology']['Address Options'].index(xbee_self_rc_addr_str)
        self.userSettingData['Topology']['Current Remote Control Address'] = xbee_self_rc_addr_ind
        # Remote Control Source Address
        # xbee_rc_source_addr = self.qsObj.msp_xbee_rc_source_addr
        xbee_rc_source_addr = self.qsObj.msp_network_config['remoteSourceAddressLow']
        xbee_rc_source_addr_str = '{:08x}'.format(xbee_rc_source_addr).upper()
        xbee_rc_source_addr_ind = self.userSettingData['Topology']['Address Options'].index(xbee_rc_source_addr_str)
        self.userSettingData['Topology']['Remote Control Source Address'] = xbee_rc_source_addr_ind

        # Formation
        self.userSettingData['Topology']['d_ji'] = self.qsObj.msp_formation_config['d_ji']
        self.userSettingData['Topology']['d_ki'] = self.qsObj.msp_formation_config['d_ki']
        self.userSettingData['Topology']['d_kj'] = self.qsObj.msp_formation_config['d_kj']
        self.userSettingData['Topology']['Graph Type'] = self.qsObj.msp_formation_config['graph_type']
        self.userSettingData['Topology']['Identity'] = self.qsObj.msp_formation_config['identity']
        self.userSettingData['Topology']['Distance Gain'] = self.qsObj.msp_formation_config['distance_gain']
        self.userSettingData['Topology']['Area Gain'] = self.qsObj.msp_formation_config['area_gain']
        self.userSettingData['Topology']['Lat Gain'] = self.qsObj.msp_formation_config['lat_gain']
        self.userSettingData['Topology']['Lon Gain'] = self.qsObj.msp_formation_config['lon_gain']
        self.userSettingData['Topology']['Flight Height'] = self.qsObj.msp_formation_config['flight_height']

        # Update UI values
        self.setUIValues()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = TopologyWidget()
    form.resize(1080,720)
    form.show()
    app.exec_()
