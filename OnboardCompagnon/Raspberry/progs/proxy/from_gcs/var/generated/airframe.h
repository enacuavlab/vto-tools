/* This file has been generated from /home/pprz/Projects/paparazzi/conf/airframes/ENAC/quadrotor/hoops_110.xml */
/* Version v5.13_devel-none-ga6fec87d6-dirty */
/* Please DO NOT EDIT */

#ifndef AIRFRAME_H
#define AIRFRAME_H

#define AIRFRAME_NAME "HOOPS_110"
#define AC_ID 110
#define MD5SUM ((uint8_t*)"\135\204\207\144\027\306\163\311\015\001\374\051\267\277\254\112")

#define SERVOS_PWM_NB 4
#include "subsystems/actuators/actuators_pwm.h"

#define SERVO_FL 0
#define SERVO_FL_NEUTRAL 1200
#define SERVO_FL_TRAVEL_UP 0.0833333333333
#define SERVO_FL_TRAVEL_UP_NUM 1
#define SERVO_FL_TRAVEL_UP_DEN 12
#define SERVO_FL_TRAVEL_DOWN 0.0208333333333
#define SERVO_FL_TRAVEL_DOWN_NUM 1
#define SERVO_FL_TRAVEL_DOWN_DEN 48
#define SERVO_FL_MAX 2000
#define SERVO_FL_MIN 1000

#define SERVO_FR 1
#define SERVO_FR_NEUTRAL 1200
#define SERVO_FR_TRAVEL_UP 0.0833333333333
#define SERVO_FR_TRAVEL_UP_NUM 1
#define SERVO_FR_TRAVEL_UP_DEN 12
#define SERVO_FR_TRAVEL_DOWN 0.0208333333333
#define SERVO_FR_TRAVEL_DOWN_NUM 1
#define SERVO_FR_TRAVEL_DOWN_DEN 48
#define SERVO_FR_MAX 2000
#define SERVO_FR_MIN 1000

#define SERVO_BR 2
#define SERVO_BR_NEUTRAL 1200
#define SERVO_BR_TRAVEL_UP 0.0833333333333
#define SERVO_BR_TRAVEL_UP_NUM 1
#define SERVO_BR_TRAVEL_UP_DEN 12
#define SERVO_BR_TRAVEL_DOWN 0.0208333333333
#define SERVO_BR_TRAVEL_DOWN_NUM 1
#define SERVO_BR_TRAVEL_DOWN_DEN 48
#define SERVO_BR_MAX 2000
#define SERVO_BR_MIN 1000

#define SERVO_BL 3
#define SERVO_BL_NEUTRAL 1200
#define SERVO_BL_TRAVEL_UP 0.0833333333333
#define SERVO_BL_TRAVEL_UP_NUM 1
#define SERVO_BL_TRAVEL_UP_DEN 12
#define SERVO_BL_TRAVEL_DOWN 0.0208333333333
#define SERVO_BL_TRAVEL_DOWN_NUM 1
#define SERVO_BL_TRAVEL_DOWN_DEN 48
#define SERVO_BL_MAX 2000
#define SERVO_BL_MIN 1000

static inline int get_servo_min_PWM(int _idx) {
  switch (_idx) {
    case SERVO_FL: return SERVO_FL_MIN;
    case SERVO_FR: return SERVO_FR_MIN;
    case SERVO_BR: return SERVO_BR_MIN;
    case SERVO_BL: return SERVO_BL_MIN;
    default: return 0;
  };
}

static inline int get_servo_max_PWM(int _idx) {
  switch (_idx) {
    case SERVO_FL: return SERVO_FL_MAX;
    case SERVO_FR: return SERVO_FR_MAX;
    case SERVO_BR: return SERVO_BR_MAX;
    case SERVO_BL: return SERVO_BL_MAX;
    default: return 0;
  };
}


#define COMMAND_ROLL 0
#define COMMAND_PITCH 1
#define COMMAND_YAW 2
#define COMMAND_THRUST 3
#define COMMANDS_NB 4
#define COMMANDS_FAILSAFE {0,0,0,0}


#define SECTION_MIXING 1
#define MOTOR_MIXING_TYPE QUAD_X

#define SERVO_BL_IDX 3
#define Set_BL_Servo(_v) { \
  actuators[SERVO_BL_IDX] = Chop(_v, SERVO_BL_MIN, SERVO_BL_MAX); \
  ActuatorPwmSet(SERVO_BL, actuators[SERVO_BL_IDX]); \
}

#define SERVO_FL_IDX 0
#define Set_FL_Servo(_v) { \
  actuators[SERVO_FL_IDX] = Chop(_v, SERVO_FL_MIN, SERVO_FL_MAX); \
  ActuatorPwmSet(SERVO_FL, actuators[SERVO_FL_IDX]); \
}

#define SERVO_BR_IDX 2
#define Set_BR_Servo(_v) { \
  actuators[SERVO_BR_IDX] = Chop(_v, SERVO_BR_MIN, SERVO_BR_MAX); \
  ActuatorPwmSet(SERVO_BR, actuators[SERVO_BR_IDX]); \
}

#define SERVO_FR_IDX 1
#define Set_FR_Servo(_v) { \
  actuators[SERVO_FR_IDX] = Chop(_v, SERVO_FR_MIN, SERVO_FR_MAX); \
  ActuatorPwmSet(SERVO_FR, actuators[SERVO_FR_IDX]); \
}

#define ACTUATORS_NB 4

#define AllActuatorsInit() { \
  ActuatorsPwmInit();\
}

#define AllActuatorsCommit() { \
  ActuatorsPwmCommit();\
}

#define SetActuatorsFromCommands(values, AP_MODE) { \
  int32_t servo_value;\
  int32_t command_value;\
\
  motor_mixing_run(autopilot_get_motors_on(),FALSE,values); \
\
  command_value = motor_mixing.commands[MOTOR_FRONT_LEFT]; \
  command_value *= command_value>0 ? SERVO_FL_TRAVEL_UP_NUM : SERVO_FL_TRAVEL_DOWN_NUM; \
  command_value /= command_value>0 ? SERVO_FL_TRAVEL_UP_DEN : SERVO_FL_TRAVEL_DOWN_DEN; \
  servo_value = SERVO_FL_NEUTRAL + command_value; \
  Set_FL_Servo(servo_value); \
\
  command_value = motor_mixing.commands[MOTOR_FRONT_RIGHT]; \
  command_value *= command_value>0 ? SERVO_FR_TRAVEL_UP_NUM : SERVO_FR_TRAVEL_DOWN_NUM; \
  command_value /= command_value>0 ? SERVO_FR_TRAVEL_UP_DEN : SERVO_FR_TRAVEL_DOWN_DEN; \
  servo_value = SERVO_FR_NEUTRAL + command_value; \
  Set_FR_Servo(servo_value); \
\
  command_value = motor_mixing.commands[MOTOR_BACK_RIGHT]; \
  command_value *= command_value>0 ? SERVO_BR_TRAVEL_UP_NUM : SERVO_BR_TRAVEL_DOWN_NUM; \
  command_value /= command_value>0 ? SERVO_BR_TRAVEL_UP_DEN : SERVO_BR_TRAVEL_DOWN_DEN; \
  servo_value = SERVO_BR_NEUTRAL + command_value; \
  Set_BR_Servo(servo_value); \
\
  command_value = motor_mixing.commands[MOTOR_BACK_LEFT]; \
  command_value *= command_value>0 ? SERVO_BL_TRAVEL_UP_NUM : SERVO_BL_TRAVEL_DOWN_NUM; \
  command_value /= command_value>0 ? SERVO_BL_TRAVEL_UP_DEN : SERVO_BL_TRAVEL_DOWN_DEN; \
  servo_value = SERVO_BL_NEUTRAL + command_value; \
  Set_BL_Servo(servo_value); \
\
  AllActuatorsCommit(); \
}

#define SECTION_IMU 1
#define IMU_GYRO_P_SIGN -1
#define IMU_GYRO_Q_SIGN 1
#define IMU_GYRO_R_SIGN -1
#define IMU_ACCEL_X_SIGN -1
#define IMU_ACCEL_Y_SIGN 1
#define IMU_ACCEL_Z_SIGN -1
#define IMU_ACCEL_X_NEUTRAL -57
#define IMU_ACCEL_Y_NEUTRAL -4
#define IMU_ACCEL_Z_NEUTRAL -192
#define IMU_ACCEL_X_SENS 2.46154229935
#define IMU_ACCEL_X_SENS_NUM 49349
#define IMU_ACCEL_X_SENS_DEN 20048
#define IMU_ACCEL_Y_SENS 2.43602916679
#define IMU_ACCEL_Y_SENS_NUM 14699
#define IMU_ACCEL_Y_SENS_DEN 6034
#define IMU_ACCEL_Z_SENS 2.46158796549
#define IMU_ACCEL_Z_SENS_NUM 30600
#define IMU_ACCEL_Z_SENS_DEN 12431

#define SECTION_AHRS 1
#define AHRS_HEADING_UPDATE_GPS_MIN_SPEED 0
#define AHRS_USE_GPS_HEADING TRUE

#define SECTION_STABILIZATION_ATTITUDE 1
#define STABILIZATION_ATTITUDE_SP_MAX_PHI 0.7853981625
#define STABILIZATION_ATTITUDE_SP_MAX_THETA 0.7853981625
#define STABILIZATION_ATTITUDE_SP_MAX_R 3.4906585
#define STABILIZATION_ATTITUDE_DEADBAND_A 0
#define STABILIZATION_ATTITUDE_DEADBAND_E 0
#define STABILIZATION_ATTITUDE_DEADBAND_R 250
#define STABILIZATION_ATTITUDE_REF_OMEGA_P 6.981317
#define STABILIZATION_ATTITUDE_REF_ZETA_P 0.85
#define STABILIZATION_ATTITUDE_REF_MAX_P 6.981317
#define STABILIZATION_ATTITUDE_REF_MAX_PDOT RadOfDeg(8000.)
#define STABILIZATION_ATTITUDE_REF_OMEGA_Q 6.981317
#define STABILIZATION_ATTITUDE_REF_ZETA_Q 0.85
#define STABILIZATION_ATTITUDE_REF_MAX_Q 6.981317
#define STABILIZATION_ATTITUDE_REF_MAX_QDOT RadOfDeg(8000.)
#define STABILIZATION_ATTITUDE_REF_OMEGA_R 4.363323125
#define STABILIZATION_ATTITUDE_REF_ZETA_R 0.85
#define STABILIZATION_ATTITUDE_REF_MAX_R 4.363323125
#define STABILIZATION_ATTITUDE_REF_MAX_RDOT RadOfDeg(1800.)
#define STABILIZATION_ATTITUDE_PHI_PGAIN 500
#define STABILIZATION_ATTITUDE_PHI_DGAIN 260
#define STABILIZATION_ATTITUDE_PHI_IGAIN 100
#define STABILIZATION_ATTITUDE_THETA_PGAIN 500
#define STABILIZATION_ATTITUDE_THETA_DGAIN 260
#define STABILIZATION_ATTITUDE_THETA_IGAIN 100
#define STABILIZATION_ATTITUDE_PSI_PGAIN 1279
#define STABILIZATION_ATTITUDE_PSI_DGAIN 802
#define STABILIZATION_ATTITUDE_PSI_IGAIN 31
#define STABILIZATION_ATTITUDE_PHI_DDGAIN 300
#define STABILIZATION_ATTITUDE_THETA_DDGAIN 300
#define STABILIZATION_ATTITUDE_PSI_DDGAIN 300

#define SECTION_GUIDANCE_V 1
#define GUIDANCE_V_HOVER_KP 150
#define GUIDANCE_V_HOVER_KD 80
#define GUIDANCE_V_HOVER_KI 20
#define GUIDANCE_V_NOMINAL_HOVER_THROTTLE 0.45
#define GUIDANCE_V_ADAPT_THROTTLE_ENABLED FALSE

#define SECTION_GUIDANCE_H 1
#define GUIDANCE_H_PGAIN 136
#define GUIDANCE_H_DGAIN 146
#define GUIDANCE_H_IGAIN 30

#define SECTION_SIMULATOR 1
#define NPS_ACTUATOR_NAMES { "nw_motor" , "ne_motor" , "se_motor" , "sw_motor" }
#define NPS_JSBSIM_MODEL "HOOPERFLY/hooperfly_teensyfly_quad"
#define NPS_SENSORS_PARAMS "nps_sensors_params_default.h"
#define NPS_JS_AXIS_MODE 4

#define SECTION_AUTOPILOT 1
#define MODE_STARTUP AP_MODE_NAV
#define MODE_MANUAL AP_MODE_ATTITUDE_DIRECT
#define MODE_AUTO1 AP_MODE_HOVER_Z_HOLD
#define MODE_AUTO2 AP_MODE_NAV

#define SECTION_BAT 1
#define CATASTROPHIC_BAT_LEVEL 10.5

#define SECTION_GCS 1
#define ALT_SHIFT_PLUS_PLUS 5
#define ALT_SHIFT_PLUS 1
#define ALT_SHIFT_MINUS -1


#endif // AIRFRAME_H
