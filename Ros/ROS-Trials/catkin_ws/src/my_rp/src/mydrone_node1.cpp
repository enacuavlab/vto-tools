#include <ros/ros.h>
#include <visualization_msgs/Marker.h>

int main( int argc, char** argv )
{
  ros::init(argc, argv, "mydrone_node1");
  ros::NodeHandle n;
  ros::Rate r(100);
  ros::Publisher marker_pub = n.advertise<visualization_msgs::Marker>("my_topic", 1);


  while (ros::ok())
  {
    visualization_msgs::Marker marker;
    marker.header.frame_id = "/my_fixedframe";
    marker.header.stamp = ros::Time::now();

    marker.ns = "mydrone_node1";
    marker.id = 0;

    marker.type = visualization_msgs::Marker::MESH_RESOURCE;
    marker.mesh_resource = "package://my_rp/meshes/ParrotArDrone.stl";

    marker.pose.position.x = 0;
    marker.pose.position.y = 0;
    marker.pose.position.z = 0;
    marker.pose.orientation.x = 0.0;
    marker.pose.orientation.y = 0.0;
    marker.pose.orientation.z = 0.0;
    marker.pose.orientation.w = 1.0;

    marker.scale.x = 1.0;
    marker.scale.y = 1.0;
    marker.scale.z = 1.0;

    marker.color.r = 0.0f;
    marker.color.g = 1.0f;
    marker.color.b = 0.0f;
    marker.color.a = 1.0;

    marker_pub.publish(marker);

    r.sleep();
  }
}
