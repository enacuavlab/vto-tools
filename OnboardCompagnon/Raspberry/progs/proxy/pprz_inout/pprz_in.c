/*
  This program bridge serial and network interfaces.
  Furthermore incomming messages are parse for DL_SETTING uplink message 
  to get setting information for de the Jevois camera module

  When the telemétry setting is "Start" the the video streaming is started.
  When the telemétry setting is "Stop" the the video streaming is killed.
*/


#include <stdlib.h> 
 
#include "uartnet.h"
#include "pprzlink/pprz_transport.h"

#define DOWNLINK 1
#include "pprzlink/messages.h"
#include "pprzlink/datalink/SETTING.h"

#define GST_EXEC "gst-launch-1.0 -v v4l2src device=/dev/video0 ! video/x-raw,width=640,height=500,framerate=20/1 ! omxh264enc ! rtph264pay ! udpsink host=192.168.1.255 port=5000 &"
#define GST_KILL "sudo killall gst-launch-1.0"

bool Gst_launched=false;

/*****************************************************************************/
void *pprzcam_run()
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
    len = uartnet_getin((uint8_t *)&buf);

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

        //printf("%d %d %d %d %d\n",sender_id, receiver_id, component_id,
	//	      class_id, msg_id);

	if(msg_id == DL_SETTING) {
          uint8_t i = DL_SETTING_index(buf);
	  if(i==9) { // From generated settings.h => ... case 9: jevois_stream
            float var = DL_SETTING_value(buf);
	    if(var==0.0f) {
              if(Gst_launched) { 
                Gst_launched = false;
                system(GST_KILL);
              }
            } else {
              if(!Gst_launched) { 
                Gst_launched = true;
                system(GST_EXEC);
              }
            }
	  }
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
  pthread_t pprzcam_id;
  
  uartnet_t arg;
  strcpy(arg.serdev,"/dev/ttyAMA0");
  arg.serspeed=B115200;
  strcpy(arg.netipdest,"192.168.1.255");
  arg.netportout = 4242;
  arg.netportin = 4243;
 
  pthread_create(&uartnet_id, NULL, uartnet_run, (void *)&arg);
  pthread_create(&pprzcam_id, NULL, pprzcam_run, NULL);
  sleep(1);
  pthread_join(uartnet_id,NULL); 
  pthread_join(pprzcam_id,NULL); 
}
