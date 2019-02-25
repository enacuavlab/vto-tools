/etc/hosts
192.168.1.237	shama


export ROS_MASTER_URI=http://shama:11311
roscore


export ROS_MASTER_URI=http://192.168.6.1:11311/
export ROS_IP=192.168.6.2
rosrun bbblue_drivers imu_pub_node
