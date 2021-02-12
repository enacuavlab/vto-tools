#!/bin/bash 

# example (prelimanary add PermitRootLogin in sshd_config and ssh-copy-id -i root@groundpi_112)
#  /usr/bin/ssh  root@groundpi_112 "/home/pi/groundpi.sh 192.168.1.236 > /dev/null 2>&1 &"

if /bin/pidof -x "wfb_tx" >/dev/null ; then
  exit 1
fi
GCS_IP=$1

ifconfig wlan0 down  
sleep 1
ifconfig wlan1 down  
sleep 1 
iw dev wlan1 set monitor otherbss  
iw reg set DE  
ifconfig wlan1 up  
iw dev wlan1 set channel 40 
#iw dev wlan1_DEV set txpower fixed 4000 
#iw wlan1 info 
/home/pi/wifibroadcast-svpcom/wfb_rx -K /home/pi/wifibroadcast-svpcom/drone.key -p 6 -c 127.0.0.1 -u 5610 wlan1 &
/home/pi/wifibroadcast-svpcom/wfb_rx -K /home/pi/wifibroadcast-svpcom/drone.key -p 1 -c 127.0.0.1 -u 5600 wlan1 &
/home/pi/wifibroadcast-svpcom/wfb_rx -K /home/pi/wifibroadcast-svpcom/drone.key -p 2 -u 4242 -c $GCS_IP -k 1 -n 2 wlan1 &
/home/pi/wifibroadcast-svpcom/wfb_tx -K /home/pi/wifibroadcast-svpcom/drone.key -p 3 -u 4243 -k 1 -n 2 wlan1 &
/home/pi/wifibroadcast-svpcom/wfb_tx -K /home/pi/wifibroadcast-svpcom/drone.key -p 4 -u 14800 -k 1 -n 2 wlan1 &
/home/pi/wifibroadcast-svpcom/wfb_rx -K /home/pi/wifibroadcast-svpcom/drone.key -p 5 -u 14801 -c 127.0.0.1 -k 1 -n 2 wlan1 &
gst-launch-1.0 udpsrc port=5600 \
 ! tee name=streams \
 ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 \
 ! udpsink host=127.0.0.1 port=5620 streams. \
 ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 \
 ! application/x-rtp, encoding-name=H264,payload=96 \
 ! rtph264depay \
 ! video/x-h264,stream-format=byte-stream \
 ! fdsink | /home/pi/wifibroadcast_osd/fpv_video/fpv_video &
/home/pi/gst-rtsp-server-1.14.4/examples/.libs/test-launch \
  "udpsrc port=5620 do-timestamp=true ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay name=pay0 pt=96 config-interval=1" \
  "udpsrc port=5610 do-timestamp=true ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay name=pay0 pt=96 config-interval=1" &
socat -u TUN:10.0.1.1/24,tun-name=groundpituntx,iff-no-pi,tun-type=tun,iff-up udp-sendto:127.0.0.1:14800 & 
socat -u udp-listen:14801,reuseaddr,fork TUN:10.0.1.1/24,tun-name=groundpitunrx,iff-no-pi,tun-type=tun,iff-up &
sleep 1
ifconfig groundpituntx mtu 1400 up &
