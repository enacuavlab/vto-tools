#!/bin/bash

HOME_PRJ=/home/pi/Projects/compagnon-software/
HOME_WFB=$HOME_PRJ/wifibroadcast
PIDFILE=/tmp/wfb.pid

if [ $# -eq 2 ]; then

  wl=$1
  nb=$2

  $HOME_WFB/wfb_tx -K $HOME_WFB/drone.key -p 6 -u 5600 $wl > /dev/null 2>&1 &
  echo $! > $PIDFILE
  $HOME_WFB/wfb_tx -K $HOME_WFB/drone.key -p 1 -u 5700 $wl > /dev/null 2>&1 &
  echo $! >> $PIDFILE
  $HOME_WFB/wfb_tx -K $HOME_WFB/drone.key -p 2 -u 4244 -k 1 -n 2 $wl > /dev/null 2>&1 &
  echo $! >> $PIDFILE
  $HOME_WFB/wfb_rx -K $HOME_WFB/drone.key -p 3 -u 4245 -c 127.0.0.1 -k 1 -n 2 $wl > /dev/null 2>&1 &
  echo $! >> $PIDFILE
  $HOME_WFB/wfb_rx -K $HOME_WFB/drone.key -p 4 -u 14901 -c 127.0.0.1 -k 1 -n 2 $wl > /dev/null 2>&1 &
  echo $! >> $PIDFILE
  $HOME_WFB/wfb_tx -K $HOME_WFB/drone.key -p 5 -u 14900 -k 1 -n 2 $wl > /dev/null 2>&1 &
  echo $! >> $PIDFILE

  if uname -a | grep -cs "4.9"> /dev/null 2>&1;then
    DEVICE="/dev/ttyTHS1"
    $HOME_PRJ/scripts/air_camjet.sh
  else
    DEVICE="/dev/ttyAMA0"
    $HOME_PRJ/scripts/air_campi.sh
  fi

  socat -u $DEVICE,raw,echo=0,b115200 - | tee >(socat - udp-sendto:127.0.0.1:4244) >(socat - udp-sendto:127.0.0.1:4246) > /dev/null 2>&1 &
  echo $! >> $PIDFILE
#  socat -u udp-listen:4245,reuseaddr,fork $DEVICE,raw,echo=0,b115200 > /dev/null 2>&1 &
#  echo $! >> $PIDFILE

  $HOME_PRJ/scripts/proxy-air.py > /dev/null 2>&1 &
  echo $! >> $PIDFILE


  socat TUN:10.0.$((1+nb)).2/24,tun-name=airtuntx,iff-no-pi,tun-type=tun,iff-up udp-sendto:127.0.0.1:14900 > /dev/null 2>&1 &
  echo $! >> $PIDFILE
  socat udp-listen:14901,reuseaddr,fork TUN:10.0.$((1+nb)).2/24,tun-name=airtunrx,iff-no-pi,tun-type=tun,iff-up > /dev/null 2>&1 &
  echo $! >> $PIDFILE
  sleep 1
  ifconfig airtuntx mtu 1400 up &

  while [ ! "`sysctl -w net.ipv4.conf.airtunrx.rp_filter=2`" = "net.ipv4.conf.airtunrx.rp_filter = 2" ];do sleep 1; done
  route add default airtuntx  > /dev/null 2>&1 &
  echo $! >> $PIDFILE

fi
