/*
  This program bridge serial and network interfaces.
  Furthermore outcomming messages are parse for DL_IMU_ACCEL_SCALED downlink message 
  to get sensor information
*/


#include "uartnet.h"
#include "pprzlink/pprz_transport.h"
 
#define DOWNLINK 1
#include "pprzlink/messages.h"

/*****************************************************************************/
void *pprzout_run()
{
  struct pprz_transport pprz_data;
  uint8_t len=0;
  uint8_t buf[uartnet_maxbufsize];

  uint8_t sender_id;
  uint8_t receiver_id;
  uint8_t component_id;
  uint8_t class_id;
  uint8_t msg_id;
 
  while(true) {
    len = uartnet_getout((uint8_t *)&buf);

    for (int i=0;i<len;i++) {
      parse_pprz(&pprz_data,buf[i]);

      if(pprz_data.trans_rx.msg_received) {
        for (int k = 0; k < pprz_data.trans_rx.payload_len; k++) {
          buf[k] = pprz_data.trans_rx.payload[k];
        }

        sender_id    = pprzlink_get_msg_sender_id(buf); 
        receiver_id  = pprzlink_get_msg_receiver_id(buf);
        component_id = pprzlink_get_msg_component_id(buf);
        class_id     = pprzlink_get_msg_class_id(buf); 
        msg_id       = pprzlink_get_msg_id(buf); 

        printf("%d %d %d %d %d\n",sender_id, receiver_id, component_id,
		      class_id, msg_id);

	if(msg_id == DL_IMU_ACCEL_SCALED) {
          float ax = DL_IMU_ACCEL_SCALED_ax(buf);
          float ay = DL_IMU_ACCEL_SCALED_ay(buf);
          float az = DL_IMU_ACCEL_SCALED_az(buf);
	  printf("%f %f %f\n",ax,ay,az);
	}

        pprz_data.trans_rx.msg_received = false;
      }
    }
  }
}

/*****************************************************************************/
void main(int c, char **argv) 
{
  pthread_t uartnet_id;
  pthread_t pprzout_id;
  
  uartnet_t arg;
  strcpy(arg.serdev,"/dev/ttyAMA0");
  arg.serspeed=B115200;
  strcpy(arg.netipdest,"192.168.1.255");
  arg.netportout = 4242;
  arg.netportin = 4243;
 
  pthread_create(&uartnet_id, NULL, uartnet_run, (void *)&arg);
  pthread_create(&pprzout_id, NULL, pprzout_run, NULL);
  sleep(1);
  pthread_join(uartnet_id,NULL); 
  pthread_join(pprzout_id,NULL); 
}
