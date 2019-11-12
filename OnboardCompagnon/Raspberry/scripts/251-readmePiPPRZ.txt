-------------------------------------------------------------------------------
Install Paparazzi on PI3 debian strech (Debian_9.0)
-------------------------------------------------------------------------------
wget -q "http://download.opensuse.org/repositories/home:/flixr:/paparazzi-uav/Debian_9.0/Release.key" -O- | sudo apt-key add -

echo "deb http://download.opensuse.org/repositories/home:/flixr:/paparazzi-uav/Debian_9.0/ ./" | tee -a /etc/apt/sources.list

sudo apt-get update 
sudo apt-get install paparazzi-dev

sudo apt-get update
sudo apt-get install gcc-arm-none-eabi gdb-arm-none-eabi

git clone https://github.com/enacuavlab/paparazzi.git
cd paparazzi
git checkout demo_vto

sudo cp conf/system/udev/rules/*.rules /etc/udev/rules.d/ && sudo udevadm control --reload-rules

make
./paparazzi

export PAPARAZZI_HOME=/home/pi/paparazzi
export PAPARAZZI_SRC=/home/pi/paparazzi

copy 
var/aircrafts/Karpet/*

rm /home/ppi/paparazzi/conf/conf.xml
ln -s /home/pi/paparazzi/conf/airframes/ENAC/conf_enac_vto.xml /home/ppi/paparazzi/conf/conf.xml




---------------------------------------------------------
#sudo apt-get install python-pip
#sudo pip install numpy
#sudo pip install ivy

#git clone https://gitlab.com/ivybus/ivy-python.git
#cd ivy-python/
#sudo ./setup.py install

---------------------------------------------------------

sudo apt-get install python3-pip
sudo pip3 install numpy
sudo pip3 install ivy-python
sudo pip3 install lxml

---------------------------------------------------------
/home/pi/paparazzi/sw/ground_segment/tmtc/server
/home/pi/paparazzi/sw/ground_segment/tmtc/link  -udp 
/home/pi/paparazzi/sw/ground_segment/python/natnet3.x/natnet2ivy.py  -ac 115 115  -s 192.168.1.230 -f 5

---------------------------------------------------------
/etc/udev/rules.d/91-joystick.rules
SUBSYSTEM=="hidraw", ACTION=="add", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5710", RUN+="/home/pi/groundpi-joystick.sh"
KERNEL=="input[0-9]*", ACTION=="remove", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5710", RUN+="/home/pi/groundpi-joystick.sh"


sudo service udev restart
tail -f /var/log/syslog

#!/bin/bash

export PAPARAZZI_SRC=/home/pi/paparazzi
export PAPARAZZI_HOME=/home/pi/paparazzi

if [ "$ACTION" = "add" ]
then
  $PAPARAZZI_HOME/sw/ground_segment/joystick/input2ivy -ac Karpet frsky_lite.xml -b 192.168.1.255:2010 &
elif [ "$ACTION" = "remove" ]
  then killall input2ivy 
fi

#sudo -E /home/pi/paparazzi/sw/ground_segment/joystick/input2ivy -ac Karpet frsky_lite.xml -b 192.168.1.255:2010 &


---------------------------------------------------------

