#!/bin/bash

#------------------------------------------------------------------------------
# WIFIBROADCAST CONFIGURATION
#------------------------------------------------------------------------------
WFB_KEY="-K /home/pi/wifibroadcast-svpcom/drone.key" 
WFB_TX="/home/pi/wifibroadcast-svpcom/wfb_tx "$WFB_KEY
WFB_RX="/home/pi/wifibroadcast-svpcom/wfb_rx "$WFB_KEY
WFB_DEV="wlan1"
WFB_CHAN=36

#CLIENT_IP=192.168.43.194
CLIENT_IP=127.0.0.1

#------------------------------------------------------------------------------
# EXECUTION COMMON
#------------------------------------------------------------------------------
ifconfig $WFB_DEV down
sleep 1
iw dev $WFB_DEV set monitor otherbss
iw reg set DE
ifconfig $WFB_DEV up
iw dev $WFB_DEV set channel $WFB_CHAN
#iw $WFB_DEV info

#------------------------------------------------------------------------------
# EXECUTION 
#------------------------------------------------------------------------------
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

socat TUN:10.0.1.1/24,tun-name=groundpituntx,iff-no-pi,tun-type=tun,su=pi,iff-up udp-sendto:127.0.0.1:14800 &
sleep 1
ip link set groundpituntx mtu 1400 &
socat udp-listen:14801 TUN:10.0.1.1/24,tun-name=groundpitunrx,iff-no-pi,tun-type=tun,su=pi,iff-up &

#------------------------------------------------------------------------------
else
echo "FLYING"

#---------
sleep 1
$WFB_TX -p 1 -u 5600 $WFB_DEV &

#---------
sleep 1
#/home/pi/proxy/exe/bridge &
#DEVICE=ttyAMA0
DEVICE=ttyUSB0
DEVICECMD=/dev/$DEVICE,raw,echo=0,b115200
socat -u udp-listen:4243,reuseaddr,fork $DEVICECMD &
socat -u $DEVICECMD udp-sendto:127.0.0.1:4242 &

#---------
sleep 1
$WFB_TX -p 2 -u 4242 $WFB_DEV &
$WFB_RX -p 3 -u 4243 -c 127.0.0.1 $WFB_DEV &

#---------
sleep 1
$WFB_TX -p 5 -u 14900 -k 1 -n 2 $WFB_DEV &
$WFB_RX -p 4 -u 14901 -c 127.0.0.1 -k 1 -n 2 $WFB_DEV &

socat TUN:10.0.1.2/24,tun-name=airpituntx,iff-no-pi,tun-type=tun,su=pi,iff-up udp-sendto:127.0.0.1:14900 &
sleep 1
ip link set airpituntx mtu 1400 &
socat udp-listen:14901 TUN:10.0.1.2/24,tun-name=airpitunrx,iff-no-pi,tun-type=tun,su=pi,iff-up &

#------------------------------------------------------------------------------
fi
