#!/bin/bash
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
/home/pi/wifibroadcast-svpcom/wfb_tx -K /home/pi/wifibroadcast-svpcom/drone.key -p 6 -u 5610 wlan1 &
/home/pi/wifibroadcast-svpcom/wfb_tx -K /home/pi/wifibroadcast-svpcom/drone.key -p 1 -u 5600 wlan1 &
/home/pi/wifibroadcast-svpcom/wfb_tx -K /home/pi/wifibroadcast-svpcom/drone.key -p 2 -u 4242 -k 1 -n 2 wlan1 &
/home/pi/wifibroadcast-svpcom/wfb_rx -K /home/pi/wifibroadcast-svpcom/drone.key -p 3 -u 4243 -c 127.0.0.1 -k 1 -n 2 wlan1 &
/home/pi/wifibroadcast-svpcom/wfb_tx -K /home/pi/wifibroadcast-svpcom/drone.key -p 5 -u 14900 -k 1 -n 2 wlan1 &
/home/pi/wifibroadcast-svpcom/wfb_rx -K /home/pi/wifibroadcast-svpcom/drone.key -p 4 -u 14901 -c 127.0.0.1 -k 1 -n 2 wlan1 &
rm /tmp/camera*;
#/usr/bin/raspivid -t 0 -w 640 -h 480 -fps 30/1 -b 3000000 -g 5 -cd H264 -n -fl -ih -pf high -if both -ex sports -mm average -awb horizon -a ENAC -ae 22 -o - \
#/home/pi/RaspiCV/build/raspicv -t 0 -w 640 -h 480 -fps 30/1 -b 3000000 -g 5 -vf -hf -cd H264 -n -fl -ih -x /dev/null -r /dev/null -rf gray -o - \
rm /tmp/fromimu
rm /tmp/camera*
/home/pi/RaspiCV/build/raspicv -t 0 -w 640 -h 480 -fps 30/1 -b 500000 -vf -hf -cd H264 -n -a ENAC -ae 22 -x /dev/null -r /dev/null -rf gray -o - \
  | gst-launch-1.0 fdsrc \
    ! h264parse \
    ! video/x-h264,stream-format=byte-stream,alignment=au \
    ! rtph264pay name=pay0 pt=96 config-interval=1 \
    ! udpsink host=127.0.0.1 port=5610 &
sleep 10
gst-launch-1.0 shmsrc socket-path=/tmp/camera3 do-timestamp=true \
  ! video/x-raw, format=BGR, width=640, height=480, framerate=30/1, colorimetry=1:1:5:1  \
  ! v4l2h264enc extra-controls="controls,video_bitrate=4000000;" \
  ! rtph264pay name=pay0 pt=96 config-interval=1 \
  ! udpsink host=127.0.0.1 port=5600 &


#if [ -f "/data/logfile0.txt" ]; then
#  FILE="/data/logfile`ls /data/logfile* | wc -l`.txt"
#else
#  FILE="/data/logfile0.txt"
#fi

PPRZ_LINK_IP=127.0.0.1
PPRZ_LINK_IN=4242
PPRZ_LINK_OUT=4243
socat -u /dev/ttyAMA0,raw,echo=0,b115200 - | tee >(socat - udp-sendto:127.0.0.1:4245) >(socat - udp-sendto:127.0.0.1:4242) > /dev/null 2>&1 &
socat -u udp-listen:4243,reuseaddr,fork /dev/ttyAMA0,raw,echo=0,b115200 &

export LD_LIBRARY_PATH=/home/pi/muxer/lib
/home/pi/muxer/exe/muxer 4244 4245 > /dev/null 2>&1 &

#                  | PPRZ_LINK_IP:PPRZ_LINK_IN
#      /dev/tty -> |
#                  | 4246 -> |
#                            | muxer -> |
#                  | 4245 -> |          | 4244 -> /dev/tty
# PPRZ_LINK_OUT -> | -----------------> |

#export LD_LIBRARY_PATH=/home/pi/muxer/lib
#/home/pi/muxer/exe/muxer 4244 4245 4246 &

#/home/pi/muxer/exe/muxer 4244 4245 > $FILE &
#export PYTHONPATH=/home/pi/pprzlink/lib/v2.0/python:$PYTHONPATH
#/usr/bin/python3 /home/pi/muxer/src/muxer.py 4244 4245 4246 &

#socat -u /dev/ttyAMA0,raw,echo=0,b115200 - | tee >(socat - udp-sendto:127.0.0.1:4245) >(socat - udp-sendto:$PPRZ_LINK_IP:$PPRZ_LINK_IN) > /dev/null &
#socat -u udp-listen:$PPRZ_LINK_OUT,reuseaddr,fork /dev/ttyAMA0,raw,echo=0,b115200 &

#socat -u udp-listen:$PPRZ_LINK_OUT,reuseaddr,fork  | tee >(socat - udp-sendto:127.0.0.1:4245) >(socat - /dev/ttyAMA0,raw,echo=0,b115200) > /dev/null &
#socat -u udp-listen:4243,reuseaddr,fork /dev/ttyAMA0,raw,echo=0,b115200 &

#socat -u /dev/ttyAMA0,raw,echo=0,b115200 udp-sendto:127.0.0.1:4242 &

#export LD_LIBRARY_PATH=/home/pi/muxer/lib
#/home/pi/muxer/exe/muxer 4244 4245 &

socat TUN:10.0.1.2/24,tun-name=airpituntx,iff-no-pi,tun-type=tun,su=pi,iff-up udp-sendto:127.0.0.1:14900 &
socat udp-listen:14901,reuseaddr,fork TUN:10.0.1.2/24,tun-name=airpitunrx,iff-no-pi,tun-type=tun,su=pi,iff-up &
sleep 1
ifconfig airpituntx mtu 1400 up
