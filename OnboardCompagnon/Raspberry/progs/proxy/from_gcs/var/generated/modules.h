/* This file has been generated from /home/pprz/Projects/paparazzi/conf/airframes/ENAC/quadrotor/hoops_110.xml */
/* Version v5.13_devel-none-ga6fec87d6-dirty */
/* Please DO NOT EDIT */

#ifndef MODULES_H
#define MODULES_H

#define MODULES_IDLE  0
#define MODULES_RUN   1
#define MODULES_START 2
#define MODULES_STOP  3

#define MODULES_FREQUENCY 512

#ifdef MODULES_C
#define EXTERN_MODULES
#else
#define EXTERN_MODULES extern
#endif
#include "std.h"
#include "ctrl/object_tracking.h"
#include "sensors/cameras/jevois.h"
#include "stabilization/stabilization_attitude.h"
#include "stabilization/stabilization_attitude_quat_int.h"
#include "firmwares/rotorcraft/stabilization.h"
#include "stabilization/stabilization_none.h"
#include "firmwares/rotorcraft/navigation.h"
#include "guidance/guidance_h.h"
#include "guidance/guidance_v.h"
#include "subsystems/ins/ins_gps_passthrough.h"
#include "subsystems/ahrs.h"
#include "boards/apogee/imu_apogee.h"
#include "boards/apogee/imu_apogee.h"
#include "subsystems/imu.h"
#include "subsystems/radio_control/rc_datalink.h"
#include "subsystems/actuators/motor_mixing.h"
#include "subsystems/gps.h"
#include "subsystems/gps.h"
#include "subsystems/actuators/actuators_pwm.h"
#include "datalink/pprz_dl.h"

#define IMU_APOGEE_PERIODIC_PERIOD 0.001953
#define IMU_APOGEE_PERIODIC_FREQ 512.000000
#define GPS_DATALINK_PERIODIC_CHECK_PERIOD 1.000000
#define GPS_DATALINK_PERIODIC_CHECK_FREQ 1.000000

EXTERN_MODULES uint8_t gps_datalink_gps_datalink_periodic_check_status;


static inline void modules_datalink_init(void) {
  pprz_dl_init();
}

static inline void modules_default_init(void) {
  gps_init();
  gps_datalink_init();
  gps_datalink_gps_datalink_periodic_check_status = MODULES_START;
  imu_init();
  imu_apogee_init();
  ins_gps_passthrough_init();
  guidance_h_init();
  guidance_v_init();
  nav_init();
  stabilization_init();
  stabilization_none_init();
  stabilization_attitude_init();
  jevois_init();
  object_tracking_init();
}

static inline void modules_actuators_init(void) {
  motor_mixing_init();
}

static inline void modules_init(void) {
  modules_datalink_init();
  modules_default_init();
  modules_actuators_init();
}

static inline void modules_datalink_periodic_task(void) {


}

static inline void modules_default_periodic_task(void) {
  static uint8_t i1; i1++; if (i1>=1) i1=0;
  static uint16_t i512; i512++; if (i512>=512) i512=0;


  if (gps_datalink_gps_datalink_periodic_check_status == MODULES_START) {
    gps_datalink_gps_datalink_periodic_check_status = MODULES_RUN;
  }
  if (gps_datalink_gps_datalink_periodic_check_status == MODULES_STOP) {
    gps_datalink_gps_datalink_periodic_check_status = MODULES_IDLE;
  }













  imu_apogee_periodic();
  if (i512 == 0 && gps_datalink_gps_datalink_periodic_check_status == MODULES_RUN) {
    gps_datalink_periodic_check();
  }
}

static inline void modules_actuators_periodic_task(void) {



}

static inline void modules_periodic_task(void) {
  modules_datalink_periodic_task();
  modules_default_periodic_task();
  modules_actuators_periodic_task();
}

static inline void modules_datalink_event_task(void) {
  pprz_dl_event();
}

static inline void modules_default_event_task(void) {
  imu_apogee_event();
  jevois_event();
}

static inline void modules_actuators_event_task(void) {
}

static inline void modules_event_task(void) {
  modules_datalink_event_task();
  modules_default_event_task();
  modules_actuators_event_task();
}

#ifdef MODULES_DATALINK_C

#include "pprzlink/messages.h"
#include "generated/airframe.h"
static inline void modules_parse_datalink(uint8_t msg_id __attribute__ ((unused)),
                                          struct link_device *dev __attribute__((unused)),
                                          struct transport_tx *trans __attribute__((unused)),
                                          uint8_t *buf __attribute__((unused))) {
  if (msg_id == DL_REMOTE_GPS) { gps_datalink_parse_REMOTE_GPS(); }
  else if (msg_id == DL_REMOTE_GPS_SMALL) { gps_datalink_parse_REMOTE_GPS_SMALL(); }
  else if (msg_id == DL_REMOTE_GPS_LOCAL) { gps_datalink_parse_REMOTE_GPS_LOCAL(); }
}

#endif // MODULES_DATALINK_C

#endif // MODULES_H
