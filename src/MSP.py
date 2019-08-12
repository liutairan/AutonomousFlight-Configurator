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
# from xbee import ZigBee
import signal
from contextlib import contextmanager

class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise (TimeoutException, "Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.alarm(0)

def message_received(data):
    print(len(data))

class MSP:
    # Multiwii MSP Commands
    API_VERSION = 1
    FC_VARIANT = 2
    FC_VERSION = 3
    BOARD_INFO = 4
    BUILD_INFO = 5

    MSP_INAV_PID = 6
    MSP_SET_INAV_PID = 7

    MSP_NAME = 10
    MSP_SET_NAME = 11

    NAV_POSHOLD = 12
    SET_NAV_POSHOLD = 13

    MODE_RANGES = 34    # MSP_MODE_RANGES    out message         Returns all mode ranges
    SET_MODE_RANGE = 35 # MSP_SET_MODE_RANGE in message          Sets a single mode range

    MSP_FEATURE = 36
    MSP_SET_FEATURE = 37

    MSP_BOARD_ALIGNMENT = 38
    MSP_SET_BOARD_ALIGNMENT = 39

    MSP_RX_CONFIG = 44
    MSP_SET_RX_CONFIG = 45

    MSP_ADJUSTMENT_RANGES = 52
    MSP_SET_ADJUSTMENT_RANGE = 53

    MSP_SONAR_ALTITUDE = 58      # SONAR cm

    MSP_PID_CONTROLLER = 59
    MSP_SET_PID_CONTROLLER = 60

    MSP_ARMING_CONFIG = 61         # out message         Returns auto_disarm_delay and disarm_kill_switch parameters
    MSP_SET_ARMING_CONFIG = 62     # in message          Sets auto_disarm_delay and disarm_kill_switch parameters

    REBOOT = 68    # in message reboot settings

    MSP_LOOP_TIME = 73 # out message         Returns FC cycle time i.e looptime parameter
    MSP_SET_LOOP_TIME = 74 # in message          Sets FC cycle time i.e looptime parameter

    MSP_FAILSAFE_CONFIG = 75 # out message         Returns FC Fail-Safe settings
    MSP_SET_FAILSAFE_CONFIG = 76 #in message          Sets FC Fail-Safe settings

    MSP_RXFAIL_CONFIG = 77 # out message         Returns RXFAIL settings
    MSP_SET_RXFAIL_CONFIG = 78 # in message          Sets RXFAIL settings

    IDENT = 100
    STATUS = 101
    RAW_IMU = 102
    SERVO = 103
    MOTOR = 104
    RC = 105
    RAW_GPS = 106
    COMP_GPS = 107
    ATTITUDE = 108
    ALTITUDE = 109
    ANALOG = 110
    RC_TUNING = 111
    PID = 112
    BOX = 113
    MISC = 114
    MOTOR_PINS = 115
    BOXNAMES = 116
    PIDNAMES = 117
    WP = 118
    BOXIDS = 119
    CONTROL = 120
    NAV_STATUS = 121
    NAV_CONFIG = 122
    MSP_3D = 124
    MSP_RC_DEADBAND = 125
    MSP_SENSOR_ALIGNMENT = 126

    MSP_STATUS_EX = 150    # out message         cycletime, errors_count, CPU load, sensor present etc
    MSP_SENSOR_STATUS = 151    # out message         Hardware sensor status
    MSP_UID = 160    # out message         Unique device ID

    GPSSVINFO = 164
    GPSSTATISTICS = 166

    RADIO = 199
    SET_RAW_RC = 200
    SET_RAW_GPS = 201  # in message          fix, numsat, lat, lon, alt, speed
    SET_PID = 202      # in message          P I D coeff (9 are used currently)
    SET_BOX = 203
    SET_RC_TUNING = 204
    ACC_CALIBRATION = 205
    MAG_CALIBRATION = 206
    SET_MISC = 207
    RESET_CONF = 208
    SET_WP = 209
    SELECT_SETTING = 210
    #SWITCH_RC_SERIAL = 210
    SET_HEAD = 211
    #IS_SERIAL = 211
    MSP_SET_SERVO_CONFIGURATION = 212
    MSP_SET_MOTOR = 214
    MSP_SET_NAV_CONFIG = 215
    MSP_SET_3D = 217
    MSP_SET_RC_DEADBAND = 218
    MSP_SET_RESET_CURR_PID = 219
    MSP_SET_SENSOR_ALIGNMENT = 220

    MSP_ACC_TRIM = 240    # out message         get acc angle trim values
    MSP_SET_ACC_TRIM = 239    # in message          set acc angle trim values
    MSP_SERVO_MIX_RULES = 241    # out message         Returns servo mixer configuration
    MSP_SET_SERVO_MIX_RULE = 242    # in message          Sets servo mixer configuration
    MSP_SET_4WAY_IF = 245    # in message          Sets 4way interface


    EEPROM_WRITE = 250
    DEBUG = 254

    INFO_WP = 400

    """Class initialization"""
    def __init__(self, serPort):
        self.elapsed = 0
        self.PRINT = 1

        self.ser = serial.Serial()
        self.ser.port = serPort
        self.ser.baudrate = 115200
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout = 1
        self.ser.xonxoff = False
        self.ser.rtscts = False
        self.ser.dsrdtr = False
        self.ser.writeTimeout = 2
        # self.zb = ZigBee(self.ser)
        """Time to wait until the board becomes operational"""
        wakeup = 3
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
        except (Exception, error):
            print("\n\nError opening "+self.ser.port+" port.\n"+str(error)+"\n\n")

    def flushSerial(self):
        self.ser.flushInput()
        self.ser.flushOutput()

    def stopDevice(self):
        # self.zb.halt()
        self.ser.close()

    def getData(self, data_length, send_code, send_data): #
        try:
            start = time.time()
            totaldata = self.requestData(data_length, send_code, send_data, obj)
            datalength = struct.unpack('<B', totaldata[3])[0]
            #print(datalength)
            cmd = struct.unpack('<B', totaldata[4])[0]
            data = totaldata[5:]

            elapsed = time.time() - start
            if cmd == MultiWii.ATTITUDE:
                temp = struct.unpack('<'+'h'*(datalength/2)+'B',data)
                #obj.attitude['angx']=float(temp[0]/10.0)
                #obj.attitude['angy']=float(temp[1]/10.0)
                #obj.attitude['heading']=float(temp[2])
                #self.attitude['elapsed']=round(elapsed,3)
                #self.attitude['timestamp']="%0.2f" % (time.time(),)
                # obj.msp_attitude['angx'] = float(temp[0]/10.0)
                # obj.msp_attitude['angy'] = float(temp[1]/10.0)
                # obj.msp_attitude['heading'] = float(temp[2])
                #return self.attitude
            elif cmd == MultiWii.RC:           # checked
                temp = struct.unpack('<'+'h'*(datalength/2)+'B',data)
                # obj.rcChannels['roll']=temp[0]
                # obj.rcChannels['pitch']=temp[1]
                # obj.rcChannels['yaw']=temp[2]
                # obj.rcChannels['throttle']=temp[3]
                # obj.rcChannels['aux1'] = temp[4]
                # obj.rcChannels['aux2'] = temp[5]
                # obj.rcChannels['aux3'] = temp[6]
                # obj.rcChannels['aux4'] = temp[7]
                # # to do aux
                # obj.rcChannels['elapsed']=round(elapsed,3)
                # obj.rcChannels['timestamp']="%0.2f" % (time.time(),)
                #return self.rcChannels
            elif cmd == MultiWii.RAW_IMU:       # checked
                temp = struct.unpack('<'+'h'*(datalength/2)+'B',data)
                # obj.rawIMU['ax']=float(temp[0])
                # obj.rawIMU['ay']=float(temp[1])
                # obj.rawIMU['az']=float(temp[2])
                # obj.rawIMU['gx']=float(temp[3])
                # obj.rawIMU['gy']=float(temp[4])
                # obj.rawIMU['gz']=float(temp[5])
                # obj.rawIMU['mx']=float(temp[6])
                # obj.rawIMU['my']=float(temp[7])
                # obj.rawIMU['mz']=float(temp[8])
                # obj.rawIMU['elapsed']=round(elapsed,3)
                # obj.rawIMU['timestamp']="%0.2f" % (time.time(),)
                #return self.rawIMU
            elif cmd == MultiWii.MOTOR:
                temp = struct.unpack('<'+'h'*(datalength/2)+'B',data)
                # obj.motor['m1']=float(temp[0])
                # obj.motor['m2']=float(temp[1])
                # obj.motor['m3']=float(temp[2])
                # obj.motor['m4']=float(temp[3])
                # obj.motor['elapsed']="%0.3f" % (elapsed,)
                # obj.motor['timestamp']="%0.2f" % (time.time(),)
                return self.motor
            elif cmd == MultiWii.STATUS:
                temp = struct.unpack('<3HI2B',data)
                # obj.msp_status['cycleTime'] = temp[0]
                # obj.msp_status['i2cError'] = temp[1]
                # obj.msp_status['activeSensors'] = temp[2]
                # obj.msp_status['flightModeFlags'] = temp[3]
                # obj.msp_status['profile'] = temp[4]
            elif cmd == MultiWii.MSP_STATUS_EX:       # checked
                temp = struct.unpack('<3HIB2HB',data)
                print(temp)
                # obj.msp_status_ex['cycletime'] = temp[0]
                # obj.msp_status_ex['i2cError'] = temp[1]
                # obj.msp_status_ex['activeSensors'] = temp[2]
                # obj.msp_status_ex['flightModeFlags'] = temp[3]
                # obj.msp_status_ex['profile'] = temp[4]
                # obj.msp_status_ex['averageSystemLoadPercent'] = temp[5]
                # obj.msp_status_ex['armingFlags'] = temp[6]

            elif cmd == MultiWii.MSP_SENSOR_STATUS:
                temp = struct.unpack('<9B',data)
                # to do

            elif cmd == MultiWii.MSP_LOOP_TIME:
                temp = struct.unpack('<HB',data)
                obj.msp_loop_time['looptime'] = temp[0]

            elif cmd == MultiWii.API_VERSION:
                temp = struct.unpack('<4B',data)
                # obj.msp_api_version['msp_protocol_version'] = temp[0]
                # obj.msp_api_version['api_version_major'] = temp[1]
                # obj.msp_api_version['api_version_minor'] = temp[2]
            elif cmd == MultiWii.BOARD_INFO:
                temp = struct.unpack('<'+'b'*(datalength-3) + 'HB',data)
                # obj.msp_board_info['board_identifier'] = temp[0]
                # obj.msp_board_info['hardware_revision'] = temp[1]

            elif cmd == MultiWii.IDENT:
                temp = struct.unpack('<3BIB',data)
                # obj.msp_ident['version'] = temp[0]
                # obj.msp_ident['multitype'] = temp[1]
                # obj.msp_ident['msp_version'] = temp[2]
                # obj.msp_ident['capability'] = temp[3]

            elif cmd == MultiWii.MISC:
                temp = struct.unpack('<6HIH4B',data) # not right
                # obj.msp_misc['intPowerTrigger1'] = temp[0]
                # obj.msp_misc['maxthrottle'] = temp[2]
                # obj.msp_misc['mincommand'] = temp[3]
                # to do
            elif cmd == MultiWii.ALTITUDE:         # may not working
                temp = struct.unpack('<IHB',data)
                # obj.msp_altitude['estalt'] = temp[0]
                # obj.msp_altitude['vario'] = temp[1]

            elif cmd == MultiWii.RADIO:
                temp = struct.unpack('<2H6B',data)
                # obj.msp_radio['rxerrors'] = temp[0]
                # obj.msp_radio['fixed_errors'] = temp[1]
                # obj.msp_radio['localrssi'] = temp[2]
                # obj.msp_radio['remrssi'] = temp[3]
                # obj.msp_radio['txbuf'] = temp[4]
                # obj.msp_radio['noise'] = temp[5]
                # obj.msp_radio['remnoise'] = temp[6]

            elif cmd == MultiWii.MSP_SONAR_ALTITUDE: # checked
                temp = struct.unpack('<iB',data)
                # obj.msp_sonar_altitude['sonar_altitude'] = temp[0]

            elif cmd == MultiWii.ANALOG:          # checked, vbat:109
                temp = struct.unpack('<B3HB',data)
                # obj.msp_analog['vbat'] = temp[0]
                # obj.msp_analog['powermetersum'] = temp[1]
                # obj.msp_analog['rssi'] = temp[2]
                # obj.msp_analog['amps'] = temp[3]
            elif cmd == MultiWii.MODE_RANGES:
                # not working,
                # because the data feedback should be '3c2B'+'80B'+'B',
                # longer than the permitted length of XBEE S2 AT ROUTER (84 Bytes).
                # So the data is separated to 2 frames.
                # But there are only two bytes (one byte for real range data, one byte for checksum) in the second frame,
                # so it does not worth to wait for another frame.
                #print(datalength)
                #print(len(data))
                temp = struct.unpack('<'+'B'*(len(data)),data)
                print(temp)
                # to do
            elif cmd == MultiWii.MSP_ADJUSTMENT_RANGES:
                pass
                # to do
            elif cmd == MultiWii.BOXIDS: # checked
                temp = struct.unpack('<'+'B'*datalength + 'B',data)
                # obj.activeBoxes = list(temp)
                # to do
            elif cmd == MultiWii.RAW_GPS:
                temp = struct.unpack('<2B2i4HB',data)  # with checksum
                # obj.msp_raw_gps['gps_fix'] = temp[0]
                # obj.msp_raw_gps['gps_numsat'] = temp[1]
                # obj.msp_raw_gps['gps_lat'] = temp[2]
                # obj.msp_raw_gps['gps_lon'] = temp[3]
                # obj.msp_raw_gps['gps_altitude'] = temp[4]
                # obj.msp_raw_gps['gps_speed'] = temp[5]
                # obj.msp_raw_gps['gps_ground_course'] = temp[6]
                # obj.msp_raw_gps['gps_hdop'] = temp[7]

            elif cmd == MultiWii.COMP_GPS:
                temp = struct.unpack('<2H2B',data)   # with checksum
                # obj.msp_comp_gps['range'] = temp[0]
                # obj.msp_comp_gps['direction'] = temp[1]
                # obj.msp_comp_gps['update'] = temp[2]
                # to do
            elif cmd == MultiWii.NAV_STATUS:
                temp = struct.unpack('<5BHB',data)  # with checksum
                # obj.msp_nav_status['nav_mode'] = temp[0]
                # obj.msp_nav_status['nav_state'] = temp[1]
                # obj.msp_nav_status['action'] = temp[2]
                # obj.msp_nav_status['wp_number'] = temp[3]
                # obj.msp_nav_status['nav_error'] = temp[4]
                # obj.msp_nav_status['mag_hold_heading'] = temp[5]
                # to do
            elif cmd == MultiWii.GPSSVINFO:
                temp = struct.unpack('<6B',data)     # with checksum
                # obj.msp_gps_svinfo['gps_hdop'] = temp[3]
                # to do
            elif cmd == MultiWii.GPSSTATISTICS:
                temp = struct.unpack('<H3I3HB',data)   # with checksum
                # obj.msp_gps_statistics['gps_last_message_dt'] = temp[0]
                # obj.msp_gps_statistics['gps_errors'] = temp[1]
                # obj.msp_gps_statistics['gps_timeouts'] = temp[2]
                # obj.msp_gps_statistics['gps_packet_count'] = temp[3]
                # obj.msp_gps_statistics['gps_hdop'] = temp[4]
                # obj.msp_gps_statistics['gps_eph'] = temp[5]
                # obj.msp_gps_statistics['gps_epv'] = temp[6]
                # to do
            elif cmd == MultiWii.MSP_FEATURE:
                temp = struct.unpack('<I',data)
                # to do
            elif cmd == MultiWii.MSP_BOARD_ALIGNMENT:
                temp = struct.unpack('<3H',data)
                # to do
            elif cmd == MultiWii.MSP_RX_CONFIG:
                pass
                # to do
            elif cmd == MultiWii.MSP_FAILSAFE_CONFIG:
                pass
                # to do
            elif cmd == MultiWii.MSP_RXFAIL_CONFIG:
                pass
                # to do
            elif cmd == MultiWii.MSP_SENSOR_ALIGNMENT:
                temp = struct.unpack('<3B',data)
                # to do
            elif cmd == MultiWii.WP:
                temp = struct.unpack('<2B3i3h2B',data)
                obj.tempMission = list(temp)
            else:
                return "No return error!"
        except (Exception, error):
            #print(Exception)
            #print error
            pass

    def readData(self):
        tempData = self.ser.readline()
        print(tempData)
        if len(tempData)>0:
            temp = struct.unpack('<3HIB2HB', tempData[5:21])
            print(temp)

    def requestData(self, data_length, send_code, send_data):
        rec_data = ['','','']
        while True:
            self.sendCMDNew(data_length, send_code, send_data, obj)
            try:
                with time_limit(0.005):   # 0.005
                    if send_code == MultiWii.MODE_RANGES:
                        rec_data = self.readZBMsg(1)
                    else:
                        rec_data = self.readZBMsg(1)
            except:
                pass
            # to do: check src address, if not match the obj address, then discard
            validation = self.preCheckReadData(rec_data, send_code, send_data, obj)
            if validation == True:
                break
            else:
                pass
        return rec_data[2]

    def readZBMsg(self, framenum=1):
        tempdata = ['', '', '']
        if framenum == 1:
            packet = self.zb.wait_read_frame()
            if packet['id'] == 'tx_status':
                pass
            elif packet['id'] == 'rx':
                tempdata[0] = packet['source_addr_long']
                tempdata[1] = packet['source_addr']
                tempdata[2] = packet['rf_data']
        return tempdata

    def preCheckReadData(self, rec_data_pack, send_code, send_data, obj):
        #print(rec_data_pack)
        if len(rec_data_pack[2]) >= 5:
            header = rec_data_pack[2][0:3]
            if header == '$M>':
                pass
            else:
                return False

            if (rec_data_pack[0] == obj.address_long):
                return True
            else:
                return False
        else:
            return False

    # input field "data" must be in a list
    def sendCMDNew(self, data_length, send_code, send_data):
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
                tempdata = struct.pack('<3c3B', *tempList)

                b = None
                # b = self.zb.send('tx', frame_id = frameid, dest_addr_long = d_addr_long, dest_addr=d_addr, data=tempdata)
                b = self.ser.write(tempdata)
            except (Exception, error):
                print(Exception, error)
        elif data_length > 0:
            if cmd == MultiWii.SET_RAW_RC:
                for i in struct.pack('<2B%dH' % len(send_data), *total_data[3:len(total_data)]):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempdata = struct.pack('<3c2B%dHB' % len(send_data), *total_data)
                    b = None
                    b = self.zb.send('tx', frame_id = frameid, dest_addr_long = d_addr_long, dest_addr = d_addr, data = tempdata)
                except (Exception, error):
                    pass
            elif cmd == MultiWii.WP:
                for i in struct.pack('<3B', *total_data[3:len(total_data)]):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempdata = struct.pack('<3c4B', *total_data)
                    b = None
                    b = self.zb.send('tx', frame_id = frameid, dest_addr_long = d_addr_long, dest_addr = d_addr, data = tempdata)
                except (Exception, error):
                    print(error)
            elif cmd == MultiWii.SET_WP:
                for i in struct.pack('<2B2B3i3hB', *total_data[3:len(total_data)]):
                    checksum = checksum ^ ord(i)
                total_data.append(checksum)
                try:
                    tempdata = struct.pack('<3c4B3i3h2B', *total_data)
                    b = None
                    b = self.zb.send('tx', frame_id = frameid, dest_addr_long = d_addr_long, dest_addr = d_addr, data = tempdata)
                except (Exception, error):
                    print(Exception,error)
        else:
            pass


    def parseSensorStatus(self, obj):
        sensorStatus = obj.msp_status_ex['activeSensors']
        temp = format(sensorStatus, '016b')

        obj.sensor_flags['hardware'] = int(temp[0])
        obj.sensor_flags['pitot'] = int(temp[9])
        obj.sensor_flags['sonar'] = int(temp[11])
        obj.sensor_flags['gps'] = int(temp[12])
        obj.sensor_flags['mag'] = int(temp[13])
        obj.sensor_flags['baro'] = int(temp[14])
        obj.sensor_flags['acc'] = int(temp[15])
        #print(obj.sensor_flags)

    def parseArmingFlags(self, obj):
        armflag = obj.msp_status_ex['armingFlags']
        temp = format(armflag, '016b')
        obj.armStatus['OK_TO_ARM'] = temp[15]
        obj.armStatus['PREVENT_ARMING'] = temp[14]
        obj.armStatus['ARMED'] = temp[13]
        obj.armStatus['WAS_EVER_ARMED'] = temp[12]
        obj.armStatus['BLOCK_UAV_NOT_LEVEL'] = temp[7]
        obj.armStatus['BLOCK_SENSORS_CALIB'] = temp[6]
        obj.armStatus['BLOCK_SYSTEM_OVERLOAD'] = temp[5]
        obj.armStatus['BLOCK_NAV_SAFETY'] = temp[4]
        obj.armStatus['BLOCK_COMPASS_NOT_CALIB'] = temp[3]
        obj.armStatus['BLOCK_ACC_NOT_CALIB'] = temp[2]
        obj.armStatus['UNUSED'] = temp[1]
        obj.armStatus['BLOCK_HARDWARE_FAILURE'] = temp[0]
        #print(obj.armStatus)

    def parseFlightModeFlags(self, obj):
        activeboxes = obj.activeBoxes
        flightModeFlags = obj.msp_status_ex['flightModeFlags']
        #print(flightModeFlags)
        if len(activeboxes) == 0:
            return False
        else:
            temp = format(flightModeFlags, '032b')
            armInd = activeboxes.index(0)
            angleInd = activeboxes.index(1)
            horizonInd = activeboxes.index(2)
            altholdInd = activeboxes.index(3)
            magInd = activeboxes.index(5)
            headfreeInd = activeboxes.index(6)
            headadjInd = activeboxes.index(7)
            rthInd = activeboxes.index(10)
            posholdInd = activeboxes.index(11)
            failsafeInd = activeboxes.index(27)
            navwpInd = activeboxes.index(28)
            airInd = activeboxes.index(29)
            homeresetInd = activeboxes.index(30)
            gcsnavInd = activeboxes.index(31)
            headinglockInd = activeboxes.index(32)
            surfaceInd = activeboxes.index(33)
            turnassistInd = activeboxes.index(35)
            obj.flightModes['ARM'] = int(temp[31-armInd])
            obj.flightModes['ANGLE'] = int(temp[31-angleInd])
            obj.flightModes['HORIZON'] = int(temp[31-horizonInd])
            obj.flightModes['ALTHOLD'] = int(temp[31-altholdInd])
            obj.flightModes['NAVRTH'] = int(temp[31-rthInd])
            obj.flightModes['POSHOLD'] = int(temp[31-posholdInd])
            obj.flightModes['NAVWP'] = int(temp[31-navwpInd])
            obj.flightModes['GCSNAV'] = int(temp[31-gcsnavInd])
            obj.flightModes['FAILSAFE'] = int(temp[31-failsafeInd])
            return True

    # upload mission will automatically download the mission and compare it
    def uploadMission(self, mission, obj):
        frameid = obj.frame_id
        d_addr_long = obj.address_long
        d_addr = obj.address_short

        while True:
            self.sendCMDNew(21, MultiWii.SET_WP, mission, obj)
            index = mission[0]
            tempRecMission = self.downloadMission(index, obj)
            uploadStatus = self.checkMissionUpload(mission, tempRecMission)
            if uploadStatus == True:
                #print('Rec mission')
                print(tempRecMission)
                break
            else:
                pass

    def checkMissionUpload(self, missionSend, missionRec):
        if missionSend == missionRec[:-1]:
            return True
        else:
            return False

    def uploadMissions(self, obj):
        frameid = obj.frame_id
        d_addr_long = obj.address_long
        d_addr = obj.address_short
        missionList = obj.missionList

        for i in range(len(missionList)):
            self.uploadMission(missionList[i], obj)

    # all_missions is a list: [{},{},{}], inside the list are dicts.
    # {'frameid':0, 'dest_addr_long':'', 'dest_addr':'', 'missionlist':[]}
    '''
    def uploadAllMissions(self, all_missions):
        for i in range(len(all_missions)):
            tempSendMission = all_missions[i]
            temp_frameid = tempSendMission['frameid']
            temp_d_addr_long = tempSendMission['dest_addr_long']
            temp_d_addr = tempSendMission['dest_addr']
            temp_missionList = tempSendMission['missionlist']
            self.uploadMissions(temp_missionList, temp_frameid, temp_d_addr_long, temp_d_addr)   # not right here
    '''

    def downloadMission(self, id, obj):
        frameid = obj.frame_id
        d_addr_long = obj.address_long
        d_addr = obj.address_short

        mission = []
        while True:
            self.getData(1, MultiWii.WP,[id], obj)
            if len(obj.tempMission) > 0:
                if obj.tempMission[0] == id:
                    mission = obj.tempMission
                    break
        return mission

    def downloadMissions(self, obj):
        frameid = obj.frame_id
        d_addr_long = obj.address_long
        d_addr = obj.address_short

        missionList = []
        i = 1
        while True:
            flag = 0
            tempRecMission = self.downloadMission(i, obj)
            missionList.append(tempRecMission)
            print(tempRecMission)
            flag = tempRecMission[8]
            if flag == 165:
                break
            else:
                i = i + 1

        return missionList

    # targets is a list: [{},{},{}], inside the list are dicts.
    # {'frameid':0, 'dest_addr_long':'', 'dest_addr':''}
    '''
    def downloadAllMissions(self, targets):
        for i in range(len(targets)):
            tempTarget = targets[i]
            temp_frameid = tempTarget['frameid']
            temp_d_addr_long = tempTarget['dest_addr_long']
            temp_d_addr = tempTarget['dest_addr']
            print('start download for: ' + ''.join("{:02x}".format(ord(c)) for c in temp_d_addr_long))
            self.downloadMissions(temp_frameid, temp_d_addr_long,temp_d_addr)    # not right here
    '''

    def arm(self, obj):
        self.sendCMDNew(16, MultiWii.SET_RAW_RC, [1500, 1500, 1000, 1500, 1350, 1000, 1000, 1000], obj)
        #self.getData(0,MultiWii.RC, [], obj)
        #print(obj.rcChannels['aux1'])

    def disarm(self, obj):
        self.sendCMDNew(16, MultiWii.SET_RAW_RC, [1500, 1500, 1000, 1500, 1000, 1000, 1000, 1000], obj)

    def getDataLoose(self, data_length, send_code, send_data, send_obj, allobjs): #
        frameid = send_obj.frame_id
        d_addr_long = send_obj.address_long
        d_addr = send_obj.address_short
        d_addr_list = []
        for i in range(len(allobjs)):
            d_addr_list.append(allobjs[i].address_long)

        try:
            start = time.time()
            rec_totaldata = self.requestDataLoose(data_length, send_code, send_data, send_obj, d_addr_list)
            rec_addr_long = rec_totaldata[0]
            objInd = d_addr_list.index(rec_addr_long)
            rec_obj = allobjs[objInd]

            totaldata = rec_totaldata[2]
            datalength = struct.unpack('<B', totaldata[3])[0]
            cmd = struct.unpack('<B', totaldata[4])[0]
            data = totaldata[5:]

            elapsed = time.time() - start
            if cmd == MultiWii.ATTITUDE:
                temp = struct.unpack('<'+'h'*(datalength/2)+'B',data)
                #obj.attitude['angx']=float(temp[0]/10.0)
                #obj.attitude['angy']=float(temp[1]/10.0)
                #obj.attitude['heading']=float(temp[2])
                #self.attitude['elapsed']=round(elapsed,3)
                #self.attitude['timestamp']="%0.2f" % (time.time(),)
                rec_obj.msp_attitude['angx'] = float(temp[0]/10.0)
                rec_obj.msp_attitude['angy'] = float(temp[1]/10.0)
                rec_obj.msp_attitude['heading'] = float(temp[2])
                #print(rec_obj.msp_attitude)
                #return self.attitude
            elif cmd == MultiWii.RC:           # checked
                temp = struct.unpack('<'+'h'*(datalength/2)+'B',data)
                rec_obj.rcChannels['roll']=temp[0]
                rec_obj.rcChannels['pitch']=temp[1]
                rec_obj.rcChannels['yaw']=temp[2]
                rec_obj.rcChannels['throttle']=temp[3]
                rec_obj.rcChannels['aux1'] = temp[4]
                rec_obj.rcChannels['aux2'] = temp[5]
                rec_obj.rcChannels['aux3'] = temp[6]
                rec_obj.rcChannels['aux4'] = temp[7]
                # to do aux
                rec_obj.rcChannels['elapsed']=round(elapsed,3)
                rec_obj.rcChannels['timestamp']="%0.2f" % (time.time(),)
                #return self.rcChannels
            elif cmd == MultiWii.RAW_IMU:       # checked
                temp = struct.unpack('<'+'h'*(datalength/2)+'B',data)
                rec_obj.rawIMU['ax']=float(temp[0])
                rec_obj.rawIMU['ay']=float(temp[1])
                rec_obj.rawIMU['az']=float(temp[2])
                rec_obj.rawIMU['gx']=float(temp[3])
                rec_obj.rawIMU['gy']=float(temp[4])
                rec_obj.rawIMU['gz']=float(temp[5])
                rec_obj.rawIMU['mx']=float(temp[6])
                rec_obj.rawIMU['my']=float(temp[7])
                rec_obj.rawIMU['mz']=float(temp[8])
                rec_obj.rawIMU['elapsed']=round(elapsed,3)
                rec_obj.rawIMU['timestamp']="%0.2f" % (time.time(),)
                #return self.rawIMU
            elif cmd == MultiWii.MOTOR:
                temp = struct.unpack('<'+'h'*(datalength/2)+'B',data)
                rec_obj.motor['m1']=float(temp[0])
                rec_obj.motor['m2']=float(temp[1])
                rec_obj.motor['m3']=float(temp[2])
                rec_obj.motor['m4']=float(temp[3])
                rec_obj.motor['elapsed']="%0.3f" % (elapsed,)
                rec_obj.motor['timestamp']="%0.2f" % (time.time(),)
                return self.motor
            elif cmd == MultiWii.STATUS:
                temp = struct.unpack('<3HI2B',data)
                rec_obj.msp_status['cycleTime'] = temp[0]
                rec_obj.msp_status['i2cError'] = temp[1]
                rec_obj.msp_status['activeSensors'] = temp[2]
                rec_obj.msp_status['flightModeFlags'] = temp[3]
                rec_obj.msp_status['profile'] = temp[4]
            elif cmd == MultiWii.MSP_STATUS_EX:       # checked
                temp = struct.unpack('<3HIB2HB',data)
                rec_obj.msp_status_ex['cycletime'] = temp[0]
                rec_obj.msp_status_ex['i2cError'] = temp[1]
                rec_obj.msp_status_ex['activeSensors'] = temp[2]
                rec_obj.msp_status_ex['flightModeFlags'] = temp[3]
                rec_obj.msp_status_ex['profile'] = temp[4]
                rec_obj.msp_status_ex['averageSystemLoadPercent'] = temp[5]
                rec_obj.msp_status_ex['armingFlags'] = temp[6]
                self.parseSensorStatus(rec_obj)
                self.parseFlightModeFlags(rec_obj)
                #print(rec_obj.msp_status_ex)

            elif cmd == MultiWii.MSP_SENSOR_STATUS:
                temp = struct.unpack('<9B',data)
                # to do

            elif cmd == MultiWii.MSP_LOOP_TIME:
                temp = struct.unpack('<HB',data)
                rec_obj.msp_loop_time['looptime'] = temp[0]

            elif cmd == MultiWii.API_VERSION:
                temp = struct.unpack('<4B',data)
                rec_obj.msp_api_version['msp_protocol_version'] = temp[0]
                rec_obj.msp_api_version['api_version_major'] = temp[1]
                rec_obj.msp_api_version['api_version_minor'] = temp[2]
            elif cmd == MultiWii.BOARD_INFO:
                temp = struct.unpack('<'+'b'*(datalength-3) + 'HB',data)
                rec_obj.msp_board_info['board_identifier'] = temp[0]
                rec_obj.msp_board_info['hardware_revision'] = temp[1]

            elif cmd == MultiWii.IDENT:
                temp = struct.unpack('<3BIB',data)
                rec_obj.msp_ident['version'] = temp[0]
                rec_obj.msp_ident['multitype'] = temp[1]
                rec_obj.msp_ident['msp_version'] = temp[2]
                rec_obj.msp_ident['capability'] = temp[3]

            elif cmd == MultiWii.MISC:
                temp = struct.unpack('<6HIH4B',data) # not right
                rec_obj.msp_misc['intPowerTrigger1'] = temp[0]
                rec_obj.msp_misc['maxthrottle'] = temp[2]
                rec_obj.msp_misc['mincommand'] = temp[3]
                # to do
            elif cmd == MultiWii.ALTITUDE:         # may not working
                temp = struct.unpack('<IHB',data)
                rec_obj.msp_altitude['estalt'] = temp[0]
                rec_obj.msp_altitude['vario'] = temp[1]

            elif cmd == MultiWii.RADIO:
                temp = struct.unpack('<2H6B',data)
                rec_obj.msp_radio['rxerrors'] = temp[0]
                rec_obj.msp_radio['fixed_errors'] = temp[1]
                rec_obj.msp_radio['localrssi'] = temp[2]
                rec_obj.msp_radio['remrssi'] = temp[3]
                rec_obj.msp_radio['txbuf'] = temp[4]
                rec_obj.msp_radio['noise'] = temp[5]
                rec_obj.msp_radio['remnoise'] = temp[6]

            elif cmd == MultiWii.MSP_SONAR_ALTITUDE: # checked
                temp = struct.unpack('<iB',data)
                rec_obj.msp_sonar_altitude['sonar_altitude'] = temp[0]

            elif cmd == MultiWii.ANALOG:          # checked, vbat:109
                temp = struct.unpack('<B3HB',data)
                rec_obj.msp_analog['vbat'] = temp[0]
                rec_obj.msp_analog['powermetersum'] = temp[1]
                rec_obj.msp_analog['rssi'] = temp[2]
                rec_obj.msp_analog['amps'] = temp[3]
                #print(rec_obj.msp_analog)
            elif cmd == MultiWii.MODE_RANGES:
                # not working,
                # because the data feedback should be '3c2B'+'80B'+'B',
                # longer than the permitted length of XBEE S2 AT ROUTER (84 Bytes).
                # So the data is separated to 2 frames.
                # But there are only two bytes (one byte for real range data, one byte for checksum) in the second frame,
                # so it does not worth to wait for another frame.
                #print(datalength)
                #print(len(data))
                temp = struct.unpack('<'+'B'*(len(data)),data)
                print(temp)
                # to do
            elif cmd == MultiWii.MSP_ADJUSTMENT_RANGES:
                pass
                # to do
            elif cmd == MultiWii.BOXIDS: # checked
                #print('right')
                #print(datalength)
                #print(len(data))
                temp = struct.unpack('<'+'B'*datalength + 'B',data)
                rec_obj.activeBoxes = list(temp)
                #print(temp)
                # to do
            elif cmd == MultiWii.RAW_GPS:
                temp = struct.unpack('<2B2I4H',data)
                # to do
            elif cmd == MultiWii.COMP_GPS:
                temp = struct.unpack('<2HB',data)
                # to do
            elif cmd == MultiWii.NAV_STATUS:
                temp = struct.unpack('<5BH',data)
                # to do
            elif cmd == MultiWii.GPSSVINFO:
                temp = struct.unpack('<5B',data)
                # to do
            elif cmd == MultiWii.GPSSTATISTICS:
                temp = struct.unpack('<H3I3H',data)
                # to do
            elif cmd == MultiWii.MSP_FEATURE:
                temp = struct.unpack('<I',data)
                # to do
            elif cmd == MultiWii.MSP_BOARD_ALIGNMENT:
                temp = struct.unpack('<3H',data)
                # to do
            elif cmd == MultiWii.MSP_RX_CONFIG:
                pass
                # to do
            elif cmd == MultiWii.MSP_FAILSAFE_CONFIG:
                pass
                # to do
            elif cmd == MultiWii.MSP_RXFAIL_CONFIG:
                pass
                # to do
            elif cmd == MultiWii.MSP_SENSOR_ALIGNMENT:
                temp = struct.unpack('<3B',data)
                # to do
            elif cmd == MultiWii.WP:
                temp = struct.unpack('<2B3i3h2B',data)
                rec_obj.tempMission = list(temp)
            else:
                return "No return error!"
        except (Exception, error):
            #print('Get Data Error')
            #print(Exception)
            #print error
            pass

    def requestDataLoose(self, data_length, send_code, send_data, obj, addr_long_list):
        frameid = obj.frame_id
        d_addr_long = obj.address_long
        d_addr = obj.address_short

        rec_data = ['','','']
        while True:
            self.sendCMDNew(data_length, send_code, send_data, obj)
            try:
                with time_limit(0.005):   # 0.005
                    if send_code == MultiWii.MODE_RANGES:
                        rec_data = self.readZBMsg(1)
                    else:
                        rec_data = self.readZBMsg(1)
            except:
                pass
            # to do: check src address, if not match the obj address, then discard
            validation = self.preCheckReadDataLoose(rec_data, send_code, send_data, addr_long_list)
            if validation == True:
                break
            else:
                pass
        return rec_data

    def preCheckReadDataLoose(self, rec_data_pack, send_code, send_data, addr_long_list):
        if len(rec_data_pack[2]) >= 5:
            header = rec_data_pack[2][0:3]
            if header == '$M>':
                pass
            else:
                return False

            #if (rec_data_pack[0][0:4] == '\x00\x13\xA2\x00'):
            if rec_data_pack[0] in addr_long_list:
                return True
            else:
                return False
        else:
            return False
