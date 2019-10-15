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


sudo apt-get install libpcap-dev 
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
su root -c /home/pi/airpi.sh

airpi.sh
#!/bin/sh

WIDTH=1280
HEIGHT=740
FPS=48
KEYFRAMERATE=5

EXTRAPARAMS="-cd H264 -n -fl -ih -pf high -if both -ex sports -mm average -awb horizon"

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


nice -n -9 raspivid -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -g $KEYFRAMERATE -t 0 $EXTRAPARAMS -a "$ANNOTATION" -ae 22 -o - | \
nice -n -9 /home/pi/wifibroadcast-base/tx_rawsock -p 0 -b $VIDEO_BLOCKS -r $VIDEO_FECS -f $VIDEO_BLOCKLENGTH -t $VIDEO_FRAMETYPE -d $VIDEO_WIFI_BITRATE -y 0 $NICS






