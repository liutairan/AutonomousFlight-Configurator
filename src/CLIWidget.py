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
from random import *
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
    QListWidget, QListWidgetItem, QAbstractItemView, QWidget, QAction,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QHeaderView, QLabel, QTreeWidget, QTreeWidgetItem, QToolBar, QLineEdit,
    QCompleter, QSizePolicy, QComboBox, QMessageBox, QDialog, QDialogButtonBox,
    QFileDialog, QGridLayout, QFormLayout, QRadioButton, QPlainTextEdit)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QEvent

class CLIWidget(QWidget):
    cliSignal = pyqtSignal(str)
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.initUI()
        self.inputHistory = []
        self.currentInputIndex = 0

    def initUI(self):
        self.bundle_dir = os.path.dirname(os.path.abspath(__file__))
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)

        self.cliTextEdit = QPlainTextEdit("CLI mode, type 'exit' to return, or 'help'\n\n")
        self.cliTextEdit.setStyleSheet("QPlainTextEdit {background-color:gray; color:white; min-height:590; max-height:600}")
        self.cliInputLine = QLineEdit()
        self.cliInputLine.installEventFilter(self)
        self.cliInputLine.returnPressed.connect(self.newInputReceived)

        self.layout.addWidget(self.cliTextEdit)
        self.layout.addWidget(self.cliInputLine)
        self.layout.addStretch(1)

        # Set Main Layout of this page
        self.setLayout(self.layout)

    # QEvent http://doc.qt.io/qt-5/qevent.html
    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and source is self.cliInputLine:
            self.keyPressed(event)
        # if event.type() == QEvent.FocusIn and source is self.cliInputLine:
        #     print("A")
        return super(QWidget, self).eventFilter(source, event)

    def keyPressed(self, event):
        flag = False
        if event.key() == Qt.Key_Up:
            if self.currentInputIndex < len(self.inputHistory):
                self.currentInputIndex = self.currentInputIndex + 1
                flag = True
        elif event.key() == Qt.Key_Down:
            if self.currentInputIndex > 0:
                self.currentInputIndex = self.currentInputIndex - 1
                flag = True
        if flag:
            if self.currentInputIndex > 0:
                self.cliInputLine.setText(self.inputHistory[-self.currentInputIndex])
            elif self.currentInputIndex == 0:
                self.cliInputLine.setText("")

    def newInputReceived(self):
        waitingText = self.cliInputLine.text()
        if len(waitingText) > 0:
            self.cliTextEdit.appendPlainText("$" + waitingText)
            self.inputHistory.append(waitingText)
            self.currentInputIndex = 0
            self.cliInputLine.setText("")
            # Check waitingText valid or not
            (vFlag, checkedPhrase) = self.validationInput(waitingText)
            if vFlag == True:
                self.cliSignal.emit(checkedPhrase)

    def validationInput(self, phrase):
        validFlag = False
        retPhrase = ""
        cmdList = ["adjrange", "aux", "mmix", "smix", "color", "defaults",
                   "diff", "dump", "exit", "feature", "get", "gpspassthrough",
                   "help", "led", "map", "mixer", "motor", "play_sound",
                   "profile", "rxrange", "save", "serialpassthrough", "set",
                   "status", "version", "um", "dm"]
        if len(phrase) > 0:
            tempList1 = phrase.split(" ")
            tempList2 = [t for t in tempList1 if t not in ('')]
            if tempList2[0] in cmdList:
                validFlag = True
                retPhrase = " ".join(tempList2)
        return (validFlag, retPhrase)

    def processFeedback(self, feedbackStr):
        self.cliTextEdit.appendPlainText(feedbackStr)
