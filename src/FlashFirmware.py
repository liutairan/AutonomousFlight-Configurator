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

import os, sys
import subprocess
import json
import time

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QSize, Qt, QTimer

try:
    to_unicode = unicode
except NameError:
    to_unicode = str

# Need to connet two pins of the bootloader to flash the firmware if using UART.
class FlashFirmware(QWidget):
    progressChangedSignal = pyqtSignal(str)
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.flashToolPath = ""
        self.loadFlashToolPath()
        self.baudrate = 115200
        self.mode = "8e1"
        self.firmwarePath = ""
        self.deviceName = "/dev/tty.SLAB_USBtoUART"

    def loadFlashToolPath(self):
        with open('BootloaderConfigure.json') as data_file:
            data_loaded = json.load(data_file)
            self.flashToolPath = data_loaded['Path']

    def getDeviceInfo(self):
        # Get device information:
        #     stm32flash /dev/ttyS0
        # or:
        #     stm32flash /dev/i2c-0
        command = self.flashToolPath + " -b " + str(self.baudrate) + " -m " + self.mode + " " + self.deviceName
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            out = process.stdout.read(1)
            if out == b'' and process.poll() != None:
                break
            if out != b'':
                sys.stdout.write(out.decode("utf-8"))
                sys.stdout.flush()

    def readFlashToFile(self):
        # Read flash to file:
        #     stm32flash -r filename /dev/ttyS0
        pass

    def readFlashToStdout(self):
        # Read 100 bytes of flash from 0x1000 to stdout:
        #     stm32flash -r - -S 0x1000:100 /dev/ttyS0
        pass

    # def writeWithVerifyAndStartExecution(self):
    #     # Write with verify and then start execution:
    #     #     stm32flash -w filename -v -g 0x0 /dev/ttyS0
    #     self.firmwarePath = "/Users/liutairan/Dropbox/Code/AutonomousFlight/obj/AutonomousFlight_1.9.1_SPRACINGF3.hex"
    #     commandFields = [self.flashToolPath, "-b", str(self.baudrate), "-m", self.mode, "-w", self.firmwarePath, "-v", "-g", "0x0", self.deviceName]
    #     command = " ".join(commandFields)
    #     process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #
    #     buff = []
    #     warnSaveFlag = False
    #     saveFlag = False
    #     printFlag = False
    #     while True:
    #         out = process.stdout.read(1)
    #         if out != b'':
    #             # print([out.decode("utf-8")])
    #             tempCharDecode = out.decode("utf-8")
    #             if tempCharDecode == "a" and saveFlag == False:
    #                 warnSaveFlag = True
    #                 continue
    #             if warnSaveFlag == True:
    #                 if tempCharDecode == "d" and saveFlag == False:
    #                     saveFlag = True
    #                 else:
    #                     warnSaveFlag = False
    #             if tempCharDecode == ")":
    #                 warnSaveFlag = False
    #                 saveFlag = False
    #             if tempCharDecode == "\r":
    #                 printFlag = True
    #             if tempCharDecode == " ":
    #                 printFlag = True
    #
    #             if saveFlag == True:
    #                 buff.append(tempCharDecode)
    #
    #             if printFlag == True:
    #                 if len(buff) > 0:
    #                     if buff[0] == "(":
    #                         printString = "".join(buff[1:])
    #                         self.progressChangedSignal.emit(printString)
    #                 # print(buff)
    #                 printFlag = False
    #                 buff = []
    #         if out == b'' and process.poll() != None:
    #             break

    # The above write function will cause the progress bar not update during the
    #    flash process. Using the function below can update the progress bar
    #    every step when the progress value changed.
    def writeWithVerifyAndStartExecution(self):
        print("Write with Verify")
        # Write with verify and then start execution:
        #     stm32flash -w filename -v -g 0x0 /dev/ttyS0
        self.firmwarePath = "/Users/liutairan/Dropbox/Code/AutonomousFlight/obj/AutonomousFlight_2.0.1_SPRACINGF3.hex"
        commandFields = [self.flashToolPath, "-b", str(self.baudrate), "-m", self.mode, "-w", self.firmwarePath, "-v", "-g", "0x0", self.deviceName]
        command = " ".join(commandFields)
        self.process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self.buff = []
        self.warnSaveFlag = False
        self.saveFlag = False
        self.printFlag = False

        self.sched = QTimer()
        self.sched.timeout.connect(self.processCharacter)

    def processCharacter(self):
        out = self.process.stdout.read(1)
        if out != b'':
            # print([out.decode("utf-8")])
            tempCharDecode = out.decode("utf-8")
            if tempCharDecode == "a" and self.saveFlag == False:
                self.warnSaveFlag = True
                return
            if self.warnSaveFlag == True:
                if tempCharDecode == "d" and self.saveFlag == False:
                    self.saveFlag = True
                else:
                    self.warnSaveFlag = False
            if tempCharDecode == ")":
                self.warnSaveFlag = False
                self.saveFlag = False
            if tempCharDecode == "\r":
                self.printFlag = True
            if tempCharDecode == " ":
                self.printFlag = True

            if self.saveFlag == True:
                self.buff.append(tempCharDecode)

            if self.printFlag == True:
                if len(self.buff) > 0:
                    if self.buff[0] == "(":
                        printString = "".join(self.buff[1:])
                        self.progressChangedSignal.emit(printString)
                # print(self.buff)
                self.printFlag = False
                self.buff = []
        if out == b'' and self.process.poll() != None:
            self.sched.stop()
            pass

    def startExecution(self):
        # Start execution:
        #     stm32flash -g 0x0 /dev/ttyS0
        pass

    def gpioSequence(self):
        # GPIO sequence:
        # - entry sequence: GPIO_3=low, GPIO_2=low, GPIO_2=high
        # - exit sequence: GPIO_3=high, GPIO_2=low, GPIO_2=high
        #     stm32flash -R -i -3,-2,2:3,-2,2 /dev/ttyS0
        pass

    def sendoutDataSimulate(self):
        for i in range(101):
            printString = str(i)+"%"
            self.progressChangedSignal.emit(printString)
            time.sleep(0.1)

    def sendoutDataSimulate(self):
        self.sched = QTimer()
        self.value = 0
        self.sched.timeout.connect(self.generateData)

    def start(self):
        self.sched.start(1)

    def generateData(self):
        if self.value < 100:
            self.value = self.value + 1
            printString = str(self.value)+"%"
            self.progressChangedSignal.emit(printString)



if __name__ == "__main__":
    flashHandle = FlashFirmware()
    # flashHandle.getDeviceInfo()
    flashHandle.writeWithVerifyAndStartExecution()
