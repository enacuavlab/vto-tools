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


sudo apt-get install libpcap-dev libsodium-dev
git clone https://github.com/svpcom/wifibroadcast
cd wifibroadcast
make

copy drone.key and gs.key


Check which had the camera 
raspistill -o toto.jpg

gst-launch-1.0 rpicamsrc bitrate=10000000 ! video/x-h264,width=640,height=480,framerate=25/1,profile=high ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.43.181 port=5600
gst-launch-1.0 udpsrc port=5600 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false


sudo ifconfig wlan1 down
sudo iw dev wlan1 set monitor otherbss
#sudo iw reg set BO
sudo ifconfig wlan1 up
sudo iw dev wlan1 set channel 149 HT40+

gst-launch-1.0 rpicamsrc bitrate=10000000 ! video/x-h264,width=640,height=480,framerate=25/1,profile=high ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=127.0.0.1 port=5600

cd wifibroadcast
sudo ./wfb_tx -p 1 -u 5600 -K drone.key wlan1
(PI0 8% CPU)

sudo ifconfig wlan1 down
sudo iw dev wlan1 set monitor otherbss
#sudo iw reg set BO
sudo ifconfig wlan1 up
sudo iw dev wlan1 set channel 149 HT40+

cd wifibroadcast
sudo ./wfb_rx -p 1 -c 192.168.43.181 -u 5000 -K gs.key wlan1


gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false


-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
https://github.com/rodizio1/EZ-WifiBroadcast
Release candidate(recommended): v1.6RC6 (google drive)

wifibroadcast-1.txt
Air =>
  FREQ=5180
Ground =>
  FREQ=5180
  WIFI_HOTSPOT=Y
  FORWARD_STREAM=raw


2nd console connect vi hotspot
=> Laptop  
  gst-launch-1.0 udpsrc port=5600 ! h264parse ! avdec_h264 ! autovideosink sync=false  
=> Mobile
  RaspberryPi Camerea Viewer (Gstreamer)
    udpsrc port=5600 ! h264parse ! avdec_h264 ! autovideosink sync=false  


-------------------------------------------------------------------------------
https://github.com/seeul8er/DroneBridge/releases/tag/v0.5

wifibroadcast-1.txt
Air =>
  FREQ=5180
Ground =>
  FREQ=5180
  WIFI_HOTSPOT=Y
  FORWARD_STREAM=raw

DroneBridgeAirIni :
en_tel=N
en_video=N
en_comm=N
en_control=N

DroneBridgeGroundIni :
en_control=N
en_video=Y
en_comm=N


2nd console connect vi hotspot
=> Laptop  
  gst-launch-1.0 udpsrc port=5000 ! h264parse ! avdec_h264 ! autovideosink sync=false  
=> Mobile
  RaspberryPi Camerea Viewer (Gstreamer)
    udpsrc port=5000 ! h264parse ! avdec_h264 ! autovideosink sync=false  

ssh pi@192.168.2.1
raspberry


-------------------------------------------------------------------------------
https://github.com/DroneBridge/RPiKernel

Sources of the current kernel used for the DroneBridge Raspberry Pi images & its patch files. Kernel source files contain the https://github.com/aircrack-ng/rtl8812au driver




https://github.com/RespawnDespair/wifibroadcast-base


https://github.com/svpcom/wifibroadcast
https://github.com/svpcom/rtl8812au

-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
echo "Sarting telemetry for $NIC"
stty -F /dev/ttyAMA0 -imaxbel -opost -isig -icanon -echo -echoe -ixoff -ixon 115200
cat /dev/ttyAMA0 | $WBC_PATH/tx -p 1 -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $NIC &

echo "Starting tx for $NIC"
raspivid -ih -vf -hf -t 0 -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -n -g $KEYFRAMERATE -pf high -ex sports -o - | $WBC_PATH/tx -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $NIC > /dev/

killall cat
killall raspivid
killall tx

----------------------
#one card wlxc4e984d75e95
#other card wlxf4f26d1d0171

CARD="wlxf4f26d1d0171"

cd
cd wifibroadcast
sudo killall ifplugd #stop management of interface
sudo ifconfig $CARD down
sudo iw dev $CARD set monitor otherbss fcsfail
sudo ifconfig $CARD up
sudo iwconfig $CARD channel 13

#for video uncomment
#sudo ./rx -b 8 -r 4 -f 1024 $CARD | gst-launch-1.0 -v fdsrc ! h264parse ! avdec_h264 !  xvimagesink sync=false

#for telemetry uncomment
sudo ./rx -p 1 -b 8 -r 4 -f 1024 $CARD | cat





https://www.rcgroups.com/forums/showthread.php?2664393-EZ-WifiBroadcast-cheap-digital-HD-transmission-made-easy%21/page84

-------------------------------------------------------------------------------
git config --global --get-regexp http.*
http.proxy http://proxy:3128
https.proxy https://proxy:3128

git config --global --unset http.proxy
git config --global --unset https.proxy


-------------------------------------------------------------------------------
sudo apt-get install libpcap-dev wiringpi
make
apt search wiringpi


ip address
3: dc4ef407ea26: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 2304 qdisc mq state UNKNOWN group default qlen 1000
    link/ieee802.11/radiotap dc:4e:f4:07:ea:26 brd ff:ff:ff:ff:ff:ff

sudo iwconfig dc4ef407ea26
dc4ef407ea26  IEEE 802.11  Mode:Monitor  Frequency:2.472 GHz  Tx-Power=30 dBm   
          Retry short limit:7   RTS thr:off   Fragment thr:off
          Power Management:off

ifconfig dc4ef407ea26
dc4ef407ea26 Link encap:UNSPEC  HWaddr DC-4E-F4-07-EA-26-00-00-00-00-00-00-00-00-00-00  
          UP BROADCAST RUNNING MULTICAST  MTU:2304  Metric:1
          RX packets:216607 errors:0 dropped:9 overruns:0 frame:0
          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:225624753 (215.1 MiB)  TX bytes:0 (0.0 B)


/rx -p 0 -d 1 -b 8 -r 4 -f 1024 dc4ef407ea26 ! cat

-------------------------------------------------------------------------------
Raspbian stretch / Open-HD

uname -a
Linux raspberrypi 4.14.71-v7+ #1145 SMP Fri Sep 21 15:38:35 BST 2018 armv7l GNU/Linux


Raspbian
sudo dmesg 
[   73.348002] usb 1-1.3: new high-speed USB device number 4 using dwc_otg
[   73.493768] usb 1-1.3: New USB device found, idVendor=148f, idProduct=5572
[   73.493781] usb 1-1.3: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[   73.493789] usb 1-1.3: Product: 802.11 n WLAN
[   73.493798] usb 1-1.3: Manufacturer: Ralink
[   73.493806] usb 1-1.3: SerialNumber: 1.0
[   73.727812] usb 1-1.3: reset high-speed USB device number 4 using dwc_otg
[   73.866789] ieee80211 phy1: rt2x00_set_rt: Info - RT chipset 5592, rev 0222 detected
[   73.883632] ieee80211 phy1: rt2x00_set_rf: Info - RF chipset 000f detected
[   73.902785] ieee80211 phy1: Selected rate control algorithm 'minstrel_ht'

[   73.904372] usbcore: registered new interface driver rt2800usb
[   74.098603] ieee80211 phy1: rt2x00lib_request_firmware: Info - Loading firmware file 'rt2870.bin'
[   74.099637] ieee80211 phy1: rt2x00lib_request_firmware: Info - Firmware detected - version: 0.36
[   74.431172] IPv6: ADDRCONF(NETDEV_UP): wlan1: link is not ready

OPEN-HD
sudo dmesg
[  302.248666] usb 1-1.3: new high-speed USB device number 5 using dwc_otg
[  302.355082] usb 1-1.3: New USB device found, idVendor=148f, idProduct=5572
[  302.355099] usb 1-1.3: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[  302.355105] usb 1-1.3: Product: 802.11 n WLAN
[  302.355111] usb 1-1.3: Manufacturer: Ralink
[  302.355117] usb 1-1.3: SerialNumber: 1.0
[  302.434626] usb 1-1.3: reset high-speed USB device number 5 using dwc_otg
[  302.535774] ieee80211 phy2: rt2x00_set_rt: Info - RT chipset 5592, rev 0222 detected
[  302.564078] ieee80211 phy2: rt2x00_set_rf: Info - RF chipset 000f detected
[  302.565279] ieee80211 phy2: Selected rate control algorithm 'minstrel_ht'





Raspbian
lsmod
rt2800usb              28672  0
rt2800lib             102400  1 rt2800usb
rt2x00usb              24576  1 rt2800usb
rt2x00lib              57344  3 rt2800lib,rt2800usb,rt2x00usb
mac80211              659456  3 rt2800lib,rt2x00lib,rt2x00usb
crc_ccitt              16384  1 rt2800lib



OPEN-HD
lsmod
rt2800usb              28672  0
rt2x00usb              20480  1 rt2800usb
rt2800lib             102400  1 rt2800usb
crc_ccitt              16384  1 rt2800lib
rt2x00lib              49152  3 rt2800lib,rt2800usb,rt2x00usb
mac80211              491520  3 rt2800lib,rt2x00lib,rt2x00usb

sudo ls -l /lib/modules/4.14.71-v7+/kernel/drivers/net/wireless/ralink/rt2x00/
total 220
-rw-r--r-- 1 root root 98756 Sep 11  2019 rt2800lib.ko
-rw-r--r-- 1 root root 52648 Sep 11  2019 rt2800usb.ko
-rw-r--r-- 1 root root 50180 Sep 11  2019 rt2x00lib.ko
-rw-r--r-- 1 root root 15444 Sep 11  2019 rt2x00usb.ko


-------------------------------------------------------------------------------
sudo apt-get install raspberrypi-kernel-headers

sudo modprobe -r rt2800usb
sudo modprobe -r rt2x00lib
sudo modprobe -r rt2x00usb

sudo vi /etc/modprobe.d/blacklist.conf
blacklist rt2800usb
blacklist rt2x00lib
blacklist rt2x00usb

patch "rt2x00lib.h"




