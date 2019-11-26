-------------------------------------------------------------------------------
https://madennis.gitbooks.io/px4dev/content/en/qgc/video_streaming_wifi_broadcast.html
-------------------------------------------------------------------------------
Installation on PI3 (and PI0)

Install raspbian strech light (configure ssh, wpa)
Boot and connect to mobile hotspot (nmap -sn 192.168.43.0/24)
Configure (raspi-config)
Reboot and add swap (/etc/dphys-swapfile CONF_SWAPSIZE=1024)


Switch uart to bluetooth, and disable bluetooth.


Install gstreamer:
sudo apt-get update
sudo apt-get install gstreamer1.0-tools
sudo apt-get install gstreamer1.0-plugins-bad
sudo apt-get install gstreamer1.0-plugins-good


#Install rpicamsrc:
#sudo apt-get install dh-autoreconf
#sudo apt-get install libgstreamer1.0-dev and libgstreamer-plugins-base1.0-dev
#sudo apt-get install gstreamer1.0-libav gstreamer1.0-omx
#sudo apt-get install git
#git clone https://github.com/thaytan/gst-rpicamsrc.git
#cd gst-rpicamsrc
#./autogen.sh
#make
#sudo make install


rename /etc/wpa_suppicant/wpa_supplicant.conf to /etc/wpa_suppicant/wpa_supplicant-wlan0.conf


sudo apt-get install libpcap-dev libsodium-dev
git clone https://github.com/svpcom/wifibroadcast
cd wifibroadcast
make

copy drone.key and gs.key

#git clone https://github.com/racic/ftee.git
#cd ftee
#gcc ftee.c -o ftee


Check which had the camera 
raspistill -o toto.jpg



/etc/rc.local
su root -c /home/pi/groundpi-svpcom.sh &
or
su root -c /home/pi/airpi-svpcom.sh &


----------------------------------------------------------------------------
airpi-svpcom.sh
----------------------------------------------------------------------------
#!/bin/bash

ifconfig wlan1 down
iw dev wlan1 set monitor otherbss
iw reg set DE
ifconfig wlan1 up
iw dev wlan1 set channel 36
iw wlan1 info

sleep 1

WIDTH=1280
HEIGHT=740
FPS=48
KEYFRAMERATE=5

EXTRAPARAMS="-cd H264 -n -fl -ih -pf high -if both -ex sports -mm average -awb horizon"
ANNOTATION="ENAC"

BITRATE=3000000 

rm -f /tmp/videofifo1 /tmp/videofifo2 /tmp/videofifo3
killall raspivid
killall wfb_tx

# videofifo1: wifibroadcast
mkfifo -m777 /tmp/videofifo1
# videofifo2: secondary display, hotspot/usb-tethering
mkfifo -m777 /tmp/videofifo2
# videofifo3: recording
mkfifo -m777 /tmp/videofifo3


ionice -c 1 -n 3 raspivid -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -g $KEYFRAMERATE -t 0 $EXTRAPARAMS -a "$ANNOTATION" -ae 22 -o - \
	| ionice -c 1 -n 4 nice -n -10 tee >(ionice -c 1 -n 4 nice -n -10 /home/pi/ftee/ftee /tmp/videofifo2 > /dev/null 2>&1) \
	>(ionice -c 3 nice /home/pi/ftee/ftee /tmp/videofifo3 > /dev/null 2>&1) \
	| ionice -c 1 -n 4 nice -n -10 /home/pi/ftee/ftee /tmp/videofifo1 \
	> /dev/null 2>&1  &

/home/pi/wifibroadcast-svpcom/wfb_tx -p 1 -u 5600 -K /home/pi/wifibroadcast-svpcom/drone.key wlan1 &

nice -n -5 gst-launch-1.0 filesrc location=/tmp/videofifo1 ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=127.0.0.1 port=5600 \
	> /dev/null 2>&1 &

#-------------------------------------------------------------------------------
/home/pi/proxy/exe/bridge &
#/home/pi/wifibroadcast-svpcom/wfb_tx -p 2 -u 4242 -K /home/pi/wifibroadcast-svpcom/drone.key wlan1 & 
#/home/pi/wifibroadcast-svpcom/wfb_rx -p 3 -c 127.0.0.1 -u 4243 -K /home/pi/wifibroadcast-svpcom/gs.key wlan1 &

----------------------------------------------------------------------------
groundpi-svpcom.sh
----------------------------------------------------------------------------
#!/bin/bash

ifconfig wlan1 down
iw dev wlan1 set monitor otherbss
iw reg set DE
ifconfig wlan1 up
iw dev wlan1 set channel 36
iw wlan1 info

sleep 1

rm -f /tmp/videofifo1 /tmp/videofifo2 /tmp/videofifo3 /tmp/videofifo4
killall fpv_video
killall wfb_rx

# videofifo1: local display, hello_video.bin
mkfifo -m777 /tmp/videofifo1
# videofifo2: secondary display, hotspot/usb-tethering
mkfifo -m777 /tmp/videofifo2
# videofifo3: recording
mkfifo -m777 /tmp/videofifo3
# videofifo4: wbc relay
mkfifo -m777 /tmp/videofifo4


/home/pi/wifibroadcast-svpcom/wfb_rx -p 1 -c 127.0.0.1 -u 5000 -K /home/pi/wifibroadcast-svpcom/gs.key wlan1 &

ionice -c 1 -n 3 gst-launch-1.0 udpsrc port=5000  ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! 'video/x-h264,stream-format=byte-stream' ! \
	fdsink \
	| ionice -c 1 -n 4 nice -n -10 tee >(ionice -c 1 -n 4 nice -n -10 /home/pi/ftee/ftee /tmp/videofifo2 > /dev/null 2>&1) \
	>(ionice -c 1 nice -n -10 /home/pi/ftee/ftee /tmp/videofifo4 > /dev/null 2>&1) \
	>(ionice -c 3 nice /home/pi/ftee /tmp/videofifo3 > /dev/null 2>&1) \
	| ionice -c 1 -n 4 nice -n -10 /home/pi/ftee/ftee /tmp/videofifo1 \
	> /dev/null 2>&1  &

ionice -c 1 -n 4 nice -n -10 cat /tmp/videofifo1 \
	| ionice -c 1 -n 4 nice -n -10 /home/pi/wifibroadcast_osd/fpv_video/fpv_video &

#nice -n -5 gst-launch-1.0 filesrc location=/tmp/videofifo2 ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.43.181 port=5500 \
#		> /dev/null 2>&1 &
# client command
#gst-launch-1.0 udpsrc port=5500 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false
#
#or install fst-rtsp-server
/home/pi/gst-rtsp-server-1.10.4/examples/test-launch "(filesrc location=/tmp/videofifo2 ! h264parse ! rtph264pay config-interval=1 pt=96 )" &
stream ready at rtsp://127.0.0.1:8554/test

# client command
#gst-launch-1.0 rtspsrc location=rtsp://192.168.1.235:8554/test ! rtph264depay ! avdec_h264 !  xvimagesink sync=false
