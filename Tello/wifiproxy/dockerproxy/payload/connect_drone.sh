#!/bin/bash

pkill socat

echo '- configuring device '$WIFI_DEV
ifconfig $WIFI_DEV down
ifconfig $WIFI_DEV up
iw dev $WIFI_DEV connect $DRONE_AP
echo '- requesting for DHCP'
cp /sbin/dhclient /usr/sbin/dhclinet >/dev/null
/usr/sbin/dhclinet $WIFI_DEV
pkill dhclient
WIFI_IP=$(ip a | grep $WIFI_DEV | pcregrep -o1 'inet ([0-9]+.[0-9]+.[0-9]+.[0-9]+)')
if [ -z "$WIFI_IP" ]
then
    echo '! proxy container did not get IP from drone wifi (is drone turned on?)'
    iwconfig $WIFI_DEV
    ifconfig $WIFI_DEV
    exit 1
else
    nohup /usr/bin/socat udp-listen:8889,reuseaddr,fork udp-sendto:192.168.10.1:8889 &>/dev/null &
    nohup /usr/bin/socat udp-listen:11111,reuseaddr,fork udp-sendto:172.17.0.1:$VID_PORT &>/dev/null &
    echo '- proxy container connected to drone wifi via '$WIFI_IP
    CONTAINER_IP=$(ip a | grep eth0 | pcregrep -o1 'inet ([0-9]+.[0-9]+.[0-9]+.[0-9]+)')
    echo '- SUCCESS! UDP forwarding setup. You can connect to wifi proxy container via:'
    echo ''
    echo $CONTAINER_IP
    exit 0
fi

