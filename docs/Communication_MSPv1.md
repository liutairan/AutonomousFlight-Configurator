# Communication Protocol  
MSP-like request-send-receive communication.  
MSP: http://www.multiwii.com/wiki/index.php?title|Multiwii_Serial_Protocol  

Message frame structure:
`preamble`, `direction`, `size`, `command` , `data`, `crc`.

| Field | Note |
|:-----:|:----:|
| Preamble | $M |
| Direction | < or > |
| Size | Size of the data frame |
| Command | Frame id |
| Data | Data for each command |
| CRC | Checksum byte |

| Command | Frame ID | Direction | Data | Type | Note |
|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|
| MSP_PROTOCOL_VERSION | 0 | FC-> | VERSION || Not using. |
|||||||
| MSP_API_VERSION | 1 | FC-> | VERSION |   |   |
|||| MSP_PROTOCOL_VERSION | UINT8 ||
|||| API_VERSION_MAJOR | UINT8 ||
|||| API_VERSION_MINOR | UINT8 ||
|||||||
| MSP_FC_VARIANT | 2 |||||
|||| flightControllerIdentifier | 4*UINT8 ||
|||||||
| MSP_FC_VERSION | 3 |||||
|||| FC_VERSION_MAJOR | UINT8 ||
|||| FC_VERSION_MINOR | UINT8 ||
|||| FC_VERSION_PATCH_LEVEL | UINT8 ||
|||||||
| MSP_BOARD_INFO | 4 | FC-> | |||
|||||||
| MSP_BUILD_INFO | 5 | FC-> | |||
| MSP_INAV_PID | 6 |||||
| MSP_SET_INAV_PID | 7 | ->FC ||| Size: 15 |
|||| async_mode | UINT8 ||
|||| acc_task_frequency | UINT16 ||
|||| attitude_task_frequency | UINT16 ||
|||| heading_hold_rate_limit | UINT8 ||
|||| heading_hold_error_lpf_freq | UINT8 ||
|||| yaw_jump_prevention_limit | UINT16 ||
|||| gyro_lpf | UINT8 ||
|||| acc_soft_lpf_hz | UINT8 ||
||||| UINT8 ||
||||| UINT8 ||
||||| UINT8 ||
||||| UINT8 ||
|||||||
| MSP_NAME | 10 |||||
| MSP_SET_NAME | 11 |||| At most 16 bytes. |
|||| name | N*char ||
|||||||
| MSP_NAV_POSHOLD | 12 |||||
| MSP_SET_NAV_POSHOLD | 13 | ->FC ||| Size:13 |
|||| flags nav_user_control_mode | UINT8 ||
|||| max_auto_speed | UINT16 ||
|||| max_auto_climb_rate | UINT16 ||
|||| max_manual_speed | UINT16 ||
|||| max_manual_climb_rate | UINT16 ||
|||| max_bank_angle | UINT8 ||
|||| flags nav_use_midthr_for_althold | UINT8 ||
|||| nav_mc_hover_thr | UINT16 ||
|||||||
| MSP_CALIBRATION_DATA | 14 |||||
| MSP_SET_CALIBRATION_DATA | 15 | ->FC ||| Size: 18 |
|||| acczero_x | UINT16 ||
|||| acczero_y | UINT16 ||
|||| acczero_z | UINT16 ||
|||| accgain_x | UINT16 ||
|||| accgain_y | UINT16 ||
|||| accgain_z | UINT16 ||
|||| magzero_x | UINT16 ||
|||| magzero_y | UINT16 ||
|||| magzero_z | UINT16 ||
|||||||
| MSP_POSITION_ESTIMATION_CONFIG | 16 |||||
| MSP_SET_POSITION_ESTIMATION_CONFIG | 17 | ->FC ||| Size: 12 |
|||| inav_w_z_baro_p | UINT16 ||
|||| inav_w_z_gps_p | UINT16 ||
|||| inav_w_z_gps_v | UINT16 ||
|||| inav_w_xy_gps_p | UINT16 ||
|||| inav_w_xy_gps_v | UINT16 ||
|||| gps_min_sats | UINT8 ||
|||| inav_use_gps_velned | UINT8 ||
|||||||
|  MSP_WP_MISSION_LOAD | 18 |||| loadNonVolatileWaypointList |
||||| UINT8 ||
|||||||
|  MSP_WP_MISSION_SAVE | 19 |||| saveNonVolatileWaypointList |
||||| UINT8 ||
|||||||
|  MSP_WP_GETINFO | 20 |||||
|  MSP_RTH_AND_LAND_CONFIG | 21 |||||
|  MSP_SET_RTH_AND_LAND_CONFIG | 22 | ||| Size: 19 |
|||| nav_min_rth_distance | UINT16 ||
|||| flags nav_rth_climb_first | UINT8 ||
|||| flags nav_rth_climb_ignore_emerg | UINT8 ||
|||| flags nav_rth_tail_first | UINT8 ||
|||| flags nav_rth_allow_landing | UINT8 ||
|||| flags nav_rth_alt_control_mode | UINT8 ||
|||| nav_rth_abort_threshold | UINT16 ||
|||| rth_altitude | UINT16 ||
|||| land_descent_rate | UINT16 ||
|||| nav_land_slowdown_minalt | UINT16 ||
|||| nav_land_slowdown_maxalt | UINT16 ||
|||| emerg_descent_rate | UINT16 ||
|||||||
|  MSP_FW_CONFIG | 23 |||||
|  MSP_SET_FW_CONFIG | 24 |||||
|  MSP_MODE_RANGES | 34 | | | | MSP_MODE_RANGES, out message, returns all mode ranges |
|  MSP_SET_MODE_RANGE | 35 | ->FC ||| MSP_SET_MODE_RANGE in message, sets a single mode range |
|||| index | UINT8 ||
|||| mode id | UINT8 ||
|||| aux channel index | UINT8 ||
|||| start step | UINT8 ||
|||| end step | UINT8 ||
|||||||
|  MSP_FEATURE | 36 |||||
|  MSP_SET_FEATURE | 37 | ->FC |||  |
|||| feature set | UINT32 ||
|||||||
|  MSP_BOARD_ALIGNMENT | 38 |||||
|  MSP_SET_BOARD_ALIGNMENT | 39 | ||||
|||| roll_deci_degrees | UINT16 ||
|||| pitch_deci_degrees | UINT16 ||
|||| yaw_deci_degrees | UINT16 ||
|||||||
|  MSP_CURRENT_METER_CONFIG | 40 |||||
|  MSP_SET_CURRENT_METER_CONFIG | 41 | ->FC ||||
|||| current_scale | UINT16 ||
|||| current_offset | UINT16 ||
|||| current_type | UINT8 ||
|||| capacity_value | UINT16 ||
|||||||
|  MSP_MIXER | 42 |||||
|  MSP_SET_MIXER | 43 | ->FC ||||
|||| mixer_mode | UINT8 ||
|||||||
|  MSP_RX_CONFIG | 44 |||||
|  MSP_SET_RX_CONFIG | 45 |||||
|||| serialrx_provider | UINT8 ||
|||| max_check | UINT16 ||
|||| mid_rc | UINT16 ||
|||| min_check | UINT16 ||
|||| spektrum_sat_bind | UINT8 ||
|||| rx_min_usec | UINT16 ||
|||| rx_max_usec | UINT16 ||
||||| UINT8 ||
||||| UINT8 ||
||||| UINT16 ||
|||| rx_spi_protocol | UINT8 ||
|||| rx_spi_id | UINT32 ||
|||| rx_spi_rf_channel_count | UINT8 ||
||||| UINT8 ||
|||| receiver_type | UINT8 ||
|||||||
|  MSP_LED_COLORS | 46 |||||
|  MSP_SET_LED_COLORS | 47 |||||
|  MSP_RSSI_CONFIG | 50 |||||
|  MSP_SET_RSSI_CONFIG | 51 | ->FC ||||
|||| rssi_channel | UINT8 ||
|||||||
|  MSP_ADJUSTMENT_RANGES | 52 |||||
|  MSP_SET_ADJUSTMENT_RANGE | 53 | ->FC | |||
|||| index | UINT8 ||
|||| adjustment index | UINT8 ||
|||| aux channel index | UINT8 ||
|||| start step | UINT8 ||
|||| end step | UINT8 ||
|||| adjustment function | UINT8 ||
|||| aux switch channel index | UINT8 ||
|||||||
|  MSP_CF_SERIAL_CONFIG | 54 |||||
|  MSP_SET_CF_SERIAL_CONFIG | 55 |||||
|||| identifier | UINT8 ||
|||| function mask | UINT16 ||
|||| msp_baudrateIndex | UINT8 ||
|||| gps_baudrateIndex | UINT8 ||
|||| telemetry_baudrateIndex | UINT8 ||
|||| peripheral_baudrateIndex | UINT8 ||
|||||||
|  MSP_VOLTAGE_METER_CONFIG | 56 |||||
|  MSP_SET_VOLTAGE_METER_CONFIG | 57 |||||
|||| voltage_scale | UINT8 ||
|||| voltage_cell_min | UINT8 ||
|||| voltage_cell_max | UINT8 ||
|||| voltage_cell_warning | UINT8 ||
|||||||
|  MSP_SONAR_ALTITUDE | 58 | FC-> |||  SONAR cm |
|  MSP_PID_CONTROLLER | 59 |||||
|  MSP_SET_PID_CONTROLLER | 60 | ||| Not using. |
|||||||
|  MSP_ARMING_CONFIG | 61 ||||  out message         Returns auto_disarm_delay and disarm_kill_switch parameters |
|  MSP_SET_ARMING_CONFIG | 62 | ->FC | || in message, sets auto_disarm_delay and disarm_kill_switch parameters |
|||| auto_disarm_delay | UINT8 ||
|||| disarm_kill_switch | UINT8 ||
|||||||
|  MSP_RX_MAP | 64 |||||
|  MSP_SET_RX_MAP | 65 |||||
|||| rcmap | 4*UINT8 ||
|||||||
|  MSP_BF_CONFIG | 66 |||||
|  MSP_SET_BF_CONFIG | 67 |||||
|||| mixer_mode | UINT8 ||
|||| feature set | UINT32 ||
|||| serialrx_provider | UINT8 ||
|||| roll_deci_degrees | UINT16 ||
|||| pitch_deci_degrees | UINT16 ||
|||| yaw_deci_degrees | UINT16 ||
|||| current_scale | UINT16 ||
|||| current_offset | UINT16 ||
|||||||
|  MSP_REBOOT | 68 |||| in message, reboot settings |
|  MSP_DATAFLASH_SUMMARY | 70 |||| out message, get description of dataflash chip |
|  MSP_DATAFLASH_READ | 71 |||| out message, get content of dataflash chip |
|  MSP_DATAFLASH_ERASE | 72 | ->FC ||| in message, erase dataflash chip |
|||||||
|  MSP_LOOP_TIME | 73 | ->FC | looptime | UINT16 | out message, returns FC cycle time i.e looptime parameter |
|||||||
|  MSP_SET_LOOP_TIME | 74 |||| in message, sets FC cycle time i.e looptime parameter |
|  MSP_FAILSAFE_CONFIG | 75 |||| out message, returns FC Fail-Safe settings |
|  MSP_SET_FAILSAFE_CONFIG | 76 ||||in message, sets FC Fail-Safe settings |
|||| failsafe_delay | UINT8 ||
|||| failsafe_off_delay | UINT8 ||
|||| failsafe_throttle | UINT16 ||
|||| failsafe_kill_switch | UINT8 ||
|||| failsafe_throttle_low_delay | UINT16 ||
|||| failsafe_procedure | UINT8 ||
|||| failsafe_recovery_delay | UINT8 ||
|||| failsafe_fw_roll_angle | UINT16 ||
|||| failsafe_fw_pitch_angle | UINT16 ||
|||| failsafe_fw_yaw_rate | UINT16 ||
|||| failsafe_stick_motion_threshold | UINT16 ||
|||| failsafe_min_distance | UINT16 ||
|||| failsafe_min_distance_procedure | UINT8||
|||||||
|  MSP_RXFAIL_CONFIG | 77 |||| out message, returns RXFAIL settings |
|  MSP_SET_RXFAIL_CONFIG | 78 |||| in message, sets RXFAIL settings |
|  MSP_SDCARD_SUMMARY | 79 |||| out message, get the state of the SD card |
|  MSP_BLACKBOX_CONFIG | 80 |||| out message, get blackbox settings |
|  MSP_SET_BLACKBOX_CONFIG | 81 | ->FC ||| in message, set blackbox settings |
|||| device | UINT8 ||
|||| rate_num | UINT8 ||
|||| rate_denom | UINT8 ||
|||||||
|  MSP_TRANSPONDER_CONFIG | 82 |||| out message, get transponder settings |
|  MSP_SET_TRANSPONDER_CONFIG | 83 |||| in message, set transponder settings |
|  MSP_OSD_CONFIG | 84 |||| out message, get osd settings - betaflight |
|  MSP_SET_OSD_CONFIG | 85 |||| in message, set osd settings - betaflight |
|  MSP_OSD_CHAR_READ | 86 |||| out message, get osd settings - betaflight |
|  MSP_OSD_CHAR_WRITE | 87 |||| in message, set osd settings - betaflight |
|  MSP_VTX_CONFIG | 88 |||| out message, get vtx settings - betaflight |
|  MSP_SET_VTX_CONFIG | 89 |||| in message          Set vtx settings - betaflight |
|  MSP_ADVANCED_CONFIG | 90 |||| Betaflight Additional Commands |
|  MSP_SET_ADVANCED_CONFIG | 91 | ->FC ||| Betaflight Additional Commands |
|||| | UINT8 | Not using. |
|||| | UINT8 | Not using. |
|||| | UINT8 | Not using. |
|||| motor pwm protocol | UINT8 ||
|||| motor pwm rate | UINT16 ||
|||| servo pwm rate | UINT16 ||
|||| gyro sync | UINT8 ||
|||||||
|  MSP_FILTER_CONFIG | 92 | FC-> ||||
|||||||
|  MSP_SET_FILTER_CONFIG | 93 | ->FC ||||
|||| gyro_soft_lpf_hz | UINT8 ||
|||| dterm_lpf_hz | UINT16 ||
|||| yaw_lpf_hz | UINT16 ||
|||| gyro_soft_notch_hz_1 | UINT16 ||
|||| gyro_soft_notch_cutoff_1 | UINT16 ||
|||| dterm_soft_notch_hz | UINT16 ||
|||| dterm_soft_notch_cutoff | UINT16 ||
|||| gyro_soft_notch_hz_2 | UINT16 ||
|||| gyro_soft_notch_cutoff_2 | UINT16 ||
|||||||
|  MSP_PID_ADVANCED | 94 |||||
|||||||
|  MSP_SET_PID_ADVANCED | 95 | ||| Size: 17 |
|||| roll pitch item ignore rate | UINT16 ||
|||| yaw item ignore rate | UINT16 ||
|||| yaw p limit | UINT16 ||
|||| delta method | UINT8 ||
|||| vbat pid compensation | UINT8 ||
|||| setpoint relax ratio | UINT8 ||
|||| dterm_setpoint_weight | UINT8 ||
|||| pid_sum_limit | UINT16 ||
|||| iterm throttle gain | UINT8 ||
|||| axis acceleration limit roll pitch | UINT16 ||
|||| axis acceleration limit yaw | UINT16 ||
|||||||
|  MSP_SENSOR_CONFIG | 96 |||||
|  MSP_SET_SENSOR_CONFIG | 97 | ->FC ||| Size 6|
|||| acc_hardware | UINT8 ||
|||| baro_hardware | UINT8 ||
|||| mag_hardware | UINT8 ||
|||| pitot_hardware | UINT8 ||
|||| rangefinder_hardware | UINT8 ||
|||| opflow_hardware | UINT8 ||
|||||||
|  MSP_SPECIAL_PARAMETERS | 98 |||| Temporary betaflight parameters before cleanup and keep CF compatibility |
|  MSP_SET_SPECIAL_PARAMETERS | 99 |||| Temporary betaflight parameters before cleanup and keep CF compatibility |
|||||||
|  MSP_IDENT | 100 | FC-> | VERSION || DEPRECATED - Use MSP_API_VERSION |
|||| MW_VERSION | UINT8 ||
|||| mixer_mode | UINT8 ||
|||| MSP_PROTOCOL_VERSION | UINT8 ||
|||| capability | UINT32 ||
|||||||
|  MSP_STATUS | 101 | FC-> ||||
|||| cycleTime | UINT16 | unit: microseconds |
|||| i2cGetErrorCounter | UINT16 ||
|||| packSensorStatus | UINT16 ||
|||| mspBoxModeFlags | UINT32 ||
|||| getConfigProfile | UINT8 | to indicate the current configuration setting |
|||||||
|  MSP_RAW_IMU | 102|||| unit: it depends on ACC sensor and is based on ACC_1G definition |
|||| acc | 3*INT16 | MMA7455 64 / MMA8451Q 512 / ADXL345 265 / BMA180 255 / BMA020 63 / NUNCHUCK 200 / LIS3LV02 256 / LSM303DLx_ACC 256 / MPU6050 512 / LSM330 256 |
|||| gyro | 3*INT16 | unit: it depends on GYRO sensor. For MPU6050, 1 unit = 1/4.096 deg/s |
|||| mag | 3*INT16 | unit: it depends on MAG sensor. |
|||||||
|  MSP_SERVO | 103|||| Range [1000;2000]. The servo order depends on multi type. |
|  MSP_MOTOR | 104|||| Range [1000;2000]. The motor order depends on multi type. |
|  MSP_RC | 105|||||
|  MSP_RAW_GPS | 106 | RC-> ||||
|||| gps_fixType | UINT8 ||
|||| gps_numSat | UINT8 ||
|||| gps_llh_lat | UINT32 | 1 / 10 000 000 deg |
|||| gps_llh_lon | UINT32 | 1 / 10 000 000 deg |
|||| gps_llh_alt | UINT16 | meter |
|||| gps_groundSpeed | UINT16 | cm/s |
|||| gps_groundCourse | UINT16 | unit: degree*10 |
|||| gps_hdop | UINT16 ||
|||||||
|  MSP_COMP_GPS | 107 |||||
|||| gps_distanceToHome | UINT16 | unit: meter |
|||| gps_directionToHome | UINT16 | unit: degree (range [-180;+180]) |
|||| gps_flags_gpsHeartbeat | UINT16 | a flag to indicate when a new GPS frame is received (the GPS fix is not dependent of this) |
|||||||
|  MSP_ATTITUDE | 108|||||
|  MSP_ALTITUDE | 109|||||
|||| getEstimatedActualPosition | INT32 | cm |
|||| getEstimatedActualVelocity | INT16 | cm/s |
|||| baroGetLatestAltitude | INT32 | cm |
|||||||
|  MSP_ANALOG | 110|||||
|  MSP_RC_TUNING | 111|||||
|  MSP_PID | 112|||||
|  MSP_ACTIVEBOXES | 113|||||
|||| mspBoxModeFlags | UINT32 ||
|||||||
|  MSP_MISC | 114|||||
|  MSP_MOTOR_PINS | 115|||||
|  MSP_BOXNAMES | 116 |||| String of BOX items |
|  MSP_PIDNAMES | 117 |||| String of PID items |
|  MSP_WP | 118|||||
|  MSP_BOXIDS | 119|||||
|  MSP_SERVO_CONFIGURATIONS | 120|||||
|  MSP_NAV_STATUS | 121|||||
|  MSP_NAV_CONFIG | 122|||||
|  MSP_3D | 124|||||
|  MSP_RC_DEADBAND | 125|||||
|  MSP_SENSOR_ALIGNMENT | 126|||||
|  MSP_LED_STRIP_MODECOLOR | 127 |||||
| MSP_REF_ALTITUDE | 130 |||||
|||||||
| MSP_REF_DISTANCE | 131 |||||
|||||||
| MSP_TOPOLOGY | 132 |||||
|||||||
| MSP_SRC_ADDR | 133 |||||
|||||||
| MSP_DEST_ADDR | 134 |||||
|||||||
|  MSP_STATUS_EX | 150    |||| out message         cycletime, errors_count, CPU load, sensor present etc |
|||| cycleTime | UINT16 ||
|||| i2cGetErrorCounter | UINT16 ||
|||| packSensorStatus | UINT16 ||
|||| mspBoxModeFlags | UINT32 ||
|||| getConfigProfile | UINT8 ||
|||| averageSystemLoadPercent | UINT16 ||
|||| armingFlags | UINT16 ||
|||| accGetCalibrationAxisFlags | UINT8 ||
|||||||
|  MSP_SENSOR_STATUS | 151    |||| out message         Hardware sensor status |
|  MSP_UID | 160    |||| out message         Unique device ID |
|  MSP_GPSSVINFO | 164 |||||
|  MSP_GPSSTATISTICS | 166 |||||
|  MSP_OSD_VIDEO_CONFIG | 180 |||| OSD specific |
|  MSP_SET_OSD_VIDEO_CONFIG | 181 |||| OSD specific |
|  MSP_DISPLAYPORT | 182 |||||
|  MSP_SET_TX_INFO | 186 |||| in message, used to send runtime information from TX lua scripts to the firmware |
|||| rssi | UINT8 ||
|||||||
|  MSP_TX_INFO | 187 |||| out message, used by TX lua scripts to read information from the firmware |
|  MSP_SET_RAW_RC | 200 | ->FC | RC data from each channel | N*UINT16 | Range [1000;2000], ROLL/PITCH/YAW/THROTTLE/CH5/CH6/..., at most 18 channels. |
|  MSP_SET_RAW_GPS | 201  | ->FC ||| in message, fix, numsat, lat, lon, alt, speed. This request is used to inject GPS data (annex GPS device or simulation purpose) |
|||| gps_fix | UINT8 ||
|||| numsat | UINT8 ||
|||| llh_lat | UINT32 ||
|||| llh_lon | UINT32 ||
|||| llh_alt | UINT16 ||
|||| ground_speed | UINT16 ||
|||||||
|  MSP_SET_PID | 202 | ->FC | All PID gains | 10 x 3 x UINT8 | PID gains, totally 10 sets of PIDs. |
|  MSP_SET_BOX | 203|||||
|  MSP_SET_RC_TUNING | 204 | ->FC ||||
|||| rcRate8 | UINT8 ||
|||| rcExpo8 | UINT8 ||
|||| roll rates | UINT8 ||
|||| pitch rates | UINT8 ||
|||| yaw rates | UINT8 ||
|||| throttle dynPID | UINT8 ||
|||| throttle rcMid8 | UINT8 ||
|||| throttle rcExpo8 | UINT8 ||
|||| throttle pa_breakpoint | UINT16 ||
|||| stablized rcYawExpo8 | UINT8 | Optional |
|||||||
|  MSP_ACC_CALIBRATION | 205 |||| If not armed, then start acc calibration process. |
|||||||
|  MSP_MAG_CALIBRATION | 206 |||| If not armed, then start mag calibration process. |
|||||||
|  MSP_SET_MISC | 207 | ->FC | || Size 22 |
|||| mid rc | UINT16 ||
|||| min throttle | UINT16 ||
|||| max throttle | UINT16 ||
|||| min command  | UINT16 ||
|||| failsafe throttle | UINT16 ||
|||| gps provider | UINT8 ||
|||| gps baudrate | UINT8 ||
|||| gps sbas mode | UINT8 ||
|||| multiwii current meter output | UINT8 ||
|||| rssi channel | UINT8 ||
||||  | UINT8 | Not using |
|||| mag declination | UINT16 ||
|||| voltage scale | UINT8 ||
|||| voltage cell min | UINT8 ||
|||| voltage cell max | UINT8 ||
|||| voltage cell warning | UINT8 ||
|||||||
|  MSP_RESET_CONF | 208 | ->FC ||| Reset configuration |
|||||||
|  MSP_SET_WP | 209 | ->FC ||| Set waypoint, size: 21. |
|||| msp_wp_no | UINT8 ||
|||| action | UINT8 ||
|||| lat | UINT32 ||
|||| lon | UINT32 ||
|||| alt | UINT32 | altitude (cm) |
|||| p1 | UINT16 ||
|||| p2 | UINT16 ||
|||| p3 | UINT16 ||
|||| flag | UINT8 ||
|||||||
|  MSP_SELECT_SETTING | 210 | ->FC | profile choice | UINT8 | select the setting configuration (can set for instance different pid and rate). Range: 0, 1 or 2 |
|  MSP_SET_HEAD | 211 | ->FC | Heading hold target | INT16 | Set a new head lock reference. Range [-180;+180] |
|  MSP_SET_SERVO_CONFIGURATION | 212|||||
|  MSP_SET_MOTOR | 214 | ->FC || 8*UINT16 | Use to set individual motor value (to be used only with DYNBALANCE config) |
|  MSP_SET_NAV_CONFIG | 215|||||
|  MSP_SET_3D | 217|||||
|  MSP_SET_RC_DEADBAND | 218 | ->FC | || Size 5|
|||| deadband | UINT8 ||
|||| yaw_deadband | UINT8 ||
|||| alt_hold_deadband | UINT8 ||
|||| deadband3d_throttle | UINT16 ||
|||||||
|  MSP_SET_RESET_CURR_PID | 219 |||| Reset pid profile |
|  MSP_SET_SENSOR_ALIGNMENT | 220 |||||
|||| gyro_align | UINT8 ||
|||| acc_align | UINT8 ||
|||| mag_align | UINT8||
|||||||
|  MSP_SET_LED_STRIP_MODECOLOR | 221 | ||||
|||||||
| MSP_SET_REF_ALTITUDE | 230 |||| Set reference altitude|
||||reference altitude | UINT16 | Unit: cm. |
|||||||
| MSP_SET_REF_DISTANCE | 231 |||| Set desired distance to other agents, currently allows at most 2. If there is only one, then set the second to zero. |
|||| d1 | UINT16 ||
|||| d2 | UINT16 ||
|||||||
| MSP_SET_TOPOLOGY | 232 |||| Set the connection topology of the communication graph. |
|||||||
| MSP_SET_SRC_ADDR | 233 |||| Set the address of source, data comes from these sources. Allows at most 2 sources. |
|||| s1 | UINT32 ||
|||| s2 | UINT32||
|||||||
| MSP_SET_DEST_ADDR | 234 |||| Set the address of destination, data goes to these destinations. Allows at most 2 destinations. |
|||| d1 | UINT32 |  |
|||| d2 | UINT32 |  |
|||||||
|  MSP_ACC_TRIM | 240 |||| out message         get acc angle trim values
|  MSP_SET_ACC_TRIM | 239    |||| in message          set acc angle trim values |
|  MSP_SERVO_MIX_RULES | 241    |||| out message, returns servo mixer configuration |
|  MSP_SET_SERVO_MIX_RULE | 242 |||| in message, sets servo mixer configuration |
|  MSP_SET_4WAY_IF | 245 |||| in message, sets 4way interface |
|  MSP_RTC | 246 |  ||||
|  MSP_SET_RTC | 247 |  ||||
|||| secs | UINT32 ||
|||| millis | UINT16 ||
|||||||
|  MSP_EEPROM_WRITE | 250 | ->FC ||| If not armed, then write EEPROM. |
|  MSP_RESERVE_1 | 251 |||||
|  MSP_RESERVE_2 | 252 |||||
|  MSP_DEBUGMSG | 253 |||||
|  MSP_DEBUG | 254 |||||
|  MSP_V2_FRAME | 255 |||||
|||||||
|||||| END OF TABLE |
