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

class QuadStates:
    def __init__(self):
        self.frame_id = ""
        self.address_long = ""
        self.address_short = ""

        self.msp_api_version = {'msp_protocol_version':0,'api_version_major':0,'api_version_minor':0}
        self.msp_fc_variant = {'fc_id':''}
        self.msp_fc_version = {'fc_version_major':0,'fc_version_minor':0,'fc_version_patch_level':0}
        self.msp_build_info = {'build_info':''}
        self.msp_board_info = {'board_identifier':'', 'hardware_revision':0, 'OSD_support':0, 'comm_capabilities':0, 'target_length':0, 'target_name':''}
        self.msp_ident = {'version':0, 'multitype':0, 'msp_version':0, 'capability':0}
        self.msp_feature = {'mask':0}
        self.msp_name = ""
        self.msp_activeboxes = []
        self.parsed_activeboxes = []
        self.msp_motor = {'1':0,'2':0,'3':0,'4':0,'5':0,'6':0,'7':0,'8':0}
        self.msp_3d = {'deadband3d_low':0, 'deadband3d_high':0, 'neutral3d':0}
        self.msp_rc = []
        self.msp_boxnames = []
        self.msp_boxids = []
        self.msp_mode_ranges = []
        self.msp_arming_config = {'auto_disarm_delay':0, 'disarm_kill_switch':0}

        self.msp_misc = {'mid_rc':0, 'min_throttle':0, 'max_throttle':0,
                         'min_command':0, 'failsafe_throttle':0,
                         'gps_provider':0, 'gps_baudrate':0, 'gps_sbas_mode':0,
                         'reserve1':0, 'rssi_channel':0, 'reserve2':0,
                         'mag_declination':0, 'voltage_scale':0,
                         'voltage_cell_min':0, 'voltage_cell_max':0,
                         'voltage_cell_warning':0}
        # {'intPowerTrigger1':0, 'conf_minthrottle':0, 'maxthrottle':0, 'mincommand':0, 'failsafe_throttle':0, 'plog_arm_counter':0, 'plog_lifetime':0, 'conf_mag_declination':0, 'conf_vbatscale':0, 'conf_vbatlevel_warn1':0, 'conf_vbatlevel_warn2':0, 'conf_vbatlevel_crit':0}

        self.sensor_flags = {'hardware':0, 'pitot':0, 'sonar':0, 'gps':0, 'mag':0, 'baro':0, 'acc':0}
        self.msp_calibration_data = {'accGetCalibrationAxisFlags':0, 'Acc X zero':0, 'Acc Y zero':0, 'Acc Z zero':0, 'Acc X gain':0, 'Acc Y gain':0, 'Acc Z gain':0, 'Mag X zero':0, 'Mag Y zero':0, 'Mag Z zero':0}
        self.msp_altitude = {'estalt':0, 'vario':0, 'baro':0}
        self.msp_sonar_altitude = {'sonar_altitude':0}
        self.msp_pid = []
        self.msp_pidnames = []
        self.msp_pid_controller = 2
        self.msp_inav_pid = {'async_mode':0, 'acc_task_frequency':0,
                             'attitude_task_frequency':0,
                             'heading_hold_rate_limit':0,
                             'heading_hold_error_lpf_freq':0,
                             'yaw_jump_prevention_limit':0,
                             'gyro_lpf':0, 'acc_soft_lpf_hz':0,
                             'reserve1':0, 'reserve2':0, 'reserve3':0, 'reserve4':0}
        self.msp_filter_config = {'gyro_soft_lpf_hz':0, 'dterm_lpf_hz':0,
                                  'yaw_lpf_hz':0,
                                  'gyro_soft_notch_hz_1':0,
                                  'gyro_soft_notch_cutoff_1':0,
                                  'dterm_soft_notch_hz':0,
                                  'dterm_soft_notch_cutoff':0,
                                  'gyro_soft_notch_hz_2':0,
                                  'gyro_soft_notch_cutoff_2':0 }
        self.msp_pid_advanced = {'roll_pitch_i_term_ignore_rate':0,
                                 'yaw_i_term_ignore_rate':0,
                                 'yaw_p_limit':0,
                                 'reserve1':0, 'reserve2':0, 'reserve3':0,
                                 'd_term_setpoint_weight':0,
                                 'pid_sum_limit':0,
                                 'reserve4':0,
                                 'axis_acceleration_limit_roll_pitch':0,
                                 'axis_acceleration_limit_yaw':0}
        self.msp_advanced_config = {'reserve1':0, 'reserve2':0, 'reserve3':0,
                                    'motor_pwm_protocol':0,
                                    'motor_pwm_rate':0,
                                    'servo_pwm_rate':0,
                                    'gyro_sync':0}
        self.msp_cf_serial_config = []
        self.msp_debug = []
        self.msp_rc_deadband = {'deadband':0, 'yaw_deadband':0, 'alt_hold_deadband':0, 'deadbanded_throttle':0}
        self.msp_board_alignment = {'roll_deci_degrees':0, 'pitch_deci_degrees':0, 'yaw_deci_degrees':0}
        self.msp_voltage_meter_config = {'scale':0, 'cell_min':0, 'cell_max':0, 'cell_warning':0}
        self.msp_current_meter_config = {'scale':0, 'offset':0, 'type':0, 'capabity_value':0}
        self.msp_adjustment_ranges = []
        self.msp_mixer = {'mixer_mode':0}
        self.msp_rx_config = {'serialrx_provider':0, 'max_check':0,
                              'mid_rc':0, 'min_check':0, 'spektrum_sat_bind':0,
                              'rx_min_usec':0, 'rx_max_usec':0,
                              'rc_interpolation':0,
                              'rc_interpolation_interval':0,
                              'air_mode_activate_threshold':0,
                              'rx_spi_protocol':0, 'rx_spi_id':0,
                              'rx_spi_rf_channel_count':0,
                              'fpv_cam_angle_degrees':0, 'receiver_type':0}
        self.msp_failsafe_config = {'failsafe_delay':0, 'failsafe_off_delay':0,
                                    'failsafe_throttle':0,
                                    'failsafe_kill_switch':0,
                                    'failsafe_throttle_low_delay':0,
                                    'failsafe_procedure':0,
                                    'failsafe_recovery_delay':0,
                                    'failsafe_fw_roll_angle':0,
                                    'failsafe_fw_pitch_angle':0,
                                    'failsafe_fw_yaw_rate':0,
                                    'failsafe_stick_motion_threshold':0,
                                    'failsafe_min_distance':0,
                                    'failsafe_min_distance_procedure':0}
        self.msp_rssi_config = {'rssi_channel':0}
        self.msp_sensor_config = {'acc':0, 'baro':0, 'mag':0, 'pitot':0, 'rangefinder':0, 'opflow':0}
        self.msp_sensor_alignment = {'gyro_align':0, 'acc_align':0, 'mag_align':0}
        self.msp_motor_pins = []
        self.msp_rx_map = []

        # GPS
        self.msp_raw_gps = {'gps_fix':0, 'gps_numsat':0, 'gps_lat':0, 'gps_lon':0, 'gps_altitude':0, 'gps_speed':0, 'gps_ground_course':0, 'gps_hdop':0}
        self.msp_comp_gps = {'range':0, 'direction':0, 'update':0}
        self.msp_gpssvinfo = {'gps_hdop':0}
        self.msp_gpsstatistics = {'gps_last_message_dt':0, 'gps_errors':0, 'gps_timeouts':0, 'gps_packet_count':0, 'gps_hdop':0, 'gps_eph':0, 'gps_epv':0}

        self.msp_attitude = {'angx':0, 'angy':0, 'heading':0}

        self.msp_wp = {'wp_no':0, 'action':0, 'lat':0, 'lon':0, 'altitude':0, 'p1':0, 'p2':0, 'p3':0, 'flag':0}

        self.msp_nav_status = {'nav_mode':0, 'nav_state':0, 'active_wp_action':0, 'active_wp_number':0, 'nav_error':0, 'heading_hold_target':0}  # 'target_bearing'

        self.msp_nav_config = {'flag1':0, 'flag2':0, 'wp_radius':0, 'safe_wp_distance':0, 'nav_max_altitude':0, 'nav_speed_max':0, 'nav_speed_min':0, 'crosstrack_gain':0, 'nav_bank_max':0, 'rth_altitude':0, 'land_speed':0, 'fence':0, 'max_wp_number':0}

        self.msp_radio = {'rxerrors':0, 'fixed_errors':0, 'localrssi':0, 'remrssi':0, 'txbuf':0, 'noise':0, 'remnoise':0}

        self.msp_rc_tuning = {'reserve1':0, 'stabilized_rc_expo':0, 'roll_rate':0, 'pitch_rate':0, 'yaw_rate':0, 'throttle_dyn_pid':0, 'throttle_rc_mid':0, 'throttle_rc_expo':0, 'throttle_pa_breakpoint':0, 'stabilized_rc_yaw_expo':0}

        self.msp_analog = {'vbat':0, 'powermetersum':0, 'rssi':0, 'amps':0}

        self.msp_nav_poshold = {'user_control_mode':0,
                                'max_auto_speed':0,
                                'max_auto_climb_rate':0,
                                'max_manual_speed':0,
                                'max_manual_climb_rate':0,
                                'mc_max_bank_angle':0,
                                'use_thr_mid_for_althold':0,
                                'mc_hover_throttle':0}

        self.msp_rth_and_land_config = {'min_rth_distance':0,
                                        'rth_climb_first':0,
                                        'rth_climb_ignore_emerg':0,
                                        'rth_tail_first':0,
                                        'rth_allow_landing':0,
                                        'rth_alt_control_mode':0,
                                        'rth_abort_threshold':0,
                                        'rth_altitude':0,
                                        'land_descent_rate':0,
                                        'land_slowdown_minalt':0,
                                        'land_slowdown_maxalt':0,
                                        'emerg_descent_rate':0}

        self.msp_position_estimation_config = {'w_z_baro_p':0,
                                               'w_z_gps_p':0,
                                               'w_z_gps_v':0,
                                               'w_xy_gps_p':0,
                                               'w_xy_gps_v':0,
                                               'gps_min_sats':0,
                                               'use_gps_velned':0}

        self.rcChannels = {'roll':0,'pitch':0,'yaw':0,'throttle':0,'aux1':0,'aux2':0,'aux3':0,'aux4':0,'elapsed':0,'timestamp':0}
        self.msp_raw_imu = {'ax':0,'ay':0,'az':0,'gx':0,'gy':0,'gz':0,'mx':0,'my':0,'mz':0,'elapsed':0,'timestamp':0}
        self.motor = {'m1':0,'m2':0,'m3':0,'m4':0,'elapsed':0,'timestamp':0}
        self.attitude = {'angx':0,'angy':0,'heading':0,'elapsed':0,'timestamp':0}
        self.message = {'angx':0,'angy':0,'heading':0,'roll':0,'pitch':0,'yaw':0,'throttle':0,'elapsed':0,'timestamp':0}
        self.msp_status = {'cycleTime':0,'i2cError':0,'activeSensors':0,'flightModeFlags':0,'profile':0}
        self.msp_status_ex = {'cycleTime':0, 'i2cError':0, 'activeSensors':0, 'flightModeFlags':0, 'profile':0, 'averageSystemLoadPercent':0, 'armingFlags':0, 'accGetCalibrationAxisFlags':0}
        self.parsed_activesensors = {'hardware_health':0, 'acc':0, 'baro':0, 'mag':0, 'gps':0, 'range':0, 'pitot':0, 'opflow':0}
        self.parsed_armingflags = {'OK_TO_ARM':0,
                                   'PREVENT_ARMING':0,
                                   'ARMED':0,
                                   'WAS_EVER_ARMED':0,
                                   'BLOCK_UAV_NOT_LEVEL':0,
                                   'BLOCK_SENSORS_CALIB':0,
                                   'BLOCK_SYSTEM_OVERLOAD':0,
                                   'BLOCK_NAV_SAFETY':0,
                                   'BLOCK_COMPASS_NOT_CALIB':0,
                                   'BLOCK_ACC_NOT_CALIB':0,
                                   'UNUSED':0,
                                   'BLOCK_HARDWARE_FAILURE':0}
        # msp_sensor_status, value can be 0, 1, 2, and 3.
        self.msp_sensor_status = {'hardware_health':0, 'gyro':0, 'acc':0, 'comp':0, 'baro':0, 'gps':0, 'range':0, 'pitot':0, 'optical':0}
        self.msp_loop_time = {'looptime':0}

        self.missionList = []
        self.tempMission = []
        self.downloadMissionList = []

        self.msp_xbee_self_telemetry_addr = 0
        self.msp_xbee_telemetry_source_addr = [0, 0, 0]
        self.msp_xbee_telemetry_destination_addr = [0, 0, 0]
        self.msp_xbee_self_rc_addr = 0
        self.msp_xbee_rc_source_addr = 0
        self.msp_formation_config = {'flight_height':200,
                                     'distance_gain':1, 'area_gain':1,
                                     'lat_gain':1000, 'lon_gain':1000,
                                     'graph_type':0, 'identity':0,
                                     'd_ji':100, 'd_ki':100, 'd_kj':100,
                                     'ad': 4330}

        self.msp_network_config = {'addressHigh': 0x0013A200,
                                   'selfTeleAddressLow': 0x00000000,
                                   'teleSource1AddressLow': 0x00000000,
                                   'teleSource2AddressLow': 0x00000000,
                                   'teleSource3AddressLow': 0x00000000,
                                   'teleDestination1AddressLow': 0x00000000,
                                   'teleDestination2AddressLow': 0x00000000,
                                   'teleDestination3AddressLow': 0x00000000,
                                   'selfRemoteAddressLow': 0x00000000,
                                   'remoteSourceAddressLow': 0x00000000 }
