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
from random import *
from PyQt5.QtWidgets import (QApplication)
from PyQt5.QtGui import QIcon

from MainWindow import App

def getScreenResolution(appHandle):
    screenRect = appHandle.desktop().screenGeometry()
    width = screenRect.width()
    height = screenRect.height()
    return (width, height)

def chooseWindowSize(width, height):
    windowWidth = width
    windowHeight = height
    if width <= 1280:
        windowWidth = 1080
    elif width == 1920:
        windowWidth = 1440
    if height <= 800:
        windowHeight = 720
    elif height == 1080:
        windowHeight = 900
    return (windowWidth, windowHeight)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Pics', 'icon.png')
    app.setWindowIcon(QIcon(path))
    (width, height) = getScreenResolution(app)
    (windowWidth, windowHeight) = chooseWindowSize(width, height)
    mainWindow = App(windowWidth, windowHeight)
    sys.exit(app.exec_())
