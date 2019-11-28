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


Install rpicamsrc:
sudo apt-get install dh-autoreconf
sudo apt-get install libgstreamer1.0-dev and libgstreamer-plugins-base1.0-dev
sudo apt-get install gstreamer1.0-libav gstreamer1.0-omx
sudo apt-get install git
git clone https://github.com/thaytan/gst-rpicamsrc.git
cd gst-rpicamsrc
./autogen.sh
make
sudo make install


rename /etc/wpa_suppicant/wpa_supplicant.conf to /etc/wpa_suppicant/wpa_supplicant-wlan0.conf


sudo apt-get install libpcap-dev wiringpi
git clone https://github.com/RespawnDespair/wifibroadcast-base.git
cd wifibroadcast-base
git submodule init
git submodule update
make

-----------------------------------------------------------------

sudo ifconfig wlan1 down
sudo iw dev wlan1 set monitor otherbss
sudo iw reg set DE
sudo ifconfig wlan1 up
sudo iw dev wlan1 set channel 36
sudo iw wlan1 info

-----------------------------------------
get video.c.48-mm from Open.HD/wifibroadcast-hello_video
compile to hello_video.bin.48-mm

/etc/rc.local
su root -c /home/pi/groundpi.sh

#!/bin/sh
/home/pi/wifibroadcast-base/rx -p 0 -d 1 -b 8 -r 4 -f 1024 wlan1 | \
/home/pi/hello-video-hdmi/hello_video.bin.48-mm


-----------------------------------------
/etc/rc.local
su root -c /home/pi/airpi.sh &

airpi.sh
#!/bin/sh

WIDTH=1280
HEIGHT=740
FPS=48
KEYFRAMERATE=5

EXTRAPARAMS="-cd H264 -n -fl -ih -pf high -if both -ex sports -mm average -awb horizon"
# -cd H264: codec
# -n: Disables the preview window completely.
# -fl: Forces a flush of output data buffers as soon as video data is written
# -ih: Forces the stream to include PPS and SPS headers on every I-frame (Apple players)
# -pf high: Sets the H264 profile to be used for the encoding
# -if both: Sets the H264 intra-refresh type
# -ex sports: select setting for sports (fast shutter etc.)a
# -mm average: average the whole frame for metering
# -awb horizon: set Automatic White Balance (AWB) mode


VIDEO_BLOCKS=8
VIDEO_FECS=4
VIDEO_BLOCKLENGTH=1024
VIDEO_FRAMETYPE=1
VIDEO_WIFI_BITRATE=18

NICS=wlan1

VIDEO_BITRATE=auto
BITRATE_PERCENT=65

BITRATE_MEASURED=`/home/pi/wifibroadcast-base/tx_measure -p 77 -b $VIDEO_BLOCKS -r $VIDEO_FECS -f $VIDEO_BLOCKLENGTH -t $VIDEO_FRAMETYPE -d $VIDEO_WIFI_BITRATE -y 0 $NICS`
BITRATE=$((BITRATE_MEASURED*$BITRATE_PERCENT/100))
BITRATE_KBIT=$((BITRATE/1000))
BITRATE_MEASURED_KBIT=$((BITRATE_MEASURED/1000))
echo "$BITRATE_MEASURED_KBIT kBit/s * $BITRATE_PERCENT% = $BITRATE_KBIT kBit/s video bitrate"

ANNOTATION="ENAC"

nice -n -9 raspivid -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -g $KEYFRAMERATE -t 0 $EXTRAPARAMS -a "$ANNOTATION" -ae 22 -o - | \
nice -n -9 /home/pi/wifibroadcast-base/tx_rawsock -p 0 -b $VIDEO_BLOCKS -r $VIDEO_FECS -f $VIDEO_BLOCKLENGTH -t $VIDEO_FRAMETYPE -d $VIDEO_WIFI_BITRATE -y 0 $NICS


process crash while running with following code ?!
gst-launch-1.0 rpicamsrc vflip=true bitrate=$BITRATE ! \
  video/x-h264,width=$WIDTH,height=$HEIGHT,framerate=$FPS/1 ! \
  fdsink | \
  nice -n -9 /home/pi/wifibroadcast-base/tx_rawsock -p 0 -b $VIDEO_BLOCKS -r $VIDEO_FECS -f $VIDEO_BLOCKLENGTH -t $VIDEO_FRAMETYPE -d $VIDEO_WIFI_BITRATE -y 0 $NICS


-------------------------------------------------------------------------------
groundpi: 
- rx: 2.8 CPU%, 0.4 MEM%
- hello_video.bin: 4x = 17 CPU% 0.3 MEM%

aipi:PI0 
- tx_rawsock: 27 CPU%, 0.4 MEM%
- raspivid: 3x = 8.9 CPU%, 0.6 MEM%

aipi:PI3 
- tx_rawsock: 9 CPU%, 0.1 MEM%
- raspivid: 3x = 1.6 CPU%, 0.2 MEM%
- gst-launch rpicamsrc|fdsink :  2.6 CPU%, 0.8 MEM%

-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
groundpi.sh 
#!/bin/bash

ifconfig wlan1 down
iw dev wlan1 set monitor otherbss
iw reg set DE
ifconfig wlan1 up
iw dev wlan1 set channel 36
iw wlan1 info

sleep 1


VIDEO_BLOCKS=8
VIDEO_FECS=4
VIDEO_BLOCKLENGTH=1024

NICS=wlan1

#/home/pi/wifibroadcast-base/rx -p 0 -d 1 -b 8 -r 4 -f 1024 wlan1 | \
#/home/pi/hello-video-hdmi/hello_video.bin.48-mm

rm -f /tmp/videofifo1 /tmp/videofifo2 /tmp/videofifo3 /tmp/videofifo4
killall hello_video.bin.48-mm
killall rx

# videofifo1: local display, hello_video.bin
mkfifo -m777 /tmp/videofifo1
# videofifo2: secondary display, hotspot/usb-tethering
mkfifo -m777 /tmp/videofifo2
# videofifo3: recording
mkfifo -m777 /tmp/videofifo3
# videofifo4: wbc relay
mkfifo -m777 /tmp/videofifo4

ionice -c 1 -n 3 /home/pi/wifibroadcast-base/rx -p 0 -d 1 -b $VIDEO_BLOCKS -r $VIDEO_FECS -f $VIDEO_BLOCKLENGTH $NICS \
	| ionice -c 1 -n 4 nice -n -10 tee >(ionice -c 1 -n 4 nice -n -10 /home/pi/ftee /tmp/videofifo2 > /dev/null 2>&1) \
	>(ionice -c 1 nice -n -10 /home/pi/ftee /tmp/videofifo4 > /dev/null 2>&1) \
	>(ionice -c 3 nice /home/pi/ftee /tmp/videofifo3 > /dev/null 2>&1) \
	| ionice -c 1 -n 4 nice -n -10 /home/pi/ftee /tmp/videofifo1 \
	> /dev/null 2>&1  &

ionice -c 1 -n 4 nice -n -10 cat /tmp/videofifo1 \
	| ionice -c 1 -n 4 nice -n -10 /home/pi/hello-video-hdmi/hello_video.bin.48-mm \
       	> /dev/null 2>&1 &

ionice -c 1 -n 4 nice -n -5 cat /tmp/videofifo2 \
	| nice -n -5 gst-launch-1.0 fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.1.46 port=5000 \
	> /dev/null 2>&1 &

# client command
#gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false


-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
airpi.sh 
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
# -cd H264: codec
# -n: Disables the preview window completely.
# -fl: Forces a flush of output data buffers as soon as video data is written
# -ih: Forces the stream to include PPS and SPS headers on every I-frame (Apple players)
# -pf high: Sets the H264 profile to be used for the encoding
# -if both: Sets the H264 intra-refresh type
# -ex sports: select setting for sports (fast shutter etc.)a
# -mm average: average the whole frame for metering
# -awb horizon: set Automatic White Balance (AWB) mode

ANNOTATION="ENAC"

VIDEO_BLOCKS=8
VIDEO_FECS=4
VIDEO_BLOCKLENGTH=1024
VIDEO_FRAMETYPE=1
VIDEO_WIFI_BITRATE=18

NICS=wlan1

VIDEO_BITRATE=auto
BITRATE_PERCENT=65

BITRATE_MEASURED=`/home/pi/wifibroadcast-base/tx_measure -p 77 -b $VIDEO_BLOCKS -r $VIDEO_FECS -f $VIDEO_BLOCKLENGTH -t $VIDEO_FRAMETYPE -d $VIDEO_WIFI_BITRATE -y 0 $NICS`
BITRATE=$((BITRATE_MEASURED*$BITRATE_PERCENT/100))
BITRATE_KBIT=$((BITRATE/1000))
BITRATE_MEASURED_KBIT=$((BITRATE_MEASURED/1000))
echo "$BITRATE_MEASURED_KBIT kBit/s * $BITRATE_PERCENT% = $BITRATE_KBIT kBit/s video bitrate"


rm -f /tmp/videofifo1 /tmp/videofifo2 /tmp/videofifo3
killall raspivid
killall tx_rawsock

# videofifo1: wifibroadcast
mkfifo -m777 /tmp/videofifo1
# videofifo2: secondary display, hotspot/usb-tethering
mkfifo -m777 /tmp/videofifo2
# videofifo3: recording
mkfifo -m777 /tmp/videofifo3


mkfifo -m777 /tmp/videofifo1
mkfifo -m777 /tmp/videofifo2
mkfifo -m777 /tmp/videofifo2


ionice -c 1 -n 3 raspivid -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -g $KEYFRAMERATE -t 0 $EXTRAPARAMS -a "$ANNOTATION" -ae 22 -o - \
	| ionice -c 1 -n 4 nice -n -10 tee >(ionice -c 1 -n 4 nice -n -10 /home/pi/ftee /tmp/videofifo2 > /dev/null 2>&1) \
	>(ionice -c 3 nice /home/pi/ftee /tmp/videofifo3 > /dev/null 2>&1) \
	| ionice -c 1 -n 4 nice -n -10 /home/pi/ftee /tmp/videofifo1 \
	> /dev/null 2>&1  &

ionice -c 1 -n 3 nice -n -10 /home/pi/wifibroadcast-base/tx_rawsock -p 0 -b $VIDEO_BLOCKS -r $VIDEO_FECS -f $VIDEO_BLOCKLENGTH -t $VIDEO_FRAMETYPE -d $VIDEO_WIFI_BITRATE -y 0 $NICS \
	< /tmp/videofifo1 &

#
#SHOULD NOT BE USED WITH TX_RAWSOCK RUNNING
#
#ionice -c 1 -n 4 nice -n -5 cat /tmp/videofifo2 \
#	| nice -n -5 gst-launch-1.0 fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.1.46 port=6000 \
#	> /dev/null 2>&1 &
# client command
#gst-launch-1.0 udpsrc port=6000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false

