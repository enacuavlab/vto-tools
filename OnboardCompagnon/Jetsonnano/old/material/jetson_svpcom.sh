#!/bin/bash

#export GROUNDED=true;
export GROUNDED=false;

#------------------------------------------------------------------------------
# WIFIBROADCAST CONFIGURATION
# /etc/network/interfaces =>  mon1 : monitor mode, channel
#------------------------------------------------------------------------------
WFB_HOME="/home/pprz/wifibroadcast-svpcom"
WFB_KEY="-K $WFB_HOME/drone.key" 
WFB_TX="$WFB_HOME/wfb_tx "$WFB_KEY
WFB_RX="$WFB_HOME/wfb_rx "$WFB_KEY
WFB_DEV="mon1"

#CLIENT_IP=192.168.43.194
CLIENT_IP=127.0.0.1

#------------------------------------------------------------------------------
# EXECUTION 
#------------------------------------------------------------------------------
killall wfb_tx wfb_rx socat

if ($GROUNDED); then
echo "GROUNDED"

#---------
sleep 1
$WFB_RX -p 1 -c 127.0.0.1 -u 5000 $WFB_DEV | socat - udp-datagram:localhost:3333 &
#socat udp-recv:3333 -

#---------
sleep 1
$WFB_RX -p 2 -u 4242 -c $CLIENT_IP $WFB_DEV &
$WFB_TX -p 3 -u 4243 $WFB_DEV &

#---------
sleep 1
$WFB_TX -p 4 -u 14800 -k 1 -n 2 $WFB_DEV &
$WFB_RX -p 5 -u 14801 -c 127.0.0.1 -k 1 -n 2 $WFB_DEV &

socat TUN:10.0.1.1/24,tun-name=groundjetsontuntx,iff-no-pi,tun-type=tun,su=pprz,iff-up udp-sendto:127.0.0.1:14800 &
sleep 1
ip link set groundjetsontuntx mtu 1400 &
socat udp-listen:14801 TUN:10.0.1.1/24,tun-name=groundjetsontunrx,iff-no-pi,tun-type=tun,su=pprz,iff-up &

#------------------------------------------------------------------------------
else
echo "FLYING"

#---------
sleep 1
$WFB_TX -p 1 -u 5600 $WFB_DEV &

#---------
sleep 1
#DEVICE=ttyAMA0
#DEVICE=ttyUSB0
#DEVICECMD=/dev/$DEVICE,raw,echo=0,b115200
#socat -u udp-listen:4243,reuseaddr,fork $DEVICECMD &
#socat -u $DEVICECMD udp-sendto:127.0.0.1:4242 &

#---------
sleep 1
$WFB_TX -p 2 -u 4242 $WFB_DEV &
$WFB_RX -p 3 -u 4243 -c 127.0.0.1 $WFB_DEV &

#---------
sleep 1
$WFB_TX -p 5 -u 14900 -k 1 -n 2 $WFB_DEV &
$WFB_RX -p 4 -u 14901 -c 127.0.0.1 -k 1 -n 2 $WFB_DEV &

#socat TUN:10.0.1.2/24,tun-name=airjetsontuntx,iff-no-pi,tun-type=tun,su=pprz,iff-up udp-sendto:127.0.0.1:14900 &
#sleep 1
#ip link set airjetsontuntx mtu 1400 &
#socat udp-listen:14901 TUN:10.0.1.2/24,tun-name=airjetsontunrx,iff-no-pi,tun-type=tun,su=pprz,iff-up &
socat -u TUN:10.0.1.2/24,tun-name=airjetsontuntx,iff-no-pi,tun-type=tun,iff-up udp-sendto:127.0.0.1:14900 &
sleep 1
ip link set airjetsontuntx mtu 1400 &
socat -u udp-listen:14901 TUN:10.0.1.2/24,tun-name=airjetsontunrx,iff-no-pi,tun-type=tun,iff-up &


#------------------------------------------------------------------------------
fi
