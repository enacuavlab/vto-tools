Jeston Nano

Wifibroadcast work tested with 
OK: Bus 001 Device 004: ID 148f:5572 Ralink Technology, Corp. RT5572 Wireless Adapter
OK: Bus 001 Device 004: ID 0bda:8812 Realtek Semiconductor Corp. RTL8812AU 802.11a/b/g/n/ac 2T2R DB WLAN Adapter

Wifiadapters can be mixed

----------------------------------------
Documentation 
https://docs.nvidia.com/jetson/

----------------------------------------
Get Jetson Nano Developer Kit - JETPACK 4.3
https://developer.nvidia.com/jetson-nano-sd-card-image

nv-jetson-nano-sd-card-image-r32.3.1.zip
Included:
- Ubuntu 18.04.4 LTS (GNU/Linux 4.9.140-tegra aarch64)
- GStreamer 1.14.5
- Opencv 4.1.1
 
Etcher: flash SD (30 min)
Plug not modified SD
Do not plug Ethernet nor Wifi adapter
First setup needs : Monitor, keyboard, mouse
Boot and set minimal configuration with desktop
shutdown -h now
(it turns the nano off off, power led turned off) 

Remove SD, an update network configuration on it.
Plug SD and boot

Then use ssh
shutdown -h now
(shutdown -r now)

!!!!
DO NOT USE COMMAND
"HALT"
USE 
"SHUTDOWN -H NOW"
!!!

----------------------------------------
CONFIGURE 
----------------------------------------
sudo vi /etc/wpa_supplicant/wpa_supplicant.conf
network={
  ssid="Androidxp"
  psk="pprzpprz"
}
network={
  ssid="pprz_router"
  key_mgmt=NONE
}
network={
  ssid="Livebox-7EA4"
  psk="6vNVEJNeLCYLubnbuk"
}
network={
  ssid="Livebox-1aa4"
  psk="E89831065C74F706AFC0E95F63"
}

---------
or for two wifi adapers
sudo vi /etc/network/interfaces
auto eth0
iface eth0 inet static
address 192.168.3.2
netmask 255.255.255.0

auto wlan0
iface wlan0 inet dhcp
    wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf

allow-hotplug wlan1
iface wlan1 inet manual
  pre-up iw phy phy1 interface add mon1 type monitor
  pre-up iw dev wlan1 del
  pre-up ifconfig mon1 up
  pre-up iw dev mon1 set channel 36

---------
or for one single wifi adapter
allow-hotplug wlan0
  iface wlan0 inet manual
  pre-up iw phy phy0 interface add mon1 type monitor
  pre-up iw dev wlan0 del
  pre-up ifconfig mon1 up
  pre-up iw dev mon1 set channel 36

---------
sudo vi /etc/udev/rules.d/10-network-device.rules 
SUBSYSTEM=="net", ACTION=="add", ATTR{address}=="00:0f:13:38:21:90", NAME="wlan0"

---------
nmap -sn 192.168.1.1/24

--------------------------
ssh

sudo vi /etc/hosts
sudo vi /etc/hostname

sudo apt-get update
sudo apt-get upgrade
(30 min)

----------------------------------------
Install OVERLAYROOT
----------------------------------------
use gparted to add user rw FAT32 partition at the end

sudo apt-get install -y overlayroot 
sudo vi /etc/overlayroot.conf
overlayroot="tmpfs"

sudo update-initramfs -u
sudo reboot


-----------------------------------------
-----------------------------------------
BOOT ON SD AND RUN FROM USB KEY
-----------------------------------------

sudo vi /etc/initramfs-tools/hooks/usb-firmware
"
if [ "$1" = "prereqs" ]; then exit 0; fi
. /usr/share/initramfs-tools/hook-functions
copy_file firmware /lib/firmware/tegra21x_xusb_firmware
"
sudo chmod a+x /etc/initramfs-tools/hooks/usb-firmware

sudo mkinitramfs -o /boot/initrd-xusb.img
lsinitramfs /boot/initrd-xusb.img | grep xusb
=> lib/firmware/tegra21x_xusb_firmware


sudo rsync -axHAWX --numeric-ids --info=progress2 --exclude=/proc / /dev/sda1
(9,9G 13 min)

sudo vi /boot/extlinux/extlinux.conf 
"
      INITRD /boot/initrd-xusb.img
      APPEND ${cbootargs} root=/dev/sda1 rootwait rootfstype=ext4
"

sudo reboot
df
=> 
pprz@jetson:~$ df
Filesystem     1K-blocks     Used Available Use% Mounted on
...
/dev/sda1       30638016 10403892  18654760  36% /
...
/dev/mmcblk0p1  30688172 10400704  18896184  36% /media/pprz/cf9d96ca-f7c4-45f5-9064-652345026106


-----------------------------------------
-----------------------------------------


----------------------------------------
GSTREAMER already installed test
----------------------------------------
Test 1
------
gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM), width=1280, height=720, framerate=30/1' ! omxh264enc ! video/x-h264, stream-format=byte-stream ! rtph264pay ! udpsink host=192.168.3.1 port=5000

gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false

Test 2
------
gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM), width=1280, height=720, framerate=30/1' ! omxh264enc ! video/x-h264,stream-format=byte-stream ! shmsink socket-path=/tmp/camera1 wait-for-connection=false sync=false

gst-launch-1.0 shmsrc socket-path=/tmp/camera1 do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay ! udpsink host=192.168.3.1 port=5000

gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false

Test 3 
------
gst-launch-1.0 nvarguscamerasrc ! video/x-raw(memory:NVMM),width=1280,height=720,framerate=30/1 ! tee name=streams ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! video/x-raw(memory:NVMM) ! nvvidconv flip_method=2 ! video/x-raw(memory:NVMM),format=I420 ! omxh264enc ! video/x-h264,stream-format=byte-stream,alignment=au ! shmsink socket-path=/tmp/camera1 wait-for-connection=false sync=false async=false streams. ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! nvvidconv flip_method=2 ! video/x-raw,format=I420 ! shmsink socket-path=/tmp/camera2 wait-for-connection=false sync=false async=false

gst-launch-1.0 shmsrc socket-path=/tmp/camera2 do-timestamp=true ! 'video/x-raw, width=(int)1280, height=(int)720, framerate=(fraction)30/1, format=(string)I420' ! omxh264enc ! 'video/x-h264, stream-format=(string)byte-stream' ! rtph264pay name=pay0 pt=96 config-interval=1 ! udpsink host=192.168.3.1 port=5000

gst-launch-1.0 shmsrc socket-path=/tmp/camera1 do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay ! udpsink host=192.168.3.1 port=5000

gst-launch-1.0 udpsrc port=5010 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false

----------------------------------------
GSTREAMER RTSP SERVER install anad test
----------------------------------------

sudo apt-get install libglib2.0 -y

gst-launch-1.0 --version
=> gst-launch-1.0 version 1.14.5

(ne pas faire d'installation via git !)
wget http://gstreamer.freedesktop.org/src/gst-rtsp-server/gst-rtsp-server-1.14.5.tar.xz
tar -xf gst-rtsp-server-1.14.5.tar.xz
rm gst-rtsp-server-1.14.5.tar.xz
cd gst-rtsp-server-1.14.5/
./configure
---------------- 
~/gst-rtsp-server-1.14.5/examples/test-launch.c 
patched with second stream 
  GstRTSPMediaFactory *factory2;
  factory2 = gst_rtsp_media_factory_new ();
  gst_rtsp_media_factory_set_launch (factory2, argv[2]);
  gst_rtsp_mount_points_add_factory (mounts, "/test2", factory2);
----------------
cd ~/gst-rtsp-server-1.14.5
make
sudo make install

-------------
Test
----
gst-launch-1.0 nvarguscamerasrc ! video/x-raw(memory:NVMM),width=1280,height=720,framerate=30/1 ! tee name=streams ! video/x-raw(memory:NVMM) ! nvvidconv flip_method=2 ! video/x-raw(memory:NVMM),format=I420 ! omxh264enc ! video/x-h264,stream-format=byte-stream,alignment=au ! shmsink socket-path=/tmp/camera1 wait-for-connection=false sync=false async=false streams. ! nvvidconv flip_method=2 ! video/x-raw,format=I420 ! shmsink socket-path=/tmp/camera2 wait-for-connection=false sync=false async=false

gst-rtsp-server-1.14.5/examples/test-launch "shmsrc socket-path=/tmp/camera1 do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay name=pay0 pt=96 config-interval=1" "shmsrc socket-path=/tmp/camera2 do-timestamp=true ! video/x-raw, width=1280, height=720, framerate=30/1, format=I420 ! omxh264enc ! video/x-h264, stream-format=byte-stream ! rtph264pay name=pay0 pt=96 config-interval=1"

client:
gst-launch-1.0 rtspsrc location=rtsp://192.168.3.2:8554/test ! rtph264depay ! avdec_h264 !  xvimagesink sync=false
and
gst-launch-1.0 rtspsrc location=rtsp://192.168.3.2:8554/test2 ! rtph264depay ! avdec_h264 !  xvimagesink sync=false


----------------------------------------
OPENCV already installed test
----------------------------------------

                       | --> camera1 (x-h264) 
 raspivid (x-h264) --> |   
                       | omxh264dec --> camera2 (x-raw,I420) 
	                                  |
	                                  | --> VideoCapture (yuv) VideoWriter --> camera3 (x-raw,I420)

g++ -g test.cpp -o test `pkg-config --cflags --libs opencv4` 
rm /tmp/camera3;./test

#include <opencv2/opencv.hpp>
#define WIDTH 640
#define HEIGHT 480
#define FPS 30
#define SCALE 3/2
using namespace cv;
using namespace std;

int main(int, char**)
{
  unsigned int dataSize = sizeof(unsigned char)*WIDTH*HEIGHT*SCALE;
  Mat imageIn(WIDTH*SCALE, HEIGHT, CV_8UC1);
  Mat imageOut(WIDTH,HEIGHT,CV_8UC3,Scalar(0,0,0));

  cout << getBuildInformation() << endl;

  string streamInGstStr="shmsrc socket-path=/tmp/camera2 ! video/x-raw,width="+to_string(WIDTH)+
   ",height="+to_string(HEIGHT)+",framerate="+to_string(FPS)+"/1,format=I420 ! appsink sync=true";
  string streamOutGstStr="appsrc ! shmsink socket-path=/tmp/camera3 wait-for-connection=false async=false sync=false";

  VideoCapture streamIn(streamInGstStr,CAP_GSTREAMER);
  VideoWriter  streamOut(streamOutGstStr,0,FPS/1,Size(WIDTH,HEIGHT),true);

  if (streamIn.isOpened() && streamOut.isOpened()) {
    while (true) {
      streamIn.read(imageIn);
      if (!imageIn.empty()) {
        memcpy(imageOut.data,imageIn.data,dataSize);
        streamOut.write(imageOut);
      }
    }
  }
  return 0;
}

----------------------------------------
python2
import cv2
cv2.__version__
=>'4.1.1'


--------------------------
TODO: nvvidconv ! 'video/x-raw(memory:NVMM),format=RGBA'

----------------------------------------
WIFIBROADCAST install anad test
----------------------------------------
sudo apt-get install socat

sudo apt-get install libpcap-dev libsodium-dev
git clone https://github.com/svpcom/wifibroadcast
mv wifibroadcast wifibroadcast-svpcom 
cd wifibroadcast-svpcom
make
(/bin/sh: 1: trial: not found
make: *** [Makefile:43: test] Error 127
)

copy drone.key and gs.key


--------------------------
(git clone https://github.com/aircrack-ng/rtl8812au)
git clone https://github.com/svpcom/rtl8812au.git

sudo apt install dkms

cd rtl8812au
sudo ./dkms-install.sh

/*
vi include/autoconf.h
#define CONFIG_USE_EXTERNAL_POWER 
*/

sudo dkms status
=> rtl8812au, 5.2.20.2, 4.9.140-tegra, aarch64: installed
(sudo dkms remove rtl8812au/5.2.20.2 --all)





----------------------------------------
Configure autostart
----------------------------------------
sudo vi /etc/systemd/system/jetson_cam.service
[Unit]
Description=JetsonCam
After=nvargus-daemon.service


[Service]
Type=forking
ExecStart=/usr/bin/env /home/pprz/jetson_cam.sh
User=pprz


[Install]
WantedBy=multi-user.target

----------------------------------------
sudo vi /etc/systemd/system/jetson_svpcom.service
[Unit]
Description=JetsonSvpcom
After=NetworkManager.service


[Service]
Type=forking
ExecStart=/usr/bin/env /home/pprz/jetson_svpcom.sh
User=root


[Install]
WantedBy=multi-user.target

--------------------------
sudo systemctl daemon-reload

sudo systemctl start jetson_svpcom
sudo systemctl start jetson_cam
sudo systemctl stop jetson_cam
sudo systemctl status jetson_cam

sudo systemctl enable jetson_cam
sudo systemctl enable jetson_svpcom

sudo systemctl disable jetson_cam
systemctl list-units --type=service


--------------------------
--------------------------
sudo iw list

------
RT5572
(20 dBm max)
* 5180 MHz [36] (20.0 dBm) (no IR)
* 5500 MHz [100] (20.0 dBm) (no IR, radar detection)
* 5660 MHz [132] (20.0 dBm) (no IR, radar detection)

---------
RTL8812AU AC-1200
(27 dBm max)
* 5180 MHz [36] (20.0 dBm)
* 5500 MHz [100] (27.0 dBm) (no IR, radar detection)
* 5660 MHz [132] (27.0 dBm) (no IR, radar detection)

---------
RTL8812AU AC-1200 AWUS036ACH
(26 dBm max)
* 5180 MHz [36] (20.0 dBm)
* 5500 MHz [100] (26.0 dBm) (no IR, radar detection)
* 5660 MHz [132] (26.0 dBm) (no IR, radar detection)

------
sudo iw reg get
country DE: DFS-ETSI
(5150 - 5250 @ 80), (N/A, 20), (N/A), NO-OUTDOOR, AUTO-BW
...
(5470 - 5725 @ 160), (N/A, 26), (0 ms), DFS


------
sudo iw reg set RU
sudo iw reg get
  country RU: DFS-ETSI
  (5170 - 5250 @ 80), (N/A, 20), (N/A), AUTO-BW
  ...
  (5650 - 5730 @ 80), (N/A, 30), (0 ms), DFS


--------------------------
sudo ifconfig wlan0 down
sudo iwconfig wlan0 mode monitor
sudo ifconfig wlan0 up
sudo iwconfig wlan0 channel 36

------
sudo ifconfig wlan0 down
sudo iw dev wlan0 set monitor otherbss
sudo iw reg set DE
sudo ifconfig wlan0 up
sudo iw dev wlan0 set channel 36
sudo iw wlan0 info




