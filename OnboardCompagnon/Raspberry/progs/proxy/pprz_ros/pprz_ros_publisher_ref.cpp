#include "ros/ros.h"
#include "sensor_msgs/Imu.h"

#include <signal.h>

//#include "geometry_msgs/PoseStamped.h"
//#include "geometry_msgs/Pose.h"

extern "C" {
#include "uartnet.h"
#include "pprzlink/pprz_transport.h"

#define DOWNLINK 1
#include "pprzlink/messages.h"
}

/*
export ROS_MASTER_URI=http://shama:11311
*/


static int running = 0;

ros::Publisher imu_pub;
std::string imu_frame_id_;

/*****************************************************************************/
void publish_data(float ax,float ay, float az)
{
  sensor_msgs::Imu imu_msg;
  imu_msg.header.stamp = ros::Time::now();
  imu_msg.header.frame_id = imu_frame_id_;

  imu_msg.linear_acceleration.x = ax;
  imu_msg.linear_acceleration.y = ay;
  imu_msg.linear_acceleration.z = az;
  //imu_msg.angular_velocity.x =  data.gyro[0];
  //imu_msg.angular_velocity.y = data.gyro[1];
  //imu_msg.angular_velocity.z = data.gyro[2];

  imu_pub.publish(imu_msg);
}

/*****************************************************************************/
void *pprzros_run()
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

        //printf("%d %d %d %d %d\n",sender_id, receiver_id, component_id,
	//	      class_id, msg_id);

	if(msg_id == DL_IMU_ACCEL_SCALED) {
          float ax = DL_IMU_ACCEL_SCALED_ax(buf);
          float ay = DL_IMU_ACCEL_SCALED_ay(buf);
          float az = DL_IMU_ACCEL_SCALED_az(buf);

	  publish_data(ax,ay,az);
	  printf("%f %f %f\n",ax,ay,az);
	}

        pprz_data.trans_rx.msg_received = false;
      }
    }
  }
}

/*****************************************************************************/
static void __signal_handler(__attribute__ ((unused)) int dummy)
{
  // interrupt handler to catch ctrl-c
  running=0;
  return;
}


/*****************************************************************************/
int main(int argc, char **argv) 
{
  pthread_t uartnet_id;
  pthread_t pprzros_id;

  ros::init(argc, argv, "imu_pub_nod");
  ros::NodeHandle n("imu");
  n.param<std::string>("frame_id", imu_frame_id_, "imu_link");
  ROS_INFO("FrameID: %s",imu_frame_id_.c_str());

  //imu_pub=n.advertise<sensor_msgs::Imu>("imu/data", 100);
  imu_pub = n.advertise<sensor_msgs::Imu>("data", 1, false);

  //ros::Rate loop_rate(10);

  signal(SIGINT, __signal_handler);
  running = 1;
  
  pthread_create(&uartnet_id, NULL,(void* (*)(void*))uartnet_run, NULL);
  ROS_INFO("MPU initialized");
  pthread_create(&pprzros_id, NULL,(void* (*)(void*))pprzros_run, NULL);
  ROS_INFO("ROS publisher initialized");

  while(running) sleep(1);

  pthread_join(uartnet_id,NULL); 
  pthread_join(pprzros_id,NULL); 

  return 0;
}



