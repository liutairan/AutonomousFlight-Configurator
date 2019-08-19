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

import serial, time, struct
import re
import multiprocessing
import threading
from PyQt5.QtCore import QObject, pyqtSignal
from QuadStates import QuadStates

class MSPv1(QObject):
    # MSPv1 MSP Commands
    MSP_PROTOCOL_VERSION = 0
    MSP_API_VERSION = 1
    MSP_FC_VARIANT = 2
    MSP_FC_VERSION = 3
    MSP_BOARD_INFO = 4
    MSP_BUILD_INFO = 5

    MSP_INAV_PID = 6
    MSP_SET_INAV_PID = 7

    MSP_NAME = 10
    MSP_SET_NAME = 11

    MSP_NAV_POSHOLD = 12
    MSP_SET_NAV_POSHOLD = 13

    MSP_CALIBRATION_DATA = 14
    MSP_SET_CALIBRATION_DATA = 15

    MSP_POSITION_ESTIMATION_CONFIG = 16
    MSP_SET_POSITION_ESTIMATION_CONFIG = 17

    MSP_WP_MISSION_LOAD = 18
    MSP_WP_MISSION_SAVE = 19
    MSP_WP_GETINFO = 20

    MSP_RTH_AND_LAND_CONFIG = 21
    MSP_SET_RTH_AND_LAND_CONFIG = 22
    MSP_FW_CONFIG = 23
    MSP_SET_FW_CONFIG = 24

    MSP_MODE_RANGES = 34    # MSP_MODE_RANGES    out message         Returns all mode ranges
    MSP_SET_MODE_RANGE = 35 # MSP_SET_MODE_RANGE in message          Sets a single mode range

    MSP_FEATURE = 36
    MSP_SET_FEATURE = 37

    MSP_BOARD_ALIGNMENT = 38
    MSP_SET_BOARD_ALIGNMENT = 39

    MSP_CURRENT_METER_CONFIG = 40
    MSP_SET_CURRENT_METER_CONFIG = 41

    MSP_MIXER = 42
    MSP_SET_MIXER = 43

    MSP_RX_CONFIG = 44
    MSP_SET_RX_CONFIG = 45

    MSP_LED_COLORS = 46
    MSP_SET_LED_COLORS = 47

    MSP_RSSI_CONFIG = 50
    MSP_SET_RSSI_CONFIG = 51

    MSP_ADJUSTMENT_RANGES = 52
    MSP_SET_ADJUSTMENT_RANGE = 53

    MSP_CF_SERIAL_CONFIG = 54
    MSP_SET_CF_SERIAL_CONFIG = 55

    MSP_VOLTAGE_METER_CONFIG = 56
    MSP_SET_VOLTAGE_METER_CONFIG = 57

    MSP_SONAR_ALTITUDE = 58      # SONAR cm

    MSP_PID_CONTROLLER = 59
    MSP_SET_PID_CONTROLLER = 60

    MSP_ARMING_CONFIG = 61         # out message         Returns auto_disarm_delay and disarm_kill_switch parameters
    MSP_SET_ARMING_CONFIG = 62     # in message          Sets auto_disarm_delay and disarm_kill_switch parameters

    MSP_RX_MAP = 64
    MSP_SET_RX_MAP = 65

    MSP_BF_CONFIG = 66
    MSP_SET_BF_CONFIG = 67

    MSP_REBOOT = 68    # in message reboot settings

    MSP_DATAFLASH_SUMMARY = 70 # out message - get description of dataflash chip
    MSP_DATAFLASH_READ = 71 # out message - get content of dataflash chip
    MSP_DATAFLASH_ERASE = 72 # in message - erase dataflash chip

    MSP_LOOP_TIME = 73 # out message         Returns FC cycle time i.e looptime parameter
    MSP_SET_LOOP_TIME = 74 # in message          Sets FC cycle time i.e looptime parameter

    MSP_FAILSAFE_CONFIG = 75 # out message         Returns FC Fail-Safe settings
    MSP_SET_FAILSAFE_CONFIG = 76 #in message          Sets FC Fail-Safe settings

    MSP_RXFAIL_CONFIG = 77 # out message         Returns RXFAIL settings
    MSP_SET_RXFAIL_CONFIG = 78 # in message          Sets RXFAIL settings

    MSP_SDCARD_SUMMARY = 79 # out message         Get the state of the SD card

    MSP_BLACKBOX_CONFIG = 80 # out message         Get blackbox settings
    MSP_SET_BLACKBOX_CONFIG = 81 # in message          Set blackbox settings

    MSP_TRANSPONDER_CONFIG = 82 # out message         Get transponder settings
    MSP_SET_TRANSPONDER_CONFIG = 83 # in message          Set transponder settings

    MSP_OSD_CONFIG = 84 # out message         Get osd settings - betaflight
    MSP_SET_OSD_CONFIG = 85 # in message          Set osd settings - betaflight

    MSP_OSD_CHAR_READ = 86 # out message         Get osd settings - betaflight
    MSP_OSD_CHAR_WRITE = 87 # in message          Set osd settings - betaflight

    MSP_VTX_CONFIG = 88 # out message         Get vtx settings - betaflight
    MSP_SET_VTX_CONFIG = 89 # in message          Set vtx settings - betaflight

    # Betaflight Additional Commands
    MSP_ADVANCED_CONFIG = 90
    MSP_SET_ADVANCED_CONFIG = 91

    MSP_FILTER_CONFIG = 92
    MSP_SET_FILTER_CONFIG = 93

    MSP_PID_ADVANCED = 94
    MSP_SET_PID_ADVANCED = 95

    MSP_SENSOR_CONFIG = 96
    MSP_SET_SENSOR_CONFIG = 97

    MSP_SPECIAL_PARAMETERS = 98 # Temporary betaflight parameters before cleanup and keep CF compatibility
    MSP_SET_SPECIAL_PARAMETERS = 99 # Temporary betaflight parameters before cleanup and keep CF compatibility

    # OSD specific
    MSP_OSD_VIDEO_CONFIG = 180
    MSP_SET_OSD_VIDEO_CONFIG = 181

    MSP_DISPLAYPORT = 182

    MSP_SET_TX_INFO = 186 # in message           Used to send runtime information from TX lua scripts to the firmware
    MSP_TX_INFO = 187 # out message          Used by TX lua scripts to read information from the firmware

    # XBEE Settings 130-149, 230-238
    MSP_XBEE_SELF_TELEMETRY_ADDR = 130
    MSP_SET_XBEE_SELF_TELEMETRY_ADDR = 230

    MSP_XBEE_TELEMETRY_SOURCE_ADDR = 131
    MSP_SET_XBEE_TELEMETRY_SOURCE_ADDR = 231

    MSP_XBEE_TELEMETRY_DESTINATION_ADDR = 132
    MSP_SET_XBEE_TELEMETRY_DESTINATION_ADDR = 232

    MSP_XBEE_SELF_RC_ADDR = 133
    MSP_SET_XBEE_SELF_RC_ADDR = 233

    MSP_XBEE_RC_SOURCE_ADDR = 134
    MSP_SET_XBEE_RC_SOURCE_ADDR = 234

    MSP_FORMATION_CONFIG = 135
    MSP_SET_FORMATION_CONFIG = 235

    MSP_NETWORK_CONFIG = 136
    MSP_SET_NETWORK_CONFIG = 236

    MSP_IDENT = 100
    MSP_STATUS = 101
    MSP_RAW_IMU = 102
    MSP_SERVO = 103
    MSP_MOTOR = 104
    MSP_RC = 105
    MSP_RAW_GPS = 106
    MSP_COMP_GPS = 107
    MSP_ATTITUDE = 108
    MSP_ALTITUDE = 109
    MSP_ANALOG = 110
    MSP_RC_TUNING = 111
    MSP_PID = 112
    MSP_ACTIVEBOXES = 113
    MSP_MISC = 114
    MSP_MOTOR_PINS = 115
    MSP_BOXNAMES = 116
    MSP_PIDNAMES = 117
    MSP_WP = 118
    MSP_BOXIDS = 119
    MSP_SERVO_CONFIGURATIONS = 120
    MSP_NAV_STATUS = 121
    MSP_NAV_CONFIG = 122
    MSP_3D = 124
    MSP_RC_DEADBAND = 125
    MSP_SENSOR_ALIGNMENT = 126
    MSP_LED_STRIP_MODECOLOR = 127

    MSP_STATUS_EX = 150    # out message         cycletime, errors_count, CPU load, sensor present etc
    MSP_SENSOR_STATUS = 151    # out message         Hardware sensor status
    MSP_UID = 160    # out message         Unique device ID

    MSP_GPSSVINFO = 164
    MSP_GPSSTATISTICS = 166

    MSP_SET_RAW_RC = 200
    MSP_SET_RAW_GPS = 201  # in message          fix, numsat, lat, lon, alt, speed
    MSP_SET_PID = 202      # in message          P I D coeff (9 are used currently)
    MSP_SET_BOX = 203
    MSP_SET_RC_TUNING = 204
    MSP_ACC_CALIBRATION = 205
    MSP_MAG_CALIBRATION = 206
    MSP_SET_MISC = 207
    MSP_RESET_CONF = 208
    MSP_SET_WP = 209
    MSP_SELECT_SETTING = 210
    MSP_SET_HEAD = 211
    MSP_SET_SERVO_CONFIGURATION = 212
    MSP_SET_MOTOR = 214
    MSP_SET_NAV_CONFIG = 215
    MSP_SET_3D = 217
    MSP_SET_RC_DEADBAND = 218
    MSP_SET_RESET_CURR_PID = 219
    MSP_SET_SENSOR_ALIGNMENT = 220
    MSP_SET_LED_STRIP_MODECOLOR = 221

    MSP_ACC_TRIM = 240    # out message         get acc angle trim values
    MSP_SET_ACC_TRIM = 239    # in message          set acc angle trim values
    MSP_SERVO_MIX_RULES = 241    # out message         Returns servo mixer configuration
    MSP_SET_SERVO_MIX_RULE = 242    # in message          Sets servo mixer configuration
    MSP_SET_4WAY_IF = 245    # in message          Sets 4way interface
    MSP_RTC = 246
    MSP_SET_RTC = 247

    MSP_EEPROM_WRITE = 250
    MSP_RESERVE_1 = 251
    MSP_RESERVE_2 = 252
    MSP_DEBUGMSG = 253
    MSP_DEBUG = 254
    MSP_V2_FRAME = 255

    #dataUpdateSignal = pyqtSignal(QuadStates)
    cliFeedbackSignal = pyqtSignal(str)
    calibrationFeedbackSignal = pyqtSignal()
    overviewDataUpdateSignal = pyqtSignal(int)
    sensorDataUpdateSignal = pyqtSignal(int)
    motorDataUpdateSignal = pyqtSignal(int)
    headerDataUpdateSignal = pyqtSignal(int)
    modeRCDataUpdateSignal = pyqtSignal(int)
    rebootSignal = pyqtSignal()
    serTerFeedbackSignal = pyqtSignal(str)

    """Class initialization"""
    def __init__(self, serialHandle, qsObj):
        super(MSPv1, self).__init__()
        self.serialHandle = serialHandle
        self.qsObj = qsObj

    # Using, Checked
    def constructSendPacket(self, data_length, send_code, send_data):
        checksum = 0
        total_data = ['$', 'M', '<', data_length, send_code] + send_data
        cmd = send_code

        if data_length == 0:
            byteStr = struct.pack('<2B', *total_data[3:len(total_data)])
            for i in "".join( chr(x) for x in byteStr):
                checksum = checksum ^ ord(i)
            total_data.append(checksum)
            try:
                tempList = []
                for i in range(3):
                    tempList.append(total_data[i].encode('ascii'))
                for i in range(3,len(total_data)):
                    tempList.append(total_data[i])
                tempData = struct.pack('<3c3B', *tempList)
                return tempData
            except (Exception, error):
                print(Exception, error)
        elif data_length > 0:
            if cmd == MSPv1.MSP_SET_RAW_RC:
                byteStr = struct.pack('<2B%dH' % len(send_data), *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B%dHB' % len(send_data), *tempList)
                    return tempData
                except (Exception, error):
                    pass
            elif cmd == MSPv1.MSP_WP:
                byteStr = struct.pack('<3B', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c4B', *tempList)
                    return tempData
                except (Exception, error):
                    print(error)
            elif cmd == MSPv1.MSP_SET_WP:
                byteStr = struct.pack('<2B2B3i3hB', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c4B3i3h2B', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_MODE_RANGE:
                byteStr = struct.pack('<7B', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c8B', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_CALIBRATION_DATA:
                byteStr = struct.pack('<2B9h', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B9hB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_CF_SERIAL_CONFIG:
                byteStr = struct.pack('<2BBH4BBH4BBH4B', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2BBH4BBH4BBH4BB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_MIXER:
                byteStr = struct.pack('<2BB', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2BBB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_ARMING_CONFIG:
                byteStr = struct.pack('<2B2B', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B2BB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_LOOP_TIME:
                byteStr = struct.pack('<2Bh', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2BhB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_BOARD_ALIGNMENT:
                byteStr = struct.pack('<2B3h', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B3hB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_SENSOR_ALIGNMENT:
                byteStr = struct.pack('<2B3B', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B3BB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_RX_CONFIG:
                byteStr = struct.pack('<2BB3HB2H2BHBI3B', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2BB3HB2H2BHBI3BB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_SENSOR_CONFIG:
                byteStr = struct.pack('<2B6B', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B6BB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_MISC:
                byteStr = struct.pack('<2B5H6Bh4B', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B5H6Bh4BB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_3D:
                byteStr = struct.pack('<2B3H', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B3HB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_NAME:
                byteStr = struct.pack('<2B%dB' % total_data[3], *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B%dBB' % total_data[3], *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_ADVANCED_CONFIG:
                byteStr = struct.pack('<2B4B2HB', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B4B2HBB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_INAV_PID:
                byteStr = struct.pack('<2BB2H2BH6B', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2BB2H2BH6BB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_CURRENT_METER_CONFIG:
                byteStr = struct.pack('<2B2HBH', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B2HBHB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_FAILSAFE_CONFIG:
                byteStr = struct.pack('<2B2BHBH2B5HB', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B2BHBH2B5HBB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_FEATURE:
                byteStr = struct.pack('<2BI', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2BIB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_PID:
                byteStr = struct.pack('<2B%dB' % total_data[3], *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B%dBB' % total_data[3], *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_RC_TUNING:
                byteStr = struct.pack('<2B8BHB', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B8BHBB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_PID_ADVANCED:
                byteStr = struct.pack('<2B3H4BHB2H', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B3H4BHB2HB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_FILTER_CONFIG:
                byteStr = struct.pack('<2BB2H2H2H2H', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2BB2H2H2H2HB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_NAV_POSHOLD:
                byteStr = struct.pack('<2BB4H2BH', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2BB4H2BHB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_RTH_AND_LAND_CONFIG:
                byteStr = struct.pack('<2BH5B6H', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2BH5B6HB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_POSITION_ESTIMATION_CONFIG:
                byteStr = struct.pack('<2B5H2B', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B5H2BB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_XBEE_SELF_TELEMETRY_ADDR:
                byteStr = struct.pack('<2BI', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2BIB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_XBEE_TELEMETRY_SOURCE_ADDR:
                byteStr = struct.pack('<2B3I', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B3IB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_XBEE_TELEMETRY_DESTINATION_ADDR:
                byteStr = struct.pack('<2B3I', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B3IB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_XBEE_SELF_RC_ADDR:
                byteStr = struct.pack('<2BI', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2BIB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_XBEE_RC_SOURCE_ADDR:
                byteStr = struct.pack('<2BI', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2BIB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_FORMATION_CONFIG:
                byteStr = struct.pack('<2B5H2B3HI', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B5H2B3HIB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
            elif cmd == MSPv1.MSP_SET_NETWORK_CONFIG:
                byteStr = struct.pack('<2B9I', *total_data[3:len(total_data)])
                for i in "".join( chr(x) for x in byteStr):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempList = []
                    for i in range(3):
                        tempList.append(total_data[i].encode('ascii'))
                    for i in range(3,len(total_data)):
                        tempList.append(total_data[i])
                    tempData = struct.pack('<3c2B9IB', *tempList)
                    return tempData
                except (Exception, error):
                    print(Exception,error)
        else:
            pass

    # Using, Checked
    def sendPacket(self, packet):
        self.serialHandle.writeData(packet)

    # Using, Checked
    def preCheckPacket(self, packet):
        if len(packet)>5:
            if packet[0:3] == b'$M>':
                packet_length = len(packet)
                data_length = packet[3]
                if data_length+6 <= packet_length:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    # Using, Checked
    def parseReceivedPacket(self, packet):
        validFlag = self.preCheckPacket(packet)
        if validFlag:
            data_length = packet[3]
            rec_cmd = packet[4]
            data = packet[5:5+data_length]
            if rec_cmd == MSPv1.MSP_API_VERSION:
                temp = struct.unpack('<3B', data)
                self.qsObj.msp_api_version['msp_protocol_version'] = temp[0]
                self.qsObj.msp_api_version['api_version_major'] = temp[1]
                self.qsObj.msp_api_version['api_version_minor'] = temp[2]
            elif rec_cmd == MSPv1.MSP_FC_VARIANT:
                temp = struct.unpack('<'+'c'*data_length, data)
                self.qsObj.msp_fc_variant['fc_id'] = ''.join(x.decode('utf-8') for x in temp)
            elif rec_cmd == MSPv1.MSP_FC_VERSION:
                temp = struct.unpack('<3B', data)
                self.qsObj.msp_fc_version['fc_version_major'] = temp[0]
                self.qsObj.msp_fc_version['fc_version_minor'] = temp[1]
                self.qsObj.msp_fc_version['fc_version_patch_level'] = temp[2]
            elif rec_cmd == MSPv1.MSP_BOARD_INFO:
                temp = struct.unpack('<4cH3B'+'B'*(data_length-9), data)
                tempStr = ''.join(x.decode('utf-8') for x in temp[0:4])
                targetLength = temp[7]
                targetName = ''.join(chr(x) for x in temp[8:])
                self.qsObj.msp_board_info['board_identifier'] = tempStr
                self.qsObj.msp_board_info['hardware_revision'] = temp[4]
                self.qsObj.msp_board_info['OSD_support'] = temp[5]
                self.qsObj.msp_board_info['comm_capabilities'] = temp[6]
                self.qsObj.msp_board_info['target_length'] = targetLength
                self.qsObj.msp_board_info['target_name'] = targetName
            elif rec_cmd == MSPv1.MSP_BUILD_INFO:
                temp = struct.unpack('<'+'c'*data_length, data)
                self.qsObj.msp_build_info['build_info'] = ''.join(x.decode('utf-8') for x in temp)
            elif rec_cmd == MSPv1.MSP_IDENT:
                temp = struct.unpack('<3BI', data)
                self.qsObj.msp_ident['version'] = temp[0]
                self.qsObj.msp_ident['multitype'] = temp[1]
                self.qsObj.msp_ident['msp_version'] = temp[2]
                self.qsObj.msp_ident['capability'] = temp[3]
            elif rec_cmd == MSPv1.MSP_SENSOR_STATUS:
                temp = struct.unpack('<9B', data)
                self.qsObj.msp_sensor_status['hardware_health'] = temp[0]
                self.qsObj.msp_sensor_status['gyro'] = temp[1]
                self.qsObj.msp_sensor_status['acc'] = temp[2]
                self.qsObj.msp_sensor_status['comp'] = temp[3]
                self.qsObj.msp_sensor_status['baro'] = temp[4]
                self.qsObj.msp_sensor_status['gps'] = temp[5]
                self.qsObj.msp_sensor_status['range'] = temp[6]
                self.qsObj.msp_sensor_status['pitot'] = temp[7]
                self.qsObj.msp_sensor_status['optical'] = temp[8]
                # HW_SENSOR_NONE          = 0,    // Not selected
                # HW_SENSOR_OK            = 1,    // Selected, detected and healthy (ready to be used)
                # HW_SENSOR_UNAVAILABLE   = 2,    // Selected in configuration but not detected
                # HW_SENSOR_UNHEALTHY     = 3,    // Selected, detected but is reported as not healthy
                #     sbufWriteU8(dst, isHardwareHealthy() ? 1 : 0);
                #     sbufWriteU8(dst, getHwGyroStatus());
                #     sbufWriteU8(dst, getHwAccelerometerStatus());
                #     sbufWriteU8(dst, getHwCompassStatus());
                #     sbufWriteU8(dst, getHwBarometerStatus());
                #     sbufWriteU8(dst, getHwGPSStatus());
                #     sbufWriteU8(dst, getHwRangefinderStatus());
                #     sbufWriteU8(dst, getHwPitotmeterStatus());
                #     sbufWriteU8(dst, getHwOpticalFlowStatus());
            elif rec_cmd == MSPv1.MSP_ACTIVEBOXES:
                temp = struct.unpack('<I', data)
                # tempStr = format(temp[0], '032b')
                self.qsObj.msp_activeboxes = list(temp)
            elif rec_cmd == MSPv1.MSP_STATUS_EX:
                temp = struct.unpack('<3HIB2HB', data)
                self.qsObj.msp_status_ex['cycleTime'] = temp[0]
                self.qsObj.msp_status_ex['i2cError'] = temp[1]
                self.qsObj.msp_status_ex['activeSensors'] = temp[2]
                self.qsObj.msp_status_ex['flightModeFlags'] = temp[3]
                self.qsObj.msp_status_ex['profile'] = temp[4]
                self.qsObj.msp_status_ex['averageSystemLoadPercent'] = temp[5]
                self.qsObj.msp_status_ex['armingFlags'] = temp[6]
                self.qsObj.msp_status_ex['accGetCalibrationAxisFlags'] = temp[7]
            elif rec_cmd == MSPv1.MSP_STATUS:
                temp = struct.unpack('<3HIB', data)
                self.qsObj.msp_status['cycleTime'] = temp[0]
                self.qsObj.msp_status['i2cError'] = temp[1]
                self.qsObj.msp_status['activeSensors'] = temp[2]
                self.qsObj.msp_status['flightModeFlags'] = temp[3]
                self.qsObj.msp_status['profile'] = temp[4]
            elif rec_cmd == MSPv1.MSP_RAW_IMU:
                temp = struct.unpack('<9h', data)
                self.qsObj.msp_raw_imu['ax'] = temp[0]
                self.qsObj.msp_raw_imu['ay'] = temp[1]
                self.qsObj.msp_raw_imu['az'] = temp[2]
                self.qsObj.msp_raw_imu['gx'] = temp[3]
                self.qsObj.msp_raw_imu['gy'] = temp[4]
                self.qsObj.msp_raw_imu['gz'] = temp[5]
                self.qsObj.msp_raw_imu['mx'] = temp[6]
                self.qsObj.msp_raw_imu['my'] = temp[7]
                self.qsObj.msp_raw_imu['mz'] = temp[8]
            elif rec_cmd == MSPv1.MSP_MOTOR:
                temp = struct.unpack('<8h', data)
                temp2 = list(temp)
                self.qsObj.msp_motor['1'] = temp2[0]
                self.qsObj.msp_motor['2'] = temp2[1]
                self.qsObj.msp_motor['3'] = temp2[2]
                self.qsObj.msp_motor['4'] = temp2[3]
                self.qsObj.msp_motor['5'] = temp2[4]
                self.qsObj.msp_motor['6'] = temp2[5]
                self.qsObj.msp_motor['7'] = temp2[6]
                self.qsObj.msp_motor['8'] = temp2[7]
            elif rec_cmd == MSPv1.MSP_3D:
                temp = struct.unpack('<3H', data)
                self.qsObj.msp_3d['deadband3d_low'] = temp[0]
                self.qsObj.msp_3d['deadband3d_high'] = temp[1]
                self.qsObj.msp_3d['neutral3d'] = temp[2]
            elif rec_cmd == MSPv1.MSP_RC:
                temp = struct.unpack('<'+'h'*int(data_length/2), data)
                self.qsObj.msp_rc = list(temp)
                print(self.qsObj.msp_rc)
            elif rec_cmd == MSPv1.MSP_ATTITUDE:
                temp = struct.unpack('<3h',data)
                self.qsObj.msp_attitude['angx'] = float(temp[0]/10.0)
                self.qsObj.msp_attitude['angy'] = float(temp[1]/10.0)
                self.qsObj.msp_attitude['heading'] = float(temp[2])
            elif rec_cmd == MSPv1.MSP_ALTITUDE:
                temp = struct.unpack('<ihi', data)
                self.qsObj.msp_altitude['estalt'] = temp[0]
                self.qsObj.msp_altitude['vario'] = temp[1]
                self.qsObj.msp_altitude['baro'] = temp[2] # Unit:cm
            elif rec_cmd == MSPv1.MSP_SONAR_ALTITUDE:
                temp = struct.unpack('<i', data)
                self.qsObj.msp_sonar_altitude['sonar_altitude'] = temp[0]
            elif rec_cmd == MSPv1.MSP_ANALOG:
                temp = struct.unpack('<B2Hh',data)
                self.qsObj.msp_analog['vbat'] = temp[0]
                self.qsObj.msp_analog['powermetersum'] = temp[1]
                self.qsObj.msp_analog['rssi'] = temp[2]
                self.qsObj.msp_analog['amps'] = temp[3]
            elif rec_cmd == MSPv1.MSP_ARMING_CONFIG:
                temp = struct.unpack('<2B',data)
                self.qsObj.msp_arming_config['auto_disarm_delay'] = temp[0]
                self.qsObj.msp_arming_config['disarm_kill_switch'] = temp[1]
            elif rec_cmd == MSPv1.MSP_LOOP_TIME:
                temp = struct.unpack('<H',data)
                self.qsObj.msp_loop_time['looptime'] = temp[0]
            elif rec_cmd == MSPv1.MSP_RC_TUNING:
                temp = struct.unpack('<8BHB',data)
                self.qsObj.msp_rc_tuning['reserve1'] = temp[0]
                self.qsObj.msp_rc_tuning['stabilized_rc_expo'] = temp[1]
                self.qsObj.msp_rc_tuning['roll_rate'] = temp[2]
                self.qsObj.msp_rc_tuning['pitch_rate'] = temp[3]
                self.qsObj.msp_rc_tuning['yaw_rate'] = temp[4]
                self.qsObj.msp_rc_tuning['throttle_dyn_pid'] = temp[5]
                self.qsObj.msp_rc_tuning['throttle_rc_mid'] = temp[6]
                self.qsObj.msp_rc_tuning['throttle_rc_expo'] = temp[7]
                self.qsObj.msp_rc_tuning['throttle_pa_breakpoint'] = temp[8]
                self.qsObj.msp_rc_tuning['stabilized_rc_yaw_expo'] = temp[9]
            elif rec_cmd == MSPv1.MSP_PID:
                temp = struct.unpack('<'+'B'*data_length, data)
                self.qsObj.msp_pid = list(temp)
            elif rec_cmd == MSPv1.MSP_PIDNAMES:
                temp = struct.unpack('<'+'c'*data_length, data)
                tempStr = ''.join(x.decode('utf-8') for x in temp)
                tempList = tempStr.split(";")
                tempList.remove('')
                self.qsObj.msp_pidnames = tempList
                # static const char pidnames[] =
                # "ROLL;"
                # "PITCH;"
                # "YAW;"
                # "ALT;"
                # "Pos;"
                # "PosR;"
                # "NavR;"
                # "LEVEL;"
                # "MAG;"
                # "VEL;";
            elif rec_cmd == MSPv1.MSP_PID_CONTROLLER:
                temp = struct.unpack('<B',data)
                self.qsObj.msp_pid_controller = temp[0]
            elif rec_cmd == MSPv1.MSP_INAV_PID:
                temp = struct.unpack('<B2H2BH6B',data)
                self.qsObj.msp_inav_pid['async_mode'] = temp[0]
                self.qsObj.msp_inav_pid['acc_task_frequency'] = temp[1]
                self.qsObj.msp_inav_pid['attitude_task_frequency'] = temp[2]
                self.qsObj.msp_inav_pid['heading_hold_rate_limit'] = temp[3]
                self.qsObj.msp_inav_pid['heading_hold_error_lpf_freq'] = temp[4]
                self.qsObj.msp_inav_pid['yaw_jump_prevention_limit'] = temp[5]
                self.qsObj.msp_inav_pid['gyro_lpf'] = temp[6]
                self.qsObj.msp_inav_pid['acc_soft_lpf_hz'] = temp[7]
                self.qsObj.msp_inav_pid['reserve1'] = temp[8]
                self.qsObj.msp_inav_pid['reserve2'] = temp[9]
                self.qsObj.msp_inav_pid['reserve3'] = temp[10]
                self.qsObj.msp_inav_pid['reserve4'] = temp[11]
            elif rec_cmd == MSPv1.MSP_FILTER_CONFIG:
                temp = struct.unpack('<B8H',data)
                self.qsObj.msp_filter_config['gyro_soft_lpf_hz'] = temp[0]
                self.qsObj.msp_filter_config['dterm_lpf_hz'] = temp[1]
                self.qsObj.msp_filter_config['yaw_lpf_hz'] = temp[2]
                self.qsObj.msp_filter_config['gyro_soft_notch_hz_1'] = temp[3]
                self.qsObj.msp_filter_config['gyro_soft_notch_cutoff_1'] = temp[4]
                self.qsObj.msp_filter_config['dterm_soft_notch_hz'] = temp[5]
                self.qsObj.msp_filter_config['dterm_soft_notch_cutoff'] = temp[6]
                self.qsObj.msp_filter_config['gyro_soft_notch_hz_2'] = temp[7]
                self.qsObj.msp_filter_config['gyro_soft_notch_cutoff_2'] = temp[8]
            elif rec_cmd == MSPv1.MSP_PID_ADVANCED:
                temp = struct.unpack('<3H4BHB2H',data)
                self.qsObj.msp_pid_advanced['roll_pitch_i_term_ignore_rate'] = temp[0]
                self.qsObj.msp_pid_advanced['yaw_i_term_ignore_rate'] = temp[1]
                self.qsObj.msp_pid_advanced['yaw_p_limit'] = temp[2]
                self.qsObj.msp_pid_advanced['reserve1'] = temp[3]
                self.qsObj.msp_pid_advanced['reserve2'] = temp[4]
                self.qsObj.msp_pid_advanced['reserve3'] = temp[5]
                self.qsObj.msp_pid_advanced['d_term_setpoint_weight'] = temp[6]
                self.qsObj.msp_pid_advanced['pid_sum_limit'] = temp[7]
                self.qsObj.msp_pid_advanced['reserve4'] = temp[8]
                self.qsObj.msp_pid_advanced['axis_acceleration_limit_roll_pitch'] = temp[9]
                self.qsObj.msp_pid_advanced['axis_acceleration_limit_yaw'] = temp[10]
            elif rec_cmd == MSPv1.MSP_ADVANCED_CONFIG:
                temp = struct.unpack('<4B2HB',data)
                self.qsObj.msp_advanced_config['reserve1'] = temp[0]
                self.qsObj.msp_advanced_config['reserve2'] = temp[1]
                self.qsObj.msp_advanced_config['reserve3'] = temp[2]
                self.qsObj.msp_advanced_config['motor_pwm_protocol'] = temp[3]
                self.qsObj.msp_advanced_config['motor_pwm_rate'] = temp[4]
                self.qsObj.msp_advanced_config['servo_pwm_rate'] = temp[5]
                self.qsObj.msp_advanced_config['gyro_sync'] = temp[6]
            elif rec_cmd == MSPv1.MSP_MODE_RANGES:
                temp = struct.unpack('<'+'B'*data_length, data)
                self.qsObj.msp_mode_ranges = list(temp)
            elif rec_cmd == MSPv1.MSP_ADJUSTMENT_RANGES:
                temp = struct.unpack('<'+'B'*data_length, data)
                self.qsObj.msp_adjustment_ranges = list(temp)
            elif rec_cmd == MSPv1.MSP_BOXNAMES:
                temp = struct.unpack('<'+'c'*data_length, data)
                tempStr = ''.join(x.decode('utf-8') for x in temp)
                tempList = tempStr.split(";")
                tempList.remove('')
                self.qsObj.msp_boxnames = tempList
            elif rec_cmd == MSPv1.MSP_BOXIDS:
                temp = struct.unpack('<'+'B'*data_length,data)
                self.qsObj.msp_boxids = list(temp)
            elif rec_cmd == MSPv1.MSP_MISC:
                temp = struct.unpack('<5H6BH4B',data)
                self.qsObj.msp_misc['mid_rc'] = temp[0]
                self.qsObj.msp_misc['min_throttle'] = temp[1]
                self.qsObj.msp_misc['max_throttle'] = temp[2]
                self.qsObj.msp_misc['min_command'] = temp[3]
                self.qsObj.msp_misc['failsafe_throttle'] = temp[4]
                self.qsObj.msp_misc['gps_provider'] = temp[5]
                self.qsObj.msp_misc['gps_baudrate'] = temp[6]
                self.qsObj.msp_misc['gps_sbas_mode'] = temp[7]
                self.qsObj.msp_misc['reserve1'] = temp[8]
                self.qsObj.msp_misc['rssi_channel'] = temp[9]
                self.qsObj.msp_misc['reserve2'] = temp[10]
                self.qsObj.msp_misc['mag_declination'] = temp[11]
                self.qsObj.msp_misc['voltage_scale'] = temp[12]
                self.qsObj.msp_misc['voltage_cell_min'] = temp[13]
                self.qsObj.msp_misc['voltage_cell_max'] = temp[14]
                self.qsObj.msp_misc['voltage_cell_warning'] = temp[15]
            elif rec_cmd == MSPv1.MSP_MOTOR_PINS:
                temp = struct.unpack('<8B',data)
                self.qsObj.msp_motor_pins = list(temp)
            elif rec_cmd == MSPv1.MSP_RAW_GPS:
                temp = struct.unpack('<2B2ih3H',data)
                self.qsObj.msp_raw_gps['gps_fix'] = temp[0]
                self.qsObj.msp_raw_gps['gps_numsat'] = temp[1]
                self.qsObj.msp_raw_gps['gps_lat'] = temp[2]
                self.qsObj.msp_raw_gps['gps_lon'] = temp[3]
                self.qsObj.msp_raw_gps['gps_altitude'] = temp[4]
                self.qsObj.msp_raw_gps['gps_speed'] = temp[5]
                self.qsObj.msp_raw_gps['gps_ground_course'] = temp[6]
                self.qsObj.msp_raw_gps['gps_hdop'] = temp[7]
            elif rec_cmd == MSPv1.MSP_COMP_GPS:
                temp = struct.unpack('<2HB',data)
                self.qsObj.msp_comp_gps['range'] = temp[0]
                self.qsObj.msp_comp_gps['direction'] = temp[1]
                self.qsObj.msp_comp_gps['update'] = temp[2]
            elif rec_cmd == MSPv1.MSP_NAV_STATUS:
                temp = struct.unpack('<5BH',data)
                self.qsObj.msp_nav_status['nav_mode'] = temp[0]
                self.qsObj.msp_nav_status['nav_state'] = temp[1]
                self.qsObj.msp_nav_status['active_wp_action'] = temp[2]
                self.qsObj.msp_nav_status['active_wp_number'] = temp[3]
                self.qsObj.msp_nav_status['nav_error'] = temp[4]
                self.qsObj.msp_nav_status['heading_hold_target'] = temp[5]
            elif rec_cmd == MSPv1.MSP_NAV_POSHOLD:
                temp = struct.unpack('<B4H2BH',data)
                self.qsObj.msp_nav_poshold['user_control_mode'] = temp[0]
                self.qsObj.msp_nav_poshold['max_auto_speed'] = temp[1]
                self.qsObj.msp_nav_poshold['max_auto_climb_rate'] = temp[2]
                self.qsObj.msp_nav_poshold['max_manual_speed'] = temp[3]
                self.qsObj.msp_nav_poshold['max_manual_climb_rate'] = temp[4]
                self.qsObj.msp_nav_poshold['mc_max_bank_angle'] = temp[5]
                self.qsObj.msp_nav_poshold['use_thr_mid_for_althold'] = temp[6]
                self.qsObj.msp_nav_poshold['mc_hover_throttle'] = temp[7]
            elif rec_cmd == MSPv1.MSP_RTH_AND_LAND_CONFIG:
                temp = struct.unpack('<H5B6H',data)
                self.qsObj.msp_rth_and_land_config['min_rth_distance'] = temp[0]
                self.qsObj.msp_rth_and_land_config['rth_climb_first'] = temp[1]
                self.qsObj.msp_rth_and_land_config['rth_climb_ignore_emerg'] = temp[2]
                self.qsObj.msp_rth_and_land_config['rth_tail_first'] = temp[3]
                self.qsObj.msp_rth_and_land_config['rth_allow_landing'] = temp[4]
                self.qsObj.msp_rth_and_land_config['rth_alt_control_mode'] = temp[5]
                self.qsObj.msp_rth_and_land_config['rth_abort_threshold'] = temp[6]
                self.qsObj.msp_rth_and_land_config['rth_altitude'] = temp[7]
                self.qsObj.msp_rth_and_land_config['land_descent_rate'] = temp[8]
                self.qsObj.msp_rth_and_land_config['land_slowdown_minalt'] = temp[9]
                self.qsObj.msp_rth_and_land_config['land_slowdown_maxalt'] = temp[10]
                self.qsObj.msp_rth_and_land_config['emerg_descent_rate'] = temp[11]
            elif rec_cmd == MSPv1.MSP_POSITION_ESTIMATION_CONFIG:
                temp = struct.unpack('<5H2B',data)
                self.qsObj.msp_position_estimation_config['w_z_baro_p'] = temp[0]
                self.qsObj.msp_position_estimation_config['w_z_gps_p'] = temp[1]
                self.qsObj.msp_position_estimation_config['w_z_gps_v'] = temp[2]
                self.qsObj.msp_position_estimation_config['w_xy_gps_p'] = temp[3]
                self.qsObj.msp_position_estimation_config['w_xy_gps_v'] = temp[4]
                self.qsObj.msp_position_estimation_config['gps_min_sats'] = temp[5]
                self.qsObj.msp_position_estimation_config['use_gps_velned'] = temp[6]
            elif rec_cmd == MSPv1.MSP_NAV_CONFIG:
                pass
            elif rec_cmd == MSPv1.MSP_GPSSVINFO:
                temp = struct.unpack('<5B',data)
                self.qsObj.msp_gpssvinfo['gps_hdop'] = temp[3]
            elif rec_cmd == MSPv1.MSP_GPSSTATISTICS:
                temp = struct.unpack('<H3I3H',data)
                self.qsObj.msp_gpsstatistics['gps_last_message_dt'] = temp[0]
                self.qsObj.msp_gpsstatistics['gps_errors'] = temp[1]
                self.qsObj.msp_gpsstatistics['gps_timeouts'] = temp[2]
                self.qsObj.msp_gpsstatistics['gps_packet_count'] = temp[3]
                self.qsObj.msp_gpsstatistics['gps_hdop'] = temp[4]
                self.qsObj.msp_gpsstatistics['gps_eph'] = temp[5]
                self.qsObj.msp_gpsstatistics['gps_epv'] = temp[6]
            elif rec_cmd == MSPv1.MSP_DEBUG:
                temp = struct.unpack('<'+'4H',data)
                self.qsObj.msp_debug = list(temp)
            elif rec_cmd == MSPv1.MSP_UID:
                temp = struct.unpack('<3I', data)
            elif rec_cmd == MSPv1.MSP_FEATURE:
                temp = struct.unpack('<I',data)
                self.qsObj.msp_feature['mask'] = temp[0]
            elif rec_cmd == MSPv1.MSP_CALIBRATION_DATA:
                temp = struct.unpack('<B9h',data)
                self.qsObj.msp_calibration_data['accGetCalibrationAxisFlags'] = temp[0]
                self.qsObj.msp_calibration_data['Acc X zero'] = temp[1]
                self.qsObj.msp_calibration_data['Acc Y zero'] = temp[2]
                self.qsObj.msp_calibration_data['Acc Z zero'] = temp[3]
                self.qsObj.msp_calibration_data['Acc X gain'] = temp[4]
                self.qsObj.msp_calibration_data['Acc Y gain'] = temp[5]
                self.qsObj.msp_calibration_data['Acc Z gain'] = temp[6]
                self.qsObj.msp_calibration_data['Mag X zero'] = temp[7]
                self.qsObj.msp_calibration_data['Mag Y zero'] = temp[8]
                self.qsObj.msp_calibration_data['Mag Z zero'] = temp[9]
            elif rec_cmd == MSPv1.MSP_BOARD_ALIGNMENT:
                temp = struct.unpack('<3h',data)
                self.qsObj.msp_board_alignment['roll_deci_degrees'] = temp[0]
                self.qsObj.msp_board_alignment['pitch_deci_degrees'] = temp[1]
                self.qsObj.msp_board_alignment['yaw_deci_degrees'] = temp[2]
            elif rec_cmd == MSPv1.MSP_VOLTAGE_METER_CONFIG:
                temp = struct.unpack('<4B', data)
                self.qsObj.msp_voltage_meter_config['scale'] = temp[0]
                self.qsObj.msp_voltage_meter_config['cell_min'] = temp[1]
                self.qsObj.msp_voltage_meter_config['cell_max'] = temp[2]
                self.qsObj.msp_voltage_meter_config['cell_warning'] = temp[3]
            elif rec_cmd == MSPv1.MSP_CURRENT_METER_CONFIG:
                temp = struct.unpack('<HhBH', data)
                self.qsObj.msp_current_meter_config['scale'] = temp[0]
                self.qsObj.msp_current_meter_config['offset'] = temp[1]
                self.qsObj.msp_current_meter_config['type'] = temp[2]
                self.qsObj.msp_current_meter_config['capabity_value'] = temp[3]
            elif rec_cmd == MSPv1.MSP_MIXER:
                temp = struct.unpack('<B',data)
                self.qsObj.msp_mixer['mixer_mode'] = temp[0]
            elif rec_cmd == MSPv1.MSP_RX_CONFIG:
                temp = struct.unpack('<B3HB2H2BHBI3B', data)
                self.qsObj.msp_rx_config['serialrx_provider'] = temp[0]
                self.qsObj.msp_rx_config['max_check'] = temp[1]
                self.qsObj.msp_rx_config['mid_rc'] = temp[2]
                self.qsObj.msp_rx_config['min_check'] = temp[3]
                self.qsObj.msp_rx_config['spektrum_sat_bind'] = temp[4]
                self.qsObj.msp_rx_config['rx_min_usec'] = temp[5]
                self.qsObj.msp_rx_config['rx_max_usec'] = temp[6]
                self.qsObj.msp_rx_config['rc_interpolation'] = temp[7]
                self.qsObj.msp_rx_config['rc_interpolation_interval'] = temp[8]
                self.qsObj.msp_rx_config['air_mode_activate_threshold'] = temp[9]
                self.qsObj.msp_rx_config['rx_spi_protocol'] = temp[10]
                self.qsObj.msp_rx_config['rx_spi_id'] = temp[11]
                self.qsObj.msp_rx_config['rx_spi_rf_channel_count'] = temp[12]
                self.qsObj.msp_rx_config['fpv_cam_angle_degrees'] = temp[13]
                self.qsObj.msp_rx_config['receiver_type'] = temp[14]
            elif rec_cmd == MSPv1.MSP_FAILSAFE_CONFIG:
                temp = struct.unpack('<2BHBH2B5HB', data)
                self.qsObj.msp_failsafe_config['failsafe_delay'] = temp[0]
                self.qsObj.msp_failsafe_config['failsafe_off_delay'] = temp[1]
                self.qsObj.msp_failsafe_config['failsafe_throttle'] = temp[2]
                self.qsObj.msp_failsafe_config['failsafe_kill_switch'] = temp[3]
                self.qsObj.msp_failsafe_config['failsafe_throttle_low_delay'] = temp[4]
                self.qsObj.msp_failsafe_config['failsafe_procedure'] = temp[5]
                self.qsObj.msp_failsafe_config['failsafe_recovery_delay'] = temp[6]
                self.qsObj.msp_failsafe_config['failsafe_fw_roll_angle'] = temp[7]
                self.qsObj.msp_failsafe_config['failsafe_fw_pitch_angle'] = temp[8]
                self.qsObj.msp_failsafe_config['failsafe_fw_yaw_rate'] = temp[9]
                self.qsObj.msp_failsafe_config['failsafe_stick_motion_threshold'] = temp[10]
                self.qsObj.msp_failsafe_config['failsafe_min_distance'] = temp[11]
                self.qsObj.msp_failsafe_config['failsafe_min_distance_procedure'] = temp[12]
            elif rec_cmd == MSPv1.MSP_RSSI_CONFIG:
                temp = struct.unpack('<B', data)
                self.qsObj.msp_rssi_config['rssi_channel'] = temp[0]
            elif rec_cmd == MSPv1.MSP_RX_MAP:
                temp = struct.unpack('<'+'B'*data_length, data)
                self.qsObj.msp_rx_map = list(temp)
            elif rec_cmd == MSPv1.MSP_BF_CONFIG:
                pass
            elif rec_cmd == MSPv1.MSP_CF_SERIAL_CONFIG:
                temp = struct.unpack('<' + 'BH4B'*int(data_length/7), data)
                self.qsObj.msp_cf_serial_config = list(temp)
            elif rec_cmd == MSPv1.MSP_RC_DEADBAND:
                temp = struct.unpack('<3BH', data)
                self.qsObj.msp_rc_deadband['deadband'] = temp[0]
                self.qsObj.msp_rc_deadband['yaw_deadband'] = temp[1]
                self.qsObj.msp_rc_deadband['alt_hold_deadband'] = temp[2]
                self.qsObj.msp_rc_deadband['deadbanded_throttle'] = temp[3]
            elif rec_cmd == MSPv1.MSP_SENSOR_ALIGNMENT:
                temp = struct.unpack('<3B', data)
                self.qsObj.msp_sensor_alignment['gyro_align'] = temp[0]
                self.qsObj.msp_sensor_alignment['acc_align'] = temp[1]
                self.qsObj.msp_sensor_alignment['mag_align'] = temp[2]
            elif rec_cmd == MSPv1.MSP_SENSOR_CONFIG:
                temp = struct.unpack('<6B', data)
                self.qsObj.msp_sensor_config['acc'] = temp[0]
                self.qsObj.msp_sensor_config['baro'] = temp[1]
                self.qsObj.msp_sensor_config['mag'] = temp[2]
                self.qsObj.msp_sensor_config['pitot'] = temp[3]
                self.qsObj.msp_sensor_config['rangefinder'] = temp[4]
                self.qsObj.msp_sensor_config['opflow'] = temp[5]
            elif rec_cmd == MSPv1.MSP_WP_GETINFO:
                temp = struct.unpack('<4B',data)
            elif rec_cmd == MSPv1.MSP_NAME:
                temp = struct.unpack('<'+'B'*data_length,data)
                self.qsObj.msp_name = "".join([chr(x) for x in temp])
            elif rec_cmd == MSPv1.MSP_WP:
                temp = struct.unpack('<2B3i3hB',data)
                self.qsObj.tempMission = list(temp)
            elif rec_cmd == MSPv1.MSP_XBEE_SELF_TELEMETRY_ADDR:
                temp = struct.unpack('<I', data)
                self.qsObj.msp_xbee_self_telemetry_addr = temp[0]
                print(self.qsObj.msp_xbee_self_telemetry_addr)
            elif rec_cmd == MSPv1.MSP_XBEE_TELEMETRY_SOURCE_ADDR:
                temp = struct.unpack('<3I', data)
                self.qsObj.msp_xbee_telemetry_source_addr = temp
                print(self.qsObj.msp_xbee_telemetry_source_addr)
            elif rec_cmd == MSPv1.MSP_XBEE_TELEMETRY_DESTINATION_ADDR:
                temp = struct.unpack('<3I', data)
                self.qsObj.msp_xbee_telemetry_destination_addr = temp
                print(self.qsObj.msp_xbee_telemetry_destination_addr)
            elif rec_cmd == MSPv1.MSP_XBEE_SELF_RC_ADDR:
                temp = struct.unpack('<I', data)
                self.qsObj.msp_xbee_self_rc_addr = temp[0]
                print(self.qsObj.msp_xbee_self_rc_addr)
            elif rec_cmd == MSPv1.MSP_XBEE_RC_SOURCE_ADDR:
                temp = struct.unpack('<I', data)
                self.qsObj.msp_xbee_rc_source_addr = temp[0]
                print(self.qsObj.msp_xbee_rc_source_addr)
            elif rec_cmd == MSPv1.MSP_FORMATION_CONFIG:
                temp = struct.unpack('<5H2B3HI', data)
                self.qsObj.msp_formation_config['flight_height'] = temp[0]
                self.qsObj.msp_formation_config['distance_gain'] = temp[1]
                self.qsObj.msp_formation_config['area_gain'] = temp[2]
                self.qsObj.msp_formation_config['lat_gain'] = temp[3]
                self.qsObj.msp_formation_config['lon_gain'] = temp[4]
                self.qsObj.msp_formation_config['graph_type'] = temp[5]
                self.qsObj.msp_formation_config['identity'] = temp[6]
                self.qsObj.msp_formation_config['d_ji'] = temp[7]
                self.qsObj.msp_formation_config['d_ki'] = temp[8]
                self.qsObj.msp_formation_config['d_kj'] = temp[9]
                self.qsObj.msp_formation_config['ad'] = temp[10]
            elif rec_cmd == MSPv1.MSP_NETWORK_CONFIG:
                temp = struct.unpack('<9I', data)
                self.qsObj.msp_network_config['selfTeleAddressLow'] = temp[0]
                self.qsObj.msp_network_config['teleSource1AddressLow'] = temp[1]
                self.qsObj.msp_network_config['teleSource2AddressLow'] = temp[2]
                self.qsObj.msp_network_config['teleSource3AddressLow'] = temp[3]
                self.qsObj.msp_network_config['teleDestination1AddressLow'] = temp[4]
                self.qsObj.msp_network_config['teleDestination2AddressLow'] = temp[5]
                self.qsObj.msp_network_config['teleDestination3AddressLow'] = temp[6]
                self.qsObj.msp_network_config['selfRemoteAddressLow'] = temp[7]
                self.qsObj.msp_network_config['remoteSourceAddressLow'] = temp[8]
            else:
                return "No return error!"
        return validFlag

    # Using, Checked
    def readPacket(self, return_dict):
        packet = None
        while packet == None:
            packet = self.serialHandle.readData()
        return_dict['packet'] = packet

    def readPacket2(self):
        packet = None
        packet = self.serialHandle.readData()
        return packet

    # Using, Checked
    def requestData(self, data_length, send_code, send_data):
        rec_packet = None
        send_packet = self.constructSendPacket(data_length, send_code, send_data)
        while True:
            self.sendPacket(send_packet)
            manager = multiprocessing.Manager()
            return_dict = manager.dict()
            p = multiprocessing.Process(target=self.readPacket, args=(return_dict,)) #, args=(10,)
            p.start()
            p.join(0.05)
            if p.is_alive():
                p.terminate()
                p.join()
            else:
                rec_packet = return_dict['packet']
            if rec_packet != None:
                break
        return rec_packet

    def requestData2(self, data_length, send_code, send_data):
        rec_packet = None
        send_packet = self.constructSendPacket(data_length, send_code, send_data)
        self.sendPacket(send_packet)
        rec_packet = self.readPacket2()
        return rec_packet

    def multiPacketProcess(self, packet):
        headerIndex = [m.start() for m in re.finditer(b'\$M\>', packet)]
        subpacketList = []
        for i in range(len(headerIndex)):
            if i == len(headerIndex)-1:
                subpacketList.append(packet[headerIndex[i]:])
            else:
                subpacketList.append(packet[headerIndex[i]:headerIndex[i+1]])
        return subpacketList

    # Using, Checked
    def readFromFC(self, data_length, send_code, send_data):
        rec_packet = self.requestData2(data_length, send_code, send_data)
        processedPacketList = self.multiPacketProcess(rec_packet)
        if len(processedPacketList) > 0:
            for subpacket in processedPacketList:
                self.parseReceivedPacket(subpacket)

    # Using, Checked
    def cliCommandSwitch(self, expr):
        # print(expr)
        if expr == "dump":
            self.processDump()
            #self.readFromFC(0, MSPv1.MSP_STATUS_EX, [])
            # tempPacket = self.constructSendPacket(0, MSPv1.MSP_STATUS_EX, [])
            # self.sendPacket(tempPacket)
            # tempRecPacket = self.readPacket2()
            # self.parseReceivedPacket(tempRecPacket)
        elif expr == "diff":
            self.processDiff()
        elif expr == "save":
            pass
        elif expr == "help":
            self.processHelp()
        elif expr == "um":
            self.processUploadMissions()
        elif expr == "dm":
            self.processDownloadMissions()
        elif expr == "exit":
            pass
        elif expr == "feature":
            self.processFeature()
        else:
            pass

    def debug(self):
        # self.readFromFC(0, MSPv1.MSP_FC_VARIANT, [])
        # self.readFromFC(0, MSPv1.MSP_FC_VERSION, [])
        # self.readFromFC(0, MSPv1.MSP_ACTIVEBOXES, [])
        # self.readFromFC(0, MSPv1.MSP_STATUS_EX, [])
        # self.readFromFC(0, MSPv1.MSP_STATUS, [])
        # self.readFromFC(0, MSPv1.MSP_MOTOR, [])
        # self.readFromFC(0, MSPv1.MSP_RC, [])
        # self.readFromFC(0, MSPv1.MSP_ALTITUDE, [])
        # self.readFromFC(0, MSPv1.MSP_ATTITUDE, [])
        # self.readFromFC(0, MSPv1.MSP_SONAR_ALTITUDE, [])
        # self.readFromFC(0, MSPv1.MSP_ANALOG, [])
        pass

    def overviewInfoResponse(self, ind):
        self.processOverviewCheck(ind)
        # p = multiprocessing.Process(target=self.processOverviewCheck)
        # p.deamon = True
        # p.start()

    def preCheck(self):
        # Must have, check until get this data; if more than 10 times, then fail.
        counter = 0
        while len(self.qsObj.msp_boxids) == 0 and counter < 10:
            self.readFromFC(0, MSPv1.MSP_BOXIDS, [])
            counter = counter + 1
        counter = 0
        while len(self.qsObj.msp_boxnames) == 0 and counter < 10:
            self.readFromFC(0, MSPv1.MSP_BOXNAMES, [])
            counter = counter + 1
        counter = 0
        while len(self.qsObj.msp_mode_ranges) == 0 and counter < 10:
            self.readFromFC(0, MSPv1.MSP_MODE_RANGES, [])
            counter = counter + 1
        counter = 0
        while len(self.qsObj.msp_activeboxes) == 0 and counter < 10:
            self.readFromFC(0, MSPv1.MSP_ACTIVEBOXES, [])
            counter = counter + 1
        return True

    def processOverviewCheck(self, ind):
        try:
            if ind == 0:
                # attitude
                self.readFromFC(0, MSPv1.MSP_ATTITUDE, [])
                # self.readFromFC(0, MSPv1.MSP_ACTIVEBOXES, [])
                # self.readFromFC(0, MSPv1.MSP_RAW_IMU, [])
            elif ind == 1:
                # arming flags
                self.readFromFC(0, MSPv1.MSP_STATUS_EX, [])
                self.readFromFC(0, MSPv1.MSP_SENSOR_STATUS, [])
                self.parseArmingFlags()
            elif ind == 2:
                # battery
                self.readFromFC(0, MSPv1.MSP_MISC, [])
                self.readFromFC(0, MSPv1.MSP_ANALOG, [])
            elif ind == 3:
                # communication
                self.readFromFC(0, MSPv1.MSP_STATUS_EX, [])
            elif ind == 4:
                # gps
                self.readFromFC(0, MSPv1.MSP_RAW_GPS, [])
                self.readFromFC(0, MSPv1.MSP_GPSSTATISTICS, [])
            # emit signal to MainWindow then update labels in OverviewPage.
            self.overviewDataUpdateSignal.emit(ind)
        except serial.serialutil.SerialException:
            print("Serial Exception")
        except Exception:
            print("Process Overview Check")
            print(Exception)
            pass

    def processSensorDataRequest(self, ind):
        if ind == 0:
            self.readFromFC(0, MSPv1.MSP_RAW_IMU, [])
        elif ind == 1:
            self.readFromFC(0, MSPv1.MSP_ALTITUDE, [])
        elif ind == 2:
            self.readFromFC(0, MSPv1.MSP_SONAR_ALTITUDE, [])
        self.sensorDataUpdateSignal.emit(ind)

    def processMotorDataRequest(self, ind):
        try:
            if ind == 0:
                self.readFromFC(0, MSPv1.MSP_MOTOR, [])
                # self.qsObj.msp_motor = [0,0,0,0,0,0,0,0]
                # self.readFromFC(0, MSPv1.MSP_STATUS_EX, [])
            self.motorDataUpdateSignal.emit(ind)
        except serial.serialutil.SerialException:
            print("Serial Exception")
        except Exception:
            print("Process Motor Check")
            print(Exception)
            pass

    def processHeaderDataRequest(self, ind):
        if ind == 0:
            self.readFromFC(0, MSPv1.MSP_STATUS_EX, [])
            # self.parseArmingFlags()
            self.parseActiveFlightModeFlags()
        elif ind == 1:
            self.readFromFC(0, MSPv1.MSP_SENSOR_STATUS, [])
        self.headerDataUpdateSignal.emit(ind)

    def processModeRCDataRequest(self, ind):
        try:
            if ind == 0:
                self.readFromFC(0, MSPv1.MSP_RC, [])
            self.modeRCDataUpdateSignal.emit(ind)
        except serial.serialutil.SerialException:
            print("Serial Exception")
        except Exception:
            print("Process RC Value Check")
            print(Exception)
            pass

    def processFeature(self):
        try:
            self.readFromFC(0, MSPv1.MSP_FEATURE, [])
        except Exception:
            pass

    def processCalibrationCheck(self):
        self.readFromFC(0, MSPv1.MSP_CALIBRATION_DATA, [])

    def processCalibrationSave(self):
        # MSP_SET_CALIBRATION_DATA
        calibrationDataList = [self.qsObj.msp_calibration_data['Acc X zero'],
                               self.qsObj.msp_calibration_data['Acc Y zero'],
                               self.qsObj.msp_calibration_data['Acc Z zero'],
                               self.qsObj.msp_calibration_data['Acc X gain'],
                               self.qsObj.msp_calibration_data['Acc Y gain'],
                               self.qsObj.msp_calibration_data['Acc Z gain'],
                               self.qsObj.msp_calibration_data['Mag X zero'],
                               self.qsObj.msp_calibration_data['Mag Y zero'],
                               self.qsObj.msp_calibration_data['Mag Z zero']]
        tempPacket = self.constructSendPacket(18, MSPv1.MSP_SET_CALIBRATION_DATA, calibrationDataList)
        self.sendPacket(tempPacket)
        print("Calibration Saved")
        # Save to EEPROM
        self.saveToEEPROM()
        # Reboot
        self.reboot()

    def processAccCalibrationRequest(self, ind):
        # To do: remove "ind"; it is not needed any more.
        self.readFromFC(0, MSPv1.MSP_CALIBRATION_DATA, [])
        time.sleep(0.5)
        send_packet = self.constructSendPacket(0, MSPv1.MSP_ACC_CALIBRATION, [])
        self.sendPacket(send_packet)
        time.sleep(2)
        self.readFromFC(0, MSPv1.MSP_CALIBRATION_DATA, [])
        self.calibrationFeedbackSignal.emit()

    def processMagCalibrationRequest(self):
        self.readFromFC(0, MSPv1.MSP_CALIBRATION_DATA, [])
        time.sleep(0.5)
        send_packet = self.constructSendPacket(0, MSPv1.MSP_MAG_CALIBRATION, [])
        self.sendPacket(send_packet)
        time.sleep(30)
        self.readFromFC(0, MSPv1.MSP_CALIBRATION_DATA, [])
        self.calibrationFeedbackSignal.emit()

    def processParameterSettingCheck(self):
        # PIDs
        self.readFromFC(0, MSPv1.MSP_PID, [])
        # print(self.qsObj.msp_pid)
        self.readFromFC(0, MSPv1.MSP_PIDNAMES, [])
        # print(self.qsObj.msp_pidnames)
        # Basic settings: MSP_NAV_POSHOLD
        self.readFromFC(0, MSPv1.MSP_NAV_POSHOLD, [])
        # print(self.qsObj.msp_nav_poshold)
        # RTH and Landing settings: MSP_RTH_AND_LAND_CONFIG
        self.readFromFC(0, MSPv1.MSP_RTH_AND_LAND_CONFIG, [])
        # print(self.qsObj.msp_rth_and_land_config)
        # Position Estimator: MSP_POSITION_ESTIMATION_CONFIG
        self.readFromFC(0, MSPv1.MSP_POSITION_ESTIMATION_CONFIG, [])
        # print(self.qsObj.msp_position_estimation_config)
        # Filtering
        self.readFromFC(0, MSPv1.MSP_FILTER_CONFIG, [])
        # print(self.qsObj.msp_filter_config)
        self.readFromFC(0, MSPv1.MSP_RC_TUNING, [])
        # Miscellaneous
        self.readFromFC(0, MSPv1.MSP_INAV_PID, [])
        # print(self.qsObj.msp_inav_pid)
        self.readFromFC(0, MSPv1.MSP_PID_ADVANCED, [])
        # print(self.qsObj.msp_pid_advanced)
        #
        self.readFromFC(0, MSPv1.MSP_ADVANCED_CONFIG, [])
        # print(self.qsObj.msp_advanced_config)
        # To do: MSP2_INAV_RATE_PROFILE

    def processParameterSettingSave(self):
        # PID Tuning
        # MSP_SET_PID
        # print(self.qsObj.msp_pidnames)
        # print(self.qsObj.msp_pid)
        tempPacket = self.constructSendPacket(3*len(self.qsObj.msp_pidnames), MSPv1.MSP_SET_PID, self.qsObj.msp_pid)
        self.sendPacket(tempPacket)

        # MSPV2_INAV_SET_RATE_PROFILE,
        # MSP_SET_RC_TUNING
        tempPacket = self.constructSendPacket(11, MSPv1.MSP_SET_RC_TUNING,
                                              [self.qsObj.msp_rc_tuning['reserve1'],
                                               self.qsObj.msp_rc_tuning['stabilized_rc_expo'],
                                               self.qsObj.msp_rc_tuning['roll_rate'],
                                               self.qsObj.msp_rc_tuning['pitch_rate'],
                                               self.qsObj.msp_rc_tuning['yaw_rate'],
                                               self.qsObj.msp_rc_tuning['throttle_dyn_pid'],
                                               self.qsObj.msp_rc_tuning['throttle_rc_mid'],
                                               self.qsObj.msp_rc_tuning['throttle_rc_expo'],
                                               self.qsObj.msp_rc_tuning['throttle_pa_breakpoint'],
                                               self.qsObj.msp_rc_tuning['stabilized_rc_yaw_expo'] ])
        # MSP_SET_INAV_PID
        tempPacket = self.constructSendPacket(15, MSPv1.MSP_SET_INAV_PID,
                                              [self.qsObj.msp_inav_pid['async_mode'],
                                               self.qsObj.msp_inav_pid['acc_task_frequency'],
                                               self.qsObj.msp_inav_pid['attitude_task_frequency'],
                                               self.qsObj.msp_inav_pid['heading_hold_rate_limit'],
                                               self.qsObj.msp_inav_pid['heading_hold_error_lpf_freq'],
                                               self.qsObj.msp_inav_pid['yaw_jump_prevention_limit'],
                                               self.qsObj.msp_inav_pid['gyro_lpf'],
                                               self.qsObj.msp_inav_pid['acc_soft_lpf_hz'],
                                               self.qsObj.msp_inav_pid['reserve1'],
                                               self.qsObj.msp_inav_pid['reserve2'],
                                               self.qsObj.msp_inav_pid['reserve3'],
                                               self.qsObj.msp_inav_pid['reserve4'] ])
        self.sendPacket(tempPacket)
        # MSP_SET_PID_ADVANCED
        print(self.qsObj.msp_pid_advanced)
        tempPacket = self.constructSendPacket(17, MSPv1.MSP_SET_PID_ADVANCED,
                                              [self.qsObj.msp_pid_advanced['roll_pitch_i_term_ignore_rate'],
                                               self.qsObj.msp_pid_advanced['yaw_i_term_ignore_rate'],
                                               self.qsObj.msp_pid_advanced['yaw_p_limit'],
                                               self.qsObj.msp_pid_advanced['reserve1'],
                                               self.qsObj.msp_pid_advanced['reserve2'],
                                               self.qsObj.msp_pid_advanced['reserve3'],
                                               self.qsObj.msp_pid_advanced['d_term_setpoint_weight'],
                                               self.qsObj.msp_pid_advanced['pid_sum_limit'],
                                               self.qsObj.msp_pid_advanced['reserve4'],
                                               self.qsObj.msp_pid_advanced['axis_acceleration_limit_roll_pitch'],
                                               self.qsObj.msp_pid_advanced['axis_acceleration_limit_yaw'] ])
        self.sendPacket(tempPacket)

        # Filtering
        # MSP_SET_FILTER_CONFIG
        tempPacket = self.constructSendPacket(13, MSPv1.MSP_SET_FILTER_CONFIG,
                                              [self.qsObj.msp_filter_config['gyro_soft_lpf_hz'],
                                               self.qsObj.msp_filter_config['dterm_lpf_hz'],
                                               self.qsObj.msp_filter_config['yaw_lpf_hz'],
                                               self.qsObj.msp_filter_config['gyro_soft_notch_hz_1'],
                                               self.qsObj.msp_filter_config['gyro_soft_notch_cutoff_1'],
                                               self.qsObj.msp_filter_config['dterm_soft_notch_hz'],
                                               self.qsObj.msp_filter_config['dterm_soft_notch_cutoff'],
                                               self.qsObj.msp_filter_config['gyro_soft_notch_hz_2'],
                                               self.qsObj.msp_filter_config['gyro_soft_notch_cutoff_2'] ])
        self.sendPacket(tempPacket)

        # Miscellaneous
        # MSP_SET_INAV_PID, MSP_SET_PID_ADVANCED, MSP_SET_RC_TUNING
        # All set above.

        # Basic Navigation Settings
        # MSP_SET_NAV_POSHOLD
        tempPacket = self.constructSendPacket(13, MSPv1.MSP_SET_NAV_POSHOLD,
                                              [self.qsObj.msp_nav_poshold['user_control_mode'],
                                               self.qsObj.msp_nav_poshold['max_auto_speed'],
                                               self.qsObj.msp_nav_poshold['max_auto_climb_rate'],
                                               self.qsObj.msp_nav_poshold['max_manual_speed'],
                                               self.qsObj.msp_nav_poshold['max_manual_climb_rate'],
                                               self.qsObj.msp_nav_poshold['mc_max_bank_angle'],
                                               self.qsObj.msp_nav_poshold['use_thr_mid_for_althold'],
                                               self.qsObj.msp_nav_poshold['mc_hover_throttle'] ])
        self.sendPacket(tempPacket)

        # RTH and Landing Settings
        # MSP_SET_RTH_AND_LAND_CONFIG
        tempPacket = self.constructSendPacket(19, MSPv1.MSP_SET_RTH_AND_LAND_CONFIG,
                                              [self.qsObj.msp_rth_and_land_config['min_rth_distance'],
                                               self.qsObj.msp_rth_and_land_config['rth_climb_first'],
                                               self.qsObj.msp_rth_and_land_config['rth_climb_ignore_emerg'],
                                               self.qsObj.msp_rth_and_land_config['rth_tail_first'],
                                               self.qsObj.msp_rth_and_land_config['rth_allow_landing'],
                                               self.qsObj.msp_rth_and_land_config['rth_alt_control_mode'],
                                               self.qsObj.msp_rth_and_land_config['rth_abort_threshold'],
                                               self.qsObj.msp_rth_and_land_config['rth_altitude'],
                                               self.qsObj.msp_rth_and_land_config['land_descent_rate'],
                                               self.qsObj.msp_rth_and_land_config['land_slowdown_minalt'],
                                               self.qsObj.msp_rth_and_land_config['land_slowdown_maxalt'],
                                               self.qsObj.msp_rth_and_land_config['emerg_descent_rate'] ])
        self.sendPacket(tempPacket)
        # MSP_SET_FW_CONFIG

        # Position Estimator
        # MSP_SET_POSITION_ESTIMATION_CONFIG
        tempPacket = self.constructSendPacket(12, MSPv1.MSP_SET_POSITION_ESTIMATION_CONFIG,
                                              [self.qsObj.msp_position_estimation_config['w_z_baro_p'],
                                               self.qsObj.msp_position_estimation_config['w_z_gps_p'],
                                               self.qsObj.msp_position_estimation_config['w_z_gps_v'],
                                               self.qsObj.msp_position_estimation_config['w_xy_gps_p'],
                                               self.qsObj.msp_position_estimation_config['w_xy_gps_v'],
                                               self.qsObj.msp_position_estimation_config['gps_min_sats'],
                                               self.qsObj.msp_position_estimation_config['use_gps_velned'] ])
        self.sendPacket(tempPacket)

        print("Parameter Setting Saved")
        # Save to EEPROM
        self.saveToEEPROM()
        # Reboot
        self.reboot()

    def processConfigureCheck(self):
        # MSP_BF_CONFIG
        # MSP_ARMING_CONFIG
        self.readFromFC(0, MSPv1.MSP_ARMING_CONFIG, [])
        # MSP_LOOP_TIME
        self.readFromFC(0, MSPv1.MSP_LOOP_TIME, [])
        # MSP_VTX_CONFIG
        # MSPV2_INAV_MISC
        # Serial Port
        self.readFromFC(0, MSPv1.MSP_CF_SERIAL_CONFIG, [])
        # Feature
        self.readFromFC(0, MSPv1.MSP_FEATURE, [])
        # Mixer
        self.readFromFC(0, MSPv1.MSP_MIXER, [])
        # Sensors
        self.readFromFC(0, MSPv1.MSP_SENSOR_CONFIG, [])
        # Board Alignment
        self.readFromFC(0, MSPv1.MSP_BOARD_ALIGNMENT, [])
        self.readFromFC(0, MSPv1.MSP_SENSOR_ALIGNMENT, [])
        # Receiver
        self.readFromFC(0, MSPv1.MSP_RX_CONFIG, [])
        # GPS
        self.readFromFC(0, MSPv1.MSP_MISC, [])
        # 3D
        self.readFromFC(0, MSPv1.MSP_3D, [])
        # Name
        self.readFromFC(0, MSPv1.MSP_NAME, [])
        # ESC/Motor Feature
        self.readFromFC(0, MSPv1.MSP_ADVANCED_CONFIG, [])
        # System Configure
        self.readFromFC(0, MSPv1.MSP_INAV_PID, [])
        # Battery Voltage
        self.readFromFC(0, MSPv1.MSP_VOLTAGE_METER_CONFIG, [])
        self.readFromFC(0, MSPv1.MSP_ANALOG, [])
        # Current Sensor
        self.readFromFC(0, MSPv1.MSP_CURRENT_METER_CONFIG, [])
        # Battery Capacity : MSP_MISC
        # Failsafe Settings
        self.readFromFC(0, MSPv1.MSP_FAILSAFE_CONFIG, [])
        # MSP_RXFAIL_CONFIG
        # MSP_BOXNAMES
        # MSP_MODE_RANGES
        # MSP_BOXIDS
        # MSP_RC

    def processConfigureSave(self):
        print("---MSPv1 Debug---")
        # Port
        # MSP_SET_CF_SERIAL_CONFIG
        tempPacket = self.constructSendPacket(21, MSPv1.MSP_SET_CF_SERIAL_CONFIG, self.qsObj.msp_cf_serial_config)
        self.sendPacket(tempPacket)
        # print(self.qsObj.msp_cf_serial_config)

        # Mixer
        # MSP_SET_MIXER
        tempPacket = self.constructSendPacket(1, MSPv1.MSP_SET_MIXER, [self.qsObj.msp_mixer['mixer_mode']])
        self.sendPacket(tempPacket)
        # print(self.qsObj.msp_mixer)

        # Board Alignment
        # MSP_SET_BOARD_ALIGNMENT
        # print(self.qsObj.msp_board_alignment)
        tempPacket = self.constructSendPacket(6, MSPv1.MSP_SET_BOARD_ALIGNMENT,
                                              [self.qsObj.msp_board_alignment['roll_deci_degrees'],
                                               self.qsObj.msp_board_alignment['pitch_deci_degrees'],
                                               self.qsObj.msp_board_alignment['yaw_deci_degrees'] ])
        self.sendPacket(tempPacket)

        # Board Alignment
        # MSP_SET_SENSOR_ALIGNMENT
        tempPacket = self.constructSendPacket(3, MSPv1.MSP_SET_SENSOR_ALIGNMENT,
                                              [self.qsObj.msp_sensor_alignment['gyro_align'],
                                               self.qsObj.msp_sensor_alignment['acc_align'],
                                               self.qsObj.msp_sensor_alignment['mag_align'] ])
        self.sendPacket(tempPacket)
        # print(self.qsObj.msp_sensor_alignment)

        # MSP_SET_ACC_TRIM
        # MSP_SET_ARMING_CONFIG
        tempPacket = self.constructSendPacket(2, MSPv1.MSP_SET_ARMING_CONFIG,
                                              [self.qsObj.msp_arming_config['auto_disarm_delay'],
                                               self.qsObj.msp_arming_config['disarm_kill_switch']])
        self.sendPacket(tempPacket)

        # MSP_SET_LOOP_TIME
        # print(self.qsObj.msp_loop_time)
        tempPacket = self.constructSendPacket(2, MSPv1.MSP_SET_LOOP_TIME, [self.qsObj.msp_loop_time['looptime']])
        self.sendPacket(tempPacket)

        # Receiver
        # MSP_SET_RX_CONFIG
        # print(self.qsObj.msp_rx_config)
        tempPacket = self.constructSendPacket(24, MSPv1.MSP_SET_RX_CONFIG,
                                              [self.qsObj.msp_rx_config['serialrx_provider'],
                                               self.qsObj.msp_rx_config['max_check'],
                                               self.qsObj.msp_rx_config['mid_rc'],
                                               self.qsObj.msp_rx_config['min_check'],
                                               self.qsObj.msp_rx_config['spektrum_sat_bind'],
                                               self.qsObj.msp_rx_config['rx_min_usec'],
                                               self.qsObj.msp_rx_config['rx_max_usec'],
                                               self.qsObj.msp_rx_config['rc_interpolation'],
                                               self.qsObj.msp_rx_config['rc_interpolation_interval'],
                                               self.qsObj.msp_rx_config['air_mode_activate_threshold'],
                                               self.qsObj.msp_rx_config['rx_spi_protocol'],
                                               self.qsObj.msp_rx_config['rx_spi_id'],
                                               self.qsObj.msp_rx_config['rx_spi_rf_channel_count'],
                                               self.qsObj.msp_rx_config['fpv_cam_angle_degrees'],
                                               self.qsObj.msp_rx_config['receiver_type'] ])
        self.sendPacket(tempPacket)

        # Sensors
        # MSP_SET_SENSOR_CONFIG
        # print(self.qsObj.msp_sensor_config)
        tempPacket = self.constructSendPacket(6, MSPv1.MSP_SET_SENSOR_CONFIG,
                                              [self.qsObj.msp_sensor_config['acc'],
                                               self.qsObj.msp_sensor_config['baro'],
                                               self.qsObj.msp_sensor_config['mag'],
                                               self.qsObj.msp_sensor_config['pitot'],
                                               self.qsObj.msp_sensor_config['rangefinder'],
                                               self.qsObj.msp_sensor_config['opflow']])
        self.sendPacket(tempPacket)

        # MSP_SET_VTX_CONFIG

        # GPS
        # MSP_SET_MISC
        # print(self.qsObj.msp_misc)
        tempPacket = self.constructSendPacket(22, MSPv1.MSP_SET_MISC,
                                              [self.qsObj.msp_misc['mid_rc'],
                                               self.qsObj.msp_misc['min_throttle'],
                                               self.qsObj.msp_misc['max_throttle'],
                                               self.qsObj.msp_misc['min_command'],
                                               self.qsObj.msp_misc['failsafe_throttle'],
                                               self.qsObj.msp_misc['gps_provider'],
                                               self.qsObj.msp_misc['gps_baudrate'],
                                               self.qsObj.msp_misc['gps_sbas_mode'],
                                               self.qsObj.msp_misc['reserve1'],
                                               self.qsObj.msp_misc['rssi_channel'],
                                               self.qsObj.msp_misc['reserve2'],
                                               self.qsObj.msp_misc['mag_declination'],
                                               self.qsObj.msp_misc['voltage_scale'],
                                               self.qsObj.msp_misc['voltage_cell_min'],
                                               self.qsObj.msp_misc['voltage_cell_max'],
                                               self.qsObj.msp_misc['voltage_cell_warning']])
        self.sendPacket(tempPacket)

        # MSPV2_INAV_SET_MISC

        # 3D
        # MSP_SET_3D
        tempPacket = self.constructSendPacket(6, MSPv1.MSP_SET_3D,
                                              [self.qsObj.msp_3d['deadband3d_low'],
                                               self.qsObj.msp_3d['deadband3d_high'],
                                               self.qsObj.msp_3d['neutral3d'] ])
        self.sendPacket(tempPacket)

        # Name
        # MSP_SET_NAME
        # Max Name Size: 16 characters
        tempPacket = self.constructSendPacket(len(self.qsObj.msp_name), MSPv1.MSP_SET_NAME, [ord(x) for x in list(self.qsObj.msp_name)])
        self.sendPacket(tempPacket)

        # ESC/Motor Features
        # MSP_ADVANCED_CONFIG, MSP_MISC
        # MSP_MISC is set above.
        tempPacket = self.constructSendPacket(9, MSPv1.MSP_SET_ADVANCED_CONFIG,
                                              [self.qsObj.msp_advanced_config['reserve1'],
                                               self.qsObj.msp_advanced_config['reserve2'],
                                               self.qsObj.msp_advanced_config['reserve3'],
                                               self.qsObj.msp_advanced_config['motor_pwm_protocol'],
                                               self.qsObj.msp_advanced_config['motor_pwm_rate'],
                                               self.qsObj.msp_advanced_config['servo_pwm_rate'],
                                               self.qsObj.msp_advanced_config['gyro_sync'] ])
        self.sendPacket(tempPacket)

        # System Configuration
        # MSP_INAV_PID, MSP_LOOP_TIME, MSP_ADVANCED_CONFIG
        # MSP_LOOP_TIME and MSP_ADVANCED_CONFIG are set above.
        tempPacket = self.constructSendPacket(15, MSPv1.MSP_SET_INAV_PID,
                                              [self.qsObj.msp_inav_pid['async_mode'],
                                               self.qsObj.msp_inav_pid['acc_task_frequency'],
                                               self.qsObj.msp_inav_pid['attitude_task_frequency'],
                                               self.qsObj.msp_inav_pid['heading_hold_rate_limit'],
                                               self.qsObj.msp_inav_pid['heading_hold_error_lpf_freq'],
                                               self.qsObj.msp_inav_pid['yaw_jump_prevention_limit'],
                                               self.qsObj.msp_inav_pid['gyro_lpf'],
                                               self.qsObj.msp_inav_pid['acc_soft_lpf_hz'],
                                               self.qsObj.msp_inav_pid['reserve1'],
                                               self.qsObj.msp_inav_pid['reserve2'],
                                               self.qsObj.msp_inav_pid['reserve3'],
                                               self.qsObj.msp_inav_pid['reserve4'] ])
        self.sendPacket(tempPacket)

        # Battery Voltage
        # MSP_SET_MISC
        # MSP_SET_MISC is set above.

        # Current Sensor
        # MSP_SET_CURRENT_METER_CONFIG
        tempPacket = self.constructSendPacket(7, MSPv1.MSP_SET_CURRENT_METER_CONFIG,
                                              [self.qsObj.msp_current_meter_config['scale'],
                                               self.qsObj.msp_current_meter_config['offset'],
                                               self.qsObj.msp_current_meter_config['type'],
                                               self.qsObj.msp_current_meter_config['capabity_value'] ])
        self.sendPacket(tempPacket)

        # Battery Capacity

        # Failsafe
        # MSP_SET_RX_CONFIG, MSP_SET_FAILSAFE_CONFIG
        # MSP_SET_RX_CONFIG is set above.
        tempPacket = self.constructSendPacket(20, MSPv1.MSP_SET_FAILSAFE_CONFIG,
                                              [self.qsObj.msp_failsafe_config['failsafe_delay'],
                                               self.qsObj.msp_failsafe_config['failsafe_off_delay'],
                                               self.qsObj.msp_failsafe_config['failsafe_throttle'],
                                               self.qsObj.msp_failsafe_config['failsafe_kill_switch'],
                                               self.qsObj.msp_failsafe_config['failsafe_throttle_low_delay'],
                                               self.qsObj.msp_failsafe_config['failsafe_procedure'],
                                               self.qsObj.msp_failsafe_config['failsafe_recovery_delay'],
                                               self.qsObj.msp_failsafe_config['failsafe_fw_roll_angle'],
                                               self.qsObj.msp_failsafe_config['failsafe_fw_pitch_angle'],
                                               self.qsObj.msp_failsafe_config['failsafe_fw_yaw_rate'],
                                               self.qsObj.msp_failsafe_config['failsafe_stick_motion_threshold'],
                                               self.qsObj.msp_failsafe_config['failsafe_min_distance'],
                                               self.qsObj.msp_failsafe_config['failsafe_min_distance_procedure'] ])
        self.sendPacket(tempPacket)

        # MSP_SET_BF_CONFIG

        # Other Features
        # MSP_SET_FEATURE
        # print(self.qsObj.msp_feature)
        tempPacket = self.constructSendPacket(4, MSPv1.MSP_SET_FEATURE, [self.qsObj.msp_feature['mask']])
        self.sendPacket(tempPacket)

        # Save settings to EEPROM
        print("Configure Saved")
        # Save to EEPROM
        self.saveToEEPROM()
        # Reboot
        self.reboot()

    def processTopologyCheck(self):
        # Network Configure
        # MSP_NETWORK_CONFIG
        self.readFromFC(0, MSPv1.MSP_NETWORK_CONFIG, [])
        # Address
        # # MSP_XBEE_SELF_TELEMETRY_ADDR
        # self.readFromFC(0, MSPv1.MSP_XBEE_SELF_TELEMETRY_ADDR, [])
        # # MSP_XBEE_TELEMETRY_SOURCE_ADDR
        # self.readFromFC(0, MSPv1.MSP_XBEE_TELEMETRY_SOURCE_ADDR, [])
        # # MSP_XBEE_TELEMETRY_DESTINATION_ADDR
        # self.readFromFC(0, MSPv1.MSP_XBEE_TELEMETRY_DESTINATION_ADDR, [])
        # # MSP_XBEE_SELF_RC_ADDR
        # self.readFromFC(0, MSPv1.MSP_XBEE_SELF_RC_ADDR, [])
        # # MSP_XBEE_RC_SOURCE_ADDR
        # self.readFromFC(0, MSPv1.MSP_XBEE_RC_SOURCE_ADDR, [])
        # Formation Configure
        # MSP_FORMATION_CONFIG
        self.readFromFC(0, MSPv1.MSP_FORMATION_CONFIG, [])

    def processTopologySave(self):
        # Network
        tempPacket = self.constructSendPacket(36, MSPv1.MSP_SET_NETWORK_CONFIG,
                                              [self.qsObj.msp_network_config['selfTeleAddressLow'],
                                               self.qsObj.msp_network_config['teleSource1AddressLow'],
                                               self.qsObj.msp_network_config['teleSource2AddressLow'],
                                               self.qsObj.msp_network_config['teleSource3AddressLow'],
                                               self.qsObj.msp_network_config['teleDestination1AddressLow'],
                                               self.qsObj.msp_network_config['teleDestination2AddressLow'],
                                               self.qsObj.msp_network_config['teleDestination3AddressLow'],
                                               self.qsObj.msp_network_config['selfRemoteAddressLow'],
                                               self.qsObj.msp_network_config['remoteSourceAddressLow'] ])
        self.sendPacket(tempPacket)
        # # Address
        # # MSP_SET_XBEE_SELF_TELEMETRY_ADDR
        # tempPacket = self.constructSendPacket(4, MSPv1.MSP_SET_XBEE_SELF_TELEMETRY_ADDR,
        #                                       [self.qsObj.msp_xbee_self_telemetry_addr])
        # self.sendPacket(tempPacket)
        # # MSP_SET_XBEE_TELEMETRY_SOURCE_ADDR
        # tempPacket = self.constructSendPacket(12, MSPv1.MSP_SET_XBEE_TELEMETRY_SOURCE_ADDR,
        #                                       self.qsObj.msp_xbee_telemetry_source_addr)
        # self.sendPacket(tempPacket)
        # # MSP_SET_XBEE_TELEMETRY_DESTINATION_ADDR
        # tempPacket = self.constructSendPacket(12, MSPv1.MSP_SET_XBEE_TELEMETRY_DESTINATION_ADDR,
        #                                       self.qsObj.msp_xbee_telemetry_destination_addr)
        # self.sendPacket(tempPacket)
        # # MSP_SET_XBEE_SELF_RC_ADDR
        # tempPacket = self.constructSendPacket(4, MSPv1.MSP_SET_XBEE_SELF_RC_ADDR,
        #                                       [self.qsObj.msp_xbee_self_rc_addr])
        # self.sendPacket(tempPacket)
        # # MSP_SET_XBEE_RC_SOURCE_ADDR
        # tempPacket = self.constructSendPacket(4, MSPv1.MSP_SET_XBEE_RC_SOURCE_ADDR,
        #                                       [self.qsObj.msp_xbee_rc_source_addr])
        # self.sendPacket(tempPacket)
        # Formation Configure: Gain and Target
        # MSP_SET_FORMATION_CONFIG
        # To do, firmware changed.
        tempPacket = self.constructSendPacket(22, MSPv1.MSP_SET_FORMATION_CONFIG,
                                              [self.qsObj.msp_formation_config['flight_height'],
                                               self.qsObj.msp_formation_config['distance_gain'],
                                               self.qsObj.msp_formation_config['area_gain'],
                                               self.qsObj.msp_formation_config['lat_gain'],
                                               self.qsObj.msp_formation_config['lon_gain'],
                                               self.qsObj.msp_formation_config['graph_type'],
                                               self.qsObj.msp_formation_config['identity'],
                                               self.qsObj.msp_formation_config['d_ji'],
                                               self.qsObj.msp_formation_config['d_ki'],
                                               self.qsObj.msp_formation_config['d_kj'],
                                               self.qsObj.msp_formation_config['ad']
                                              ])
        self.sendPacket(tempPacket)

        print("Topology Saved")
        # Save to EEPROM
        self.saveToEEPROM()
        # Reboot
        self.reboot()

    def processDump(self):
        # self.readFromFC(0, MSPv1.MSP_LOOP_TIME, [])
        # self.readFromFC(0, MSPv1.MSP_PID, [])
        # self.readFromFC(0, MSPv1.MSP_PIDNAMES, [])
        # self.readFromFC(0, MSPv1.MSP_PID_CONTROLLER, [])
        # self.readFromFC(0, MSPv1.MSP_CF_SERIAL_CONFIG, [])
        # self.readFromFC(0, MSPv1.MSP_ACTIVEBOXES, [])
        # self.readFromFC(0, MSPv1.MSP_MODE_RANGES, [])
        # self.readFromFC(0, MSPv1.MSP_BOXIDS, [])
        # self.readFromFC(0, MSPv1.MSP_BOXNAMES, [])
        # self.readFromFC(0, MSPv1.MSP_BOARD_INFO, [])
        # self.readFromFC(0, MSPv1.MSP_GPSSVINFO, [])
        # self.readFromFC(0, MSPv1.MSP_GPSSTATISTICS, [])
        # self.readFromFC(0, MSPv1.MSP_RAW_GPS, [])
        # self.readFromFC(0, MSPv1.MSP_COMP_GPS, [])
        # self.readFromFC(0, MSPv1.MSP_NAV_STATUS, [])
        # dumpCMDList = [MSPv1.MSP_IDENT, MSPv1.MSP_INAV_PID, MSPv1.MSP_LOOP_TIME,
        #                MSPv1.MSP_ADVANCED_CONFIG, MSPv1.MSP_FILTER_CONFIG,
        #                MSPv1.MSP_PID_ADVANCED, MSPv1.MSP_RC_TUNING,
        #                MSPv1.MSP2MSP2_INAV_RATE_PROFILE, MSPv1.MSP_PID,
        #                MSPv1.MSP_PIDNAMES, MSPv1.MSP_STATUS, MSPv1.MSP_BF_CONFIG,
        #                MSPv1.MSP2_INAV_STATUS, MSPv1.MSP_STATUS_EX, MSPv1.MSP_MISC,
        #                MSPv1.MSP2_INAV_MISC, MSPv1.MSP2_INAV_OUTPUT_MAPPING,
        #                MSPv1.MSP2_BATTERY_CONFIG, MSPv1.MSP_ARMING_CONFIG,
        #                MSPv1.MSP_RX_CONFIG, MSPv1.MSP_3D, MSPv1.MSP_SENSOR_ALIGNMENT,
        #                MSPv1.MSP_SENSOR_CONFIG, MSPv1.MSP_SENSOR_STATUS, MSPv1.MSP_RC_DEADBAND,
        #                MSPv1.MSP_RX_MAP, MSPv1.MSP_RC, MSPv1.MSP_ACC_TRIM, MSPv1.MSP_ANALOG,
        #                MSPv1.MSP_EEPROM_WRITE, MSPv1.MSP_NAV_POSHOLD,
        #                MSPv1.MSP_POSITION_ESTIMATION_CONFIG, MSPv1.MSP_CALIBRATION_DATA,
        #                MSPv1.MSP_RTH_AND_LAND_CONFIG, MSPv1.MSP_WP_GETINFO,
        #                MSPv1.MSP_SERVO_CONFIGURATIONS, MSPv1.MSP_SERVO_MIX_RULES,
        #                MSPv1.MSP2_COMMON_MOTOR_MIXER, MSPv1.MSP_MOTOR, MSPv1.MSP_NAME,
        #                MSPv1.MSP2_INAV_MIXER, MSPv1.MSP_VTX_CONFIG, MSPv1.MSP2_COMMON_PG_LIST]
        # writeCMDList = [MSPv1.MSP_SET_INAV_PID, MSPv1.MSP_SET_LOOP_TIME, MSPv1.MSP_SET_ADVANCED_CONFIG,
        #                 MSPv1.MSP_SET_FILTER_CONFIG, MSPv1.MSP_SET_PID, MSPv1.MSP_SET_RC_TUNING,
        #                 MSPv1.MSP2_INAV_SET_RATE_PROFILE, MSPv1.MSP_SET_PID_ADVANCED,
        #                 MSPv1.MSP_SET_BF_CONFIG, MSPv1.MSP_SET_MISC, MSPv1.MSP2_INAV_SET_MISC,
        #                 MSPv1.MSP2_SET_BATTERY_CONFIG, MSPv1.MSP_SET_3D, MSPv1.MSP_SET_SENSOR_ALIGNMENT,
        #                 MSPv1.MSP_SET_ARMING_CONFIG, MSPv1.MSP_SET_RX_CONFIG,
        #                 MSPv1.MSP_SET_SENSOR_CONFIG, MSPv1.MSP_SET_NAV_POSHOLD,
        #                 MSPv1.MSP_SET_POSITION_ESTIMATION_CONFIG, MSPv1.MSP_SET_CALIBRATION_DATA,
        #                 MSPv1.MSP_SET_RTH_AND_LAND_CONFIG, MSPv1.MSP_SET_NAME, MSPv1.MSP2_INAV_SET_MIXER,
        #                 MSPv1.MSP_SET_VTX_CONFIG]
        try:
            # self.readFromFC(0, MSPv1.MSP_ARMING_CONFIG, [])
            # self.readFromFC(0, MSPv1.MSP_STATUS, [])
            # self.readFromFC(0, MSPv1.MSP_STATUS_EX, [])
            # self.parseSensorStatus()
            # self.parseArmingFlags()
            # self.readFromFC(0, MSPv1.MSP_RX_MAP, [])
            # self.readFromFC(0, MSPv1.MSP_ACTIVEBOXES, [])
            # self.parseActiveFlightModeFlags()
            #self.readFromFC(0, MSPv1.MSP_API_VERSION, [])
            #self.processFeature()
            #self.readFromFC(0, MSPv1.MSP_IDENT, [])
            #self.readFromFC(0, MSPv1.MSP_BUILD_INFO, [])
            #self.readFromFC(0, MSPv1.MSP_SENSOR_STATUS, [])
            #self.readFromFC(0, MSPv1.MSP_ACTIVEBOXES, [])
            #self.readFromFC(0, MSPv1.MSP_RAW_IMU, [])
            # self.dumpFormattedPrint()
            # self.readFromFC(0, MSPv1.MSP_FAILSAFE_CONFIG, [])
            # print(self.qsObj.msp_failsafe_config)
            # self.readFromFC(0, MSPv1.MSP_CF_SERIAL_CONFIG, [])
            # print(self.qsObj.msp_cf_serial_config)
            pass
        except Exception:  # serial.serialutil.SerialException
            print(Exception)
            pass

    def processHelp(self):
        pass

    def allTypeToString(self, tempData):
        print(type(tempData))

    def dumpFormattedPrint(self):
        # Serialize all the data structures for CLI print.
        self.cliFeedbackSignal.emit("---Start of dump---")
        self.cliFeedbackSignal.emit(str(self.qsObj.msp_cf_serial_config))
        self.cliFeedbackSignal.emit(str(self.qsObj.msp_status_ex))
        self.cliFeedbackSignal.emit(str(self.qsObj.parsed_armingflags))
        self.cliFeedbackSignal.emit(str(self.qsObj.msp_rx_map))
        self.cliFeedbackSignal.emit("---End of dump---")
        # print(self.qsObj.msp_activeboxes)
        # print(self.qsObj.msp_boxids)
        # print(self.qsObj.msp_boxnames)
        # print(self.qsObj.msp_mode_ranges)

    def processSerialTerminalRequest(self):
        rec_packet = self.readPacket2()
        data_length = len(rec_packet)
        if data_length > 0:
            temp1 = struct.unpack('<'+'B'*data_length, rec_packet)
            temp2 = [chr(x) for x in temp1]
            ret_str = "".join(temp2)
            self.serTerFeedbackSignal.emit(ret_str)

    def processDiff(self):
        # Show the difference between current settings and default settings
        pass

    def processUploadMissions(self):
        self.qsObj.missionList = [[1, 1, 303883398, -911956624, 1000, 0, 0, 0, 0],
                                  [2, 1, 303840452, -911958364, 1000, 0, 0, 0, 0],
                                  [3, 1, 303841912, -911909561, 1000, 0, 0, 0, 165]
                                 ]
        self.uploadMissions()

    def processDownloadMissions(self):
        self.downloadMissions()

    def saveToEEPROM(self):
        # Save settings to EEPROM
        tempPacket = self.constructSendPacket(0, MSPv1.MSP_EEPROM_WRITE, [])
        self.sendPacket(tempPacket)
        print("EEPROM Saved")

    def reboot(self):
        # Reboot board
        # Enable the code below after all tested
        tempPacket = self.constructSendPacket(0, MSPv1.MSP_REBOOT, [])
        self.sendPacket(tempPacket)
        # Reboot Configurator
        self.rebootSignal.emit()
        pass

    # Using, Checked
    def processModeRangesSave(self, modeRangeList):
        for i in range(len(modeRangeList)):
            numberedModeRange = [i] + modeRangeList[i]
            tempPacket = self.constructSendPacket(5, MSPv1.MSP_SET_MODE_RANGE, numberedModeRange)
            self.sendPacket(tempPacket)
        self.saveToEEPROM()

    def parseFeature(self):
        featureMask = self.qsObj.msp_feature['mask']
        temp = format(featureMask, '032b')

    # Using, Checked
    def parseSensorStatus(self):
        sensorStatus = self.qsObj.msp_status_ex['activeSensors']
        temp = format(sensorStatus, '016b')
        self.qsObj.parsed_activesensors['hardware'] = int(temp[0])
        self.qsObj.parsed_activesensors['pitot'] = int(temp[9])
        self.qsObj.parsed_activesensors['range'] = int(temp[11])
        self.qsObj.parsed_activesensors['gps'] = int(temp[12])
        self.qsObj.parsed_activesensors['mag'] = int(temp[13])
        self.qsObj.parsed_activesensors['baro'] = int(temp[14])
        self.qsObj.parsed_activesensors['acc'] = int(temp[15])

    # Using, Checked
    def parseArmingFlags(self):
        armflag = self.qsObj.msp_status_ex['armingFlags']
        temp = format(armflag, '016b')
        self.qsObj.parsed_armingflags['OK_TO_ARM'] = temp[15]
        self.qsObj.parsed_armingflags['PREVENT_ARMING'] = temp[14]
        self.qsObj.parsed_armingflags['ARMED'] = temp[13]
        self.qsObj.parsed_armingflags['WAS_EVER_ARMED'] = temp[12]
        self.qsObj.parsed_armingflags['BLOCK_UAV_NOT_LEVEL'] = temp[7]
        self.qsObj.parsed_armingflags['BLOCK_SENSORS_CALIB'] = temp[6]
        self.qsObj.parsed_armingflags['BLOCK_SYSTEM_OVERLOAD'] = temp[5]
        self.qsObj.parsed_armingflags['BLOCK_NAV_SAFETY'] = temp[4]
        self.qsObj.parsed_armingflags['BLOCK_COMPASS_NOT_CALIB'] = temp[3]
        self.qsObj.parsed_armingflags['BLOCK_ACC_NOT_CALIB'] = temp[2]
        self.qsObj.parsed_armingflags['UNUSED'] = temp[1]
        self.qsObj.parsed_armingflags['BLOCK_HARDWARE_FAILURE'] = temp[0]

    # Using, Checked
    def parseActiveFlightModeFlags(self):
        activeboxes = self.qsObj.msp_activeboxes[0]
        flightModeIDList = self.qsObj.msp_boxids
        flightModeNameList = self.qsObj.msp_boxnames
        if activeboxes == 0:
            return False
        else:
            tempStr = format(activeboxes, '032b')
            tempActiveModeList = []
            for i in range(len(tempStr)):
                tempBit = tempStr[31-i]
                if tempBit == '1':
                    tempActiveModeList.append(flightModeNameList[i])
            self.qsObj.parsed_activeboxes = tempActiveModeList

    # Using, Checked
    # upload mission will automatically download the mission and compare it
    def uploadMission(self, mission):
        while True:
            send_packet = self.constructSendPacket(21, MSPv1.MSP_SET_WP, mission)
            self.sendPacket(send_packet)
            index = mission[0]
            tempRecMission = self.downloadMission(index)
            uploadStatus = self.checkMissionUpload(mission, tempRecMission)
            if uploadStatus == True:
                print(tempRecMission)
                break
            else:
                pass

    # Using, Checked
    def checkMissionUpload(self, missionSend, missionRec):
        if missionSend[:-1] == missionRec[:-1]:
            return True
        else:
            return False

    # Using, Checked
    def uploadMissions(self):
        missionList = self.qsObj.missionList
        for i in range(len(missionList)):
            self.uploadMission(missionList[i])

    # Using, Checked
    def downloadMission(self, id):
        mission = []
        while True:
            self.readFromFC(1, MSPv1.MSP_WP, [id])
            if len(self.qsObj.tempMission) > 0:
                if self.qsObj.tempMission[0] == id:
                    mission = self.qsObj.tempMission
                    break
        return mission

    # Using, Checked
    def downloadMissions(self):
        missionList = []
        i = 1
        while True:
            flag = 0
            tempRecMission = self.downloadMission(i)
            missionList.append(tempRecMission)
            print(tempRecMission)
            flag = tempRecMission[8]
            if flag == 165:
                break
            else:
                i = i + 1
        return missionList

    def arm(self, obj):
        send_packet = self.constructSendPacket(16, MSPv1.MSP_SET_RAW_RC, [1500, 1500, 1000, 1500, 1350, 1000, 1000, 1000])
        self.sendPacket(send_packet)

    def disarm(self, obj):
        send_packet = self.constructSendPacket(16, MSPv1.MSP_SET_RAW_RC, [1500, 1500, 1000, 1500, 1000, 1000, 1000, 1000])
        self.sendPacket(send_packet)
