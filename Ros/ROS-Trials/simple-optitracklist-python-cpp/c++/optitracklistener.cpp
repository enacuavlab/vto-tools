#include "ros/ros.h"
#include "geometry_msgs/PoseStamped.h"
#include "geometry_msgs/Pose.h"

void callback(const geometry_msgs::PoseStamped::ConstPtr& msg)
{
  ROS_INFO("%f  %f  %f", msg->pose.position.x, msg->pose.position.y, msg->pose.position.z);
  ROS_INFO("%f  %f  %f  %f", msg->pose.orientation.x, msg->pose.orientation.y, msg->pose.orientation.z, msg->pose.orientation.w);
}

int main(int argc, char **argv) 
{
  ros::init(argc, argv, "optitracklistener");
  ros::NodeHandle n;
  ros::Subscriber sub = n.subscribe("geometry_msgs/Pose", 1000, callback);
  ros::spin();

  return 0;
}



