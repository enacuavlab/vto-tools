#!/bin/bash

# DRONE_AP and VID_PORT should be set before calling this script

wifiadapters=`iw dev | grep Interface | awk '{print $2}'`
WIFI_DEV=""

for elt in $wifiadapters; do
  if [ -n $WIFI_DEV ]; then
    if [ `grep -Fx $elt material/disablewifiadapt.txt | wc -l` == 0 ];then
      if [ `iwconfig $elt | grep Mode:Managed | wc -l` == 1 ];then
        if [ `ip a | grep $elt | pcregrep -o1 'inet ([0-9]+.[0-9]+.[0-9]+.[0-9]+)' | wc -l` == 0 ];then
          WIFI_DEV=$elt
        fi
      fi 
    fi
  fi
done

if [ -z $WIFI_DEV ]; then
  echo "No wifi adapter available !"
  exit -1
else

  docker run -d --rm --privileged \
    -e DRONE_AP=$DRONE_AP \
    -e WIFI_DEV=$WIFI_DEV \
    -e VID_PORT=$VID_PORT \
    --name $DRONE_AP \
    wifiproxy &
  
  ph=`iw dev $WIFI_DEV info | grep wiphy | awk '{print "phy"$2}'`
  nb=`rfkill --raw | awk '{print $1" "$3}' | grep $ph | awk '{print $1}'`
  st=`rfkill --raw | awk '{print $1" "$4}' | grep $nb | awk '{print $2}'`
  if [ $st == "blocked" ];then `rfkill unblock $nb`;fi
  
  NSID=`sudo docker inspect -f '{{.State.Pid}}' $DRONE_AP`
  sudo ln -s /proc/$NSID/ns/net /var/run/netns/$NSID
  
  PHYSID=`iw dev $WIFI_DEV info | grep wiphy | awk '{print "phy"$2}'`
  sudo iw $PHYSID set netns $NSID
  
  docker exec $DRONE_AP /connect_drone.sh &

fi
