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
