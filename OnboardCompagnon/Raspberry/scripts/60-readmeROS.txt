ROS Installation on PI-ZERO W
-----------------------------
Raspberry PI-Zero W
  ARMv6:
  KO: "MELODIC" No support for ubuntu ROS on armv6
  OK: "KINETIC" Found already compiled debian package (rpi-zerow-kinetic_1.0.0-1_armhf.deb)


From raspbian lite strech install builded package (os=debian:jessie ?)
-----------------------------------------------------------------------
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install -y build-essential gdebi
mkdir -p ~/tmp
wget https://github.com/nomumu/Kinetic4RPiZero/releases/download/v_2017-10-15/rpi-zerow-kinetic_1.0.0-1_armhf.zip
unzip rpi-zerow-kinetic_1.0.0-1_armhf.zip
sudo gdebi rpi-zerow-kinetic_1.0.0-1_armhf.deb
sudo /opt/ros/kinetic/initialize.sh
(70 minutes)


