#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import PoseStamped

def callback(data):
  #rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
  #print(data)

  print('----------------------------------')
  print(data.header.stamp)
  print(data.pose.position.x)
  print(data.pose.position.y)
  print(data.pose.position.z)
  print(data.pose.orientation.x)
  print(data.pose.orientation.y)
  print(data.pose.orientation.z)
  print(data.pose.orientation.w)


def listener():
  rospy.init_node('optitracklistener', anonymous=True)
  rospy.Subscriber('geometry_msgs/Pose', PoseStamped, callback)
  rospy.spin()

if __name__ == '__main__':
  listener()
