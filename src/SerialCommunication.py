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

import serial, time, struct

class SerialCommunication:
    def __init__(self, serPort):
        self.elapsed = 0
        self.PRINT = 1

        self.ser = serial.Serial()
        self.ser.port = serPort
        self.ser.baudrate = 115200
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout = 0.01
        self.ser.xonxoff = False
        self.ser.rtscts = False
        self.ser.dsrdtr = False
        self.ser.writeTimeout = 2
        """Time to wait until the board becomes operational"""
        wakeup = 2
        try:
            self.ser.open()
            if self.PRINT:
                print("Waking up board on "+self.ser.port+"...")
            for i in range(1,wakeup):
                if self.PRINT:
                    print(wakeup-i)
                    time.sleep(1)
                else:
                    time.sleep(1)
        except serial.serialutil.SerialException:
            print(serial.serialutil.SerialException)
            #print("\n\nError opening "+self.ser.port+" port.\n"+str(error)+"\n\n")

    def flushSerial(self):
        self.ser.flushInput()
        self.ser.flushOutput()

    def stopDevice(self):
        self.ser.close()

    def readData(self):
        tempData = self.ser.readlines()
        tempData2 = b''.join(tempData)
        return tempData2

    def writeData(self, tempData):
        try:
            self.ser.write(tempData)
        except serial.serialutil.SerialException:
            print(serial.serialutil.SerialException)
