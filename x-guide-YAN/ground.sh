#!/bin/bash

# example (prelimanary add PermitRootLogin in sshd_config and ssh-copy-id -i root@groundpi_112)
#  /usr/bin/ssh  root@groundpi_112 "/home/pi/groundpi.sh 192.168.1.236 > /dev/null 2>&1 &"
#if [ -z "$1" ];then GCS_IP="127.0.0.1";else GCS_IP=$1;fi

HOME_WFB=/home/pprz/Projects/compagnon-software/wifibroadcast

#GCS_IP=192.168.3.1
GCS_IP=127.0.0.1

if [ $# -eq 2 ]; then

  wl=$1
  nb=$2

  PIDFILE=/tmp/wfb_${nb}_${wl}.pid

  $HOME_WFB/wfb_tx -K $HOME_WFB/gs.key -p 7 -u $((4300+nb)) -k 1 -n 2 $wl > /dev/null 2>&1 &
  echo $! >> $PIDFILE

#  $HOME_WFB/wfb_rx -K $HOME_WFB/gs.key -p 7 -u 4000 -c 127.0.0.1 -k 1 -n 2 $wl > /dev/null 2>&1 &
#  echo $! >> $PIDFILE
  $HOME_WFB/wfb_rx -K $HOME_WFB/gs.key -p 6 -u $((5600+nb)) -c $GCS_IP $wl > /dev/null 2>&1 &
  echo $! >> $PIDFILE
  $HOME_WFB/wfb_rx -K $HOME_WFB/gs.key -p 1 -u $((5700+nb)) -c $GCS_IP $wl > /dev/null 2>&1 &
  echo $! >> $PIDFILE
#  if [[ $nb = 1 ]]; then
  $HOME_WFB/wfb_rx -K $HOME_WFB/gs.key -p 2 -u $((4242+2*(1+nb))) -c $GCS_IP -k 1 -n 2 $wl > /dev/null 2>&1 &
#  else
#    $HOME_WFB/wfb_rx -K $HOME_WFB/gs.key -p 2 -u 4242 -c $GCS_IP -k 1 -n 2 $wl > /dev/null 2>&1 &
#  fi
  echo $! >> $PIDFILE
#  if [[ $nb = 1 ]]; then
  $HOME_WFB/wfb_tx -K $HOME_WFB/gs.key -p 3 -u $((4243+2*(1+nb))) -k 1 -n 2 $wl > /dev/null 2>&1 &
#  else
#    $HOME_WFB/wfb_tx -K $HOME_WFB/gs.key -p 3 -u 4243 -k 1 -n 2 $wl > /dev/null 2>&1 &
#  fi
  echo $! >> $PIDFILE
  $HOME_WFB/wfb_tx -K $HOME_WFB/gs.key -p 4 -u $((14800+nb)) -k 1 -n 2 $wl > /dev/null 2>&1 &
  echo $! >> $PIDFILE
  $HOME_WFB/wfb_rx -K $HOME_WFB/gs.key -p 5 -u $((14900+nb)) -c 127.0.0.1 -k 1 -n 2 $wl > /dev/null 2>&1 &
  echo $! >> $PIDFILE
  
  socat TUN:10.0.$((1+nb)).1/24,tun-name=groundtuntx$nb,iff-no-pi,tun-type=tun,iff-up udp-sendto:127.0.0.1:$((14800+nb)) > /dev/null 2>&1 &
  echo $! >> $PIDFILE
  socat udp-listen:$((14900+nb)),reuseaddr,fork  TUN:10.0.$((1+nb)).1/24,tun-name=groundtunrx$nb,iff-no-pi,tun-type=tun,iff-up > /dev/null 2>&1 &
  echo $! >> $PIDFILE
  sleep 1
  ifconfig groundtuntx$nb mtu 1400 up &

  while [ ! "`sysctl -w net.ipv4.conf.groundtunrx$nb.rp_filter=2`" = "net.ipv4.conf.groundtunrx$nb.rp_filter = 2" ];do sleep 1; done

fi
