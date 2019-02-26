-------------------------------------------------------------------------------
simple-optitracklist-python-cpp is a minimal application (C++ and python) to print subcribed ros position from natnet2ros (paparazzi)

run node
--------
on GCS (192.168.1.237)
roscore
ROS_MASTER_URI=http://shama:11311/

onboard (192.168.1.246)
export ROS_MASTER_URI=http://192.168.1.237:11311/
export ROS_IP=192.168.1.246
~/proxy/exe/pprz_ros_publisher
(set scaled_sensors on pprz telemetry)

on GCS
export ROS_MASTER_URI=http://192.168.1.237:11311/
rostopic list
rostopic echo /imu/data
