-------------------------------------------------------------------------------
simple-optitracklist-python-cpp is a minimal application (C++ and python) to print subcribed ros position from natnet2ros (paparazzi)

-------------------------------------------------------------------------------
catkin_ws is a catkin workspace to show how to use catkin tool

build wokspace
----------------
mkdir -p catkin_ws/src
cd catkin_ws
catkin_make

source devel/setup.bash


create package 
--------------
cd src
catkin_create_pkg my_rp visualization_msgs rospy roscpp

create src/mydronei-node1.cpp
modify CMakeLists
"
add_executable(mydrone src/mydronei-node1.cpp)
target_link_libraries(mydrone-node1 ${catkin_LIBRARIES})
"

create and add meshes/


build package
-------------
cd catkin_ws
catkin_make


run node
--------
roscore

source devel/setup.bash
rosrun my_rp mydrone_node1


vizualize node
--------------
source devel/setup.bash

rviz -f my_fixedframe 
(add marker with /my_topic)

rviz -d ../myconfig.rviz


