/** @file
 *  @brief PPRZLink message header for BAT in class telemetry
 *
 *  
 *  @see http://paparazziuav.org
 */

#ifndef _VAR_MESSAGES_telemetry_BAT_H_
#define _VAR_MESSAGES_telemetry_BAT_H_


#include "pprzlink/pprzlink_device.h"
#include "pprzlink/pprzlink_transport.h"
#include "pprzlink/pprzlink_utils.h"
#include "pprzlink/pprzlink_message.h"


#ifdef __cplusplus
extern "C" {
#endif

#if DOWNLINK

#define DL_BAT 12
#define PPRZ_MSG_ID_BAT 12

/**
 * Macro that redirect calls to the default version of pprzlink API
 * Used for compatibility between versions.
 */
#define pprzlink_msg_send_BAT _send_msg(BAT,PPRZLINK_DEFAULT_VER)

/**
 * Sends a BAT message (API V2.0 version)
 *
 * @param msg the pprzlink_msg structure for this message
 * @param _throttle 
 * @param _voltage 
 * @param _amps 
 * @param _flight_time 
 * @param _kill_auto_throttle 
 * @param _block_time 
 * @param _stage_time 
 * @param _energy 
 */
static inline void pprzlink_msg_v2_send_BAT(struct pprzlink_msg * msg, int16_t *_throttle, uint16_t *_voltage, int16_t *_amps, uint16_t *_flight_time, uint8_t *_kill_auto_throttle, uint16_t *_block_time, uint16_t *_stage_time, int16_t *_energy) {
#if PPRZLINK_ENABLE_FD
  long _FD = 0; /* can be an address, an index, a file descriptor, ... */
#endif
  const uint8_t size = msg->trans->size_of(msg, /* msg header overhead */4+2+2+2+2+1+2+2+2);
  if (msg->trans->check_available_space(msg, _FD_ADDR, size)) {
    msg->trans->count_bytes(msg, size);
    msg->trans->start_message(msg, _FD, /* msg header overhead */4+2+2+2+2+1+2+2+2);
    msg->trans->put_bytes(msg, _FD, DL_TYPE_UINT8, DL_FORMAT_SCALAR, &(msg->sender_id), 1);
    msg->trans->put_named_byte(msg, _FD, DL_TYPE_UINT8, DL_FORMAT_SCALAR, msg->receiver_id, NULL);
    uint8_t comp_class = (msg->component_id & 0x0F) << 4 | (1 & 0x0F);
    msg->trans->put_named_byte(msg, _FD, DL_TYPE_UINT8, DL_FORMAT_SCALAR, comp_class, NULL);
    msg->trans->put_named_byte(msg, _FD, DL_TYPE_UINT8, DL_FORMAT_SCALAR, DL_BAT, "BAT");
    msg->trans->put_bytes(msg, _FD, DL_TYPE_INT16, DL_FORMAT_SCALAR, (void *) _throttle, 2);
    msg->trans->put_bytes(msg, _FD, DL_TYPE_UINT16, DL_FORMAT_SCALAR, (void *) _voltage, 2);
    msg->trans->put_bytes(msg, _FD, DL_TYPE_INT16, DL_FORMAT_SCALAR, (void *) _amps, 2);
    msg->trans->put_bytes(msg, _FD, DL_TYPE_UINT16, DL_FORMAT_SCALAR, (void *) _flight_time, 2);
    msg->trans->put_bytes(msg, _FD, DL_TYPE_UINT8, DL_FORMAT_SCALAR, (void *) _kill_auto_throttle, 1);
    msg->trans->put_bytes(msg, _FD, DL_TYPE_UINT16, DL_FORMAT_SCALAR, (void *) _block_time, 2);
    msg->trans->put_bytes(msg, _FD, DL_TYPE_UINT16, DL_FORMAT_SCALAR, (void *) _stage_time, 2);
    msg->trans->put_bytes(msg, _FD, DL_TYPE_INT16, DL_FORMAT_SCALAR, (void *) _energy, 2);
    msg->trans->end_message(msg, _FD);
  } else
        msg->trans->overrun(msg);
}

// Compatibility with the protocol v1.0 API
#define pprzlink_msg_v1_send_BAT pprz_msg_send_BAT
#define DOWNLINK_SEND_BAT(_trans, _dev, throttle, voltage, amps, flight_time, kill_auto_throttle, block_time, stage_time, energy) pprz_msg_send_BAT(&((_trans).trans_tx), &((_dev).device), AC_ID, throttle, voltage, amps, flight_time, kill_auto_throttle, block_time, stage_time, energy)
/**
 * Sends a BAT message (API V1.0 version)
 *
 * @param trans A pointer to the transport_tx structure used for sending the message
 * @param dev A pointer to the link_device structure through which the message will be sent
 * @param ac_id The id of the sender of the message
 * @param _throttle 
 * @param _voltage 
 * @param _amps 
 * @param _flight_time 
 * @param _kill_auto_throttle 
 * @param _block_time 
 * @param _stage_time 
 * @param _energy 
 */
static inline void pprz_msg_send_BAT(struct transport_tx *trans, struct link_device *dev, uint8_t ac_id, int16_t *_throttle, uint16_t *_voltage, int16_t *_amps, uint16_t *_flight_time, uint8_t *_kill_auto_throttle, uint16_t *_block_time, uint16_t *_stage_time, int16_t *_energy) {
    struct pprzlink_msg msg;
    msg.trans = trans;
    msg.dev = dev;
    msg.sender_id = ac_id;
    msg.receiver_id = 0;
    msg.component_id = 0;
    pprzlink_msg_v2_send_BAT(&msg,_throttle,_voltage,_amps,_flight_time,_kill_auto_throttle,_block_time,_stage_time,_energy);
}


#else // DOWNLINK

#define DOWNLINK_SEND_BAT(_trans, _dev, throttle, voltage, amps, flight_time, kill_auto_throttle, block_time, stage_time, energy) {}
static inline void pprz_send_msg_BAT(struct transport_tx *trans __attribute__((unused)), struct link_device *dev __attribute__((unused)), uint8_t ac_id __attribute__((unused)), int16_t *_throttle __attribute__((unused)), uint16_t *_voltage __attribute__((unused)), int16_t *_amps __attribute__((unused)), uint16_t *_flight_time __attribute__((unused)), uint8_t *_kill_auto_throttle __attribute__((unused)), uint16_t *_block_time __attribute__((unused)), uint16_t *_stage_time __attribute__((unused)), int16_t *_energy __attribute__((unused))) {}

#endif // DOWNLINK


/** Getter for field throttle in message BAT
  *
  * @param _payload : a pointer to the BAT message
  * @return 
  */
static inline int16_t pprzlink_get_DL_BAT_throttle(uint8_t * _payload __attribute__((unused)))
{
    return _PPRZ_VAL_int16_t(_payload, 4);
}


/** Getter for field voltage in message BAT
  *
  * @param _payload : a pointer to the BAT message
  * @return 
  */
static inline uint16_t pprzlink_get_DL_BAT_voltage(uint8_t * _payload __attribute__((unused)))
{
    return _PPRZ_VAL_uint16_t(_payload, 6);
}


/** Getter for field amps in message BAT
  *
  * @param _payload : a pointer to the BAT message
  * @return 
  */
static inline int16_t pprzlink_get_DL_BAT_amps(uint8_t * _payload __attribute__((unused)))
{
    return _PPRZ_VAL_int16_t(_payload, 8);
}


/** Getter for field flight_time in message BAT
  *
  * @param _payload : a pointer to the BAT message
  * @return 
  */
static inline uint16_t pprzlink_get_DL_BAT_flight_time(uint8_t * _payload __attribute__((unused)))
{
    return _PPRZ_VAL_uint16_t(_payload, 10);
}


/** Getter for field kill_auto_throttle in message BAT
  *
  * @param _payload : a pointer to the BAT message
  * @return 
  */
static inline uint8_t pprzlink_get_DL_BAT_kill_auto_throttle(uint8_t * _payload __attribute__((unused)))
{
    return _PPRZ_VAL_uint8_t(_payload, 12);
}


/** Getter for field block_time in message BAT
  *
  * @param _payload : a pointer to the BAT message
  * @return 
  */
static inline uint16_t pprzlink_get_DL_BAT_block_time(uint8_t * _payload __attribute__((unused)))
{
    return _PPRZ_VAL_uint16_t(_payload, 13);
}


/** Getter for field stage_time in message BAT
  *
  * @param _payload : a pointer to the BAT message
  * @return 
  */
static inline uint16_t pprzlink_get_DL_BAT_stage_time(uint8_t * _payload __attribute__((unused)))
{
    return _PPRZ_VAL_uint16_t(_payload, 15);
}


/** Getter for field energy in message BAT
  *
  * @param _payload : a pointer to the BAT message
  * @return 
  */
static inline int16_t pprzlink_get_DL_BAT_energy(uint8_t * _payload __attribute__((unused)))
{
    return _PPRZ_VAL_int16_t(_payload, 17);
}


/* Compatibility macros */
#define DL_BAT_throttle(_payload) pprzlink_get_DL_BAT_throttle(_payload)
#define DL_BAT_voltage(_payload) pprzlink_get_DL_BAT_voltage(_payload)
#define DL_BAT_amps(_payload) pprzlink_get_DL_BAT_amps(_payload)
#define DL_BAT_flight_time(_payload) pprzlink_get_DL_BAT_flight_time(_payload)
#define DL_BAT_kill_auto_throttle(_payload) pprzlink_get_DL_BAT_kill_auto_throttle(_payload)
#define DL_BAT_block_time(_payload) pprzlink_get_DL_BAT_block_time(_payload)
#define DL_BAT_stage_time(_payload) pprzlink_get_DL_BAT_stage_time(_payload)
#define DL_BAT_energy(_payload) pprzlink_get_DL_BAT_energy(_payload)



#ifdef __cplusplus
}
#endif // __cplusplus

#endif // _VAR_MESSAGES_telemetry_BAT_H_

