#!/bin/bash

# Connect wifi adapter

ph=`iw dev $WIFI_DEV info | grep wiphy | awk '{print "phy"$2}'`
nb=`rfkill --raw | awk '{print $1" "$3}' | grep $ph | awk '{print $1}'`
st=`rfkill --raw | awk '{print $1" "$4}' | grep $nb | awk '{print $2}'`
if [ $st == "blocked" ];then `rfkill unblock $nb`;fi

# Give a network interface to a container.
NSID=`sudo docker inspect -f '{{.State.Pid}}' $DRONE_AP`
sudo ln -s /proc/$NSID/ns/net /var/run/netns/$NSID

# Add the interface to the container namespace
PHYSID=`iw dev $WIFI_DEV info | grep wiphy | awk '{print "phy"$2}'`
sudo iw $PHYSID set netns $NSID
