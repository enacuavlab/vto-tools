#include "ros/ros.h"
#include "geometry_msgs/PoseStamped.h"
#include "geometry_msgs/Pose.h"

extern "C" {
#include "uartnet.h"
#include "pprzlink/pprz_transport.h"
}

/*
export ROS_MASTER_URI=http://shama:11311
*/

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

        printf("%d %d %d %d %d\n",sender_id, receiver_id, component_id,
		      class_id, msg_id);

        pprz_data.trans_rx.msg_received = false;
      }
    }
  }
}

/*****************************************************************************/
void callback(const geometry_msgs::PoseStamped::ConstPtr& msg)
{
  ROS_INFO("%f  %f  %f", msg->pose.position.x, msg->pose.position.y, msg->pose.position.z);
  ROS_INFO("%f  %f  %f  %f", msg->pose.orientation.x, msg->pose.orientation.y, msg->pose.orientation.z, msg->pose.orientation.w);
}

/*****************************************************************************/
int main(int argc, char **argv) 
{
  pthread_t uartnet_id;
  pthread_t pprzcam_id;

  ros::init(argc, argv, "optitracklistener");
  ros::NodeHandle n;
  ros::Subscriber sub = n.subscribe("geometry_msgs/Pose", 1000, callback);

  pthread_create(&uartnet_id, NULL,(void* (*)(void*))uartnet_run, NULL);
  pthread_create(&pprzcam_id, NULL,(void* (*)(void*))pprzcam_run, NULL);
  sleep(1);
  ros::spin();
  pthread_join(uartnet_id,NULL); 
  pthread_join(pprzcam_id,NULL); 

  return 0;
}



