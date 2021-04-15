#!/bin/bash

# example (prelimanary add PermitRootLogin in sshd_config and ssh-copy-id -i root@groundpi_112)
#  /usr/bin/ssh  root@groundpi_112 "/home/pi/groundpi.sh 192.168.1.236 > /dev/null 2>&1 &"
#if [ -z "$1" ];then GCS_IP="127.0.0.1";else GCS_IP=$1;fi

HOME_WFB=/home/pprz/Projects/compagnon-software/wifibroadcast
PIDFILE=/tmp/wfb.pid

#GCS_IP=192.168.3.1
GCS_IP=127.0.0.1

if [ -n "$1" ]; then

  wl=$1

  $HOME_WFB/wfb_rx -K $HOME_WFB/gs.key -p 7 -u 4000 -c 127.0.0.1 -k 1 -n 2 $wl > /dev/null 2>&1 &
  echo $! >> $PIDFILE
  $HOME_WFB/wfb_rx -K $HOME_WFB/gs.key -p 6 -u 5600 -c $GCS_IP $wl > /dev/null 2>&1 &
  echo $! > $PIDFILE
  $HOME_WFB/wfb_rx -K $HOME_WFB/gs.key -p 1 -u 5700 -c $GCS_IP $wl > /dev/null 2>&1 &
  echo $! > $PIDFILE
#  $HOME_WFB/wfb_rx -K $HOME_WFB/gs.key -p 2 -u 4242 -c $GCS_IP -k 1 -n 2 $wl > /dev/null 2>&1 &
#  echo $! >> $PIDFILE
#  $HOME_WFB/wfb_tx -K $HOME_WFB/gs.key -p 3 -u 4243 -k 1 -n 2 $wl > /dev/null 2>&1 &
#  echo $! >> $PIDFILE

  $HOME_WFB/wfb_tx -K $HOME_WFB/gs.key -p 4 -u 14800 -k 1 -n 2 $wl > /dev/null 2>&1 &
  echo $! >> $PIDFILE
  $HOME_WFB/wfb_rx -K $HOME_WFB/gs.key -p 5 -u 14801 -c 127.0.0.1 -k 1 -n 2 $wl > /dev/null 2>&1 &
  echo $! >> $PIDFILE
  
  socat TUN:10.0.1.1/24,tun-name=groundtuntx,iff-no-pi,tun-type=tun,iff-up udp-sendto:127.0.0.1:14800 > /dev/null 2>&1 &
  echo $! >> $PIDFILE
  socat udp-listen:14801,reuseaddr,fork  TUN:10.0.1.1/24,tun-name=groundtunrx,iff-no-pi,tun-type=tun,iff-up > /dev/null 2>&1 &
  echo $! >> $PIDFILE
  sleep 1
  ifconfig groundtuntx mtu 1400 up &

  while [ ! "`sysctl -w net.ipv4.conf.groundtunrx.rp_filter=2`" = "net.ipv4.conf.groundtunrx.rp_filter = 2" ];do sleep 1; done

fi
