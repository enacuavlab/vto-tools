Raspberry Zero or PI3
(opencv compilation on PI3 = 2hours, not even try on PI0)

Wifibroadcast work tested with 
OK: Bus 001 Device 004: ID 148f:5572 Ralink Technology, Corp. RT5572 Wireless Adapter
OK: Bus 001 Device 004: ID 0bda:8812 Realtek Semiconductor Corp. RTL8812AU 802.11a/b/g/n/ac 2T2R DB WLAN Adapter
KO: RTL8812BU Not working

----------------------------------------------------------------------------------------------------
Backup

dd bs=512 count=1 if=/dev/sde of=raspogee/mbr.img
sync

umount /media/pprz/boot
sudo partclone.fat --clone --source /dev/sde1 --output - | bzip2 -9 > raspogee/boot.img
umount /media/pprz/rootfs
sudo partclone.extfs --clone --source /dev/sde2 --output - | bzip2 -9 > raspogee/system.img


Restore

dd bs=512 count=1 of=/dev/sde if=raspogee/mbr.img
sync
sudo partprobe

umount /media/pprz/*
sudo bunzip2 -c raspogee/boot.img | sudo partclone.vfat --restore --source - --output /dev/sde1
sudo bunzip2 -c raspogee/system.img | sudo partclone.extfs --restore --source - --output /dev/sde2

Syncing... 
several minutes

----------------------------------------------------------------------------------------------------

(2019-09-26-raspbian-buster-lite.zip)
sync

plugout/plugin 
cd /media/pprz/

Create file
boot/ssh

Create file with following content
boot/wpa_supplicant.conf
"
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=FR

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
"

nmap -sn 192.168.1.0/24

ssh pi@192.168.1.x
password "raspberry"

sudo raspi-config
1) change user password
5)P8) enable camera
7) advanced options
  A1) expand filesystem
Enable Camera
  
#sudo vi /etc/dphys-swapfile 
#CONF_SWAPSIZE=1024

/etc/hosts
127.0.1.1       raspberrypi
to 127.0.1.1       airpi or groundpi

/etc/hostname
raspberrypi to airpi or groundpi

----------------------------------------------------------------------------------------------------
sudo systemctl stop serial-getty@ttyAMA0.service
sudo systemctl disable serial-getty@ttyAMA0.service

sudo vi /boot/cmdline.txt
dwc_otg.lpm_enable=0 console=serial0,115200 console=tty1 root=PARTUUID=dc6114e5-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait fastboot noswap ro
remove
console=serial0,115200

sudo vi /boot/config.txt
add
enable_uart=1

sudo vi /boot/config.txt
add
dtoverlay=pi3-disable-bt

sudo systemctl stop hciuart
sudo systemctl disable hciuart

----------------------------------------------------------------------------------------------------
sudo apt-get update
sudo apt-get upgrade
(20 minutes)

sudo apt-get install gstreamer1.0-plugins-base -y
sudo apt-get install gstreamer1.0-plugins-good -y
sudo apt-get install gstreamer1.0-plugins-bad -y
sudo apt-get install gstreamer1.0-plugins-ugly -y
sudo apt-get install gstreamer1.0-libav -y
sudo apt-get install gstreamer1.0-omx -y
sudo apt-get install gstreamer1.0-tools -y

------------------
(check installation with Material/cam.sh)
Do not install rpicamsrc but use raspivid !


                       | --> camera1 (x-h264) 
 raspivid (x-h264) --> |   
                       | omxh264dec --> camera2 (x-raw,I420) 


raspivid -t 0 -w 640 -h 480 -fps 30/1 -b 3000000 -g 5 -vf -hf -cd H264 -n -fl -ih -o - | gst-launch-1.0 fdsrc ! h264parse ! video/x-h264,stream-format=byte-stream ! tee name=streams ! omxh264dec ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! shmsink socket-path=/tmp/camera2 wait-for-connection=false sync=false streams. ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! shmsink socket-path=/tmp/camera1 wait-for-connection=false sync=false

gst-launch-1.0 shmsrc socket-path=/tmp/camera1 do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay name=pay0 pt=96 config-interval=1 ! udpsink host=192.168.1.46 port=5000
and
gst-launch-1.0 shmsrc socket-path=/tmp/camera2 do-timestamp=true is-live=true ! video/x-raw,format=I420,width=640,height=480,framerate=15/1 ! omxh264enc ! video/x-h264,profile=high ! rtph264pay name=pay0 pt=96 config-interval=1 ! udpsink host=192.168.1.46 port=5000

client:
gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false


------------------
sudo vi /etc/dphys-swapfile
CONF_SWAPSIZE=2048
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start
sudo apt-get install libglib2.0 -y
sudo apt-get install libgstreamer1.0-dev -y
sudo apt-get install libgstreamer-plugins-base1.0-dev -y

gst-launch-1.0 --version
=> gst-launch-1.0 version 1.14.4

(ne pas faire d'installation via git !)
wget http://gstreamer.freedesktop.org/src/gst-rtsp-server/gst-rtsp-server-1.14.4.tar.xz
tar -xf gst-rtsp-server-1.14.4.tar.xz
rm gst-rtsp-server-1.14.4.tar.xz
cd gst-rtsp-server-1.14.4/
./configure
---------------- 
~/gst-rtsp-server-1.14.4/examples/test-launch.c 
patched with second stream 
  GstRTSPMediaFactory *factory2;
  factory2 = gst_rtsp_media_factory_new ();
  gst_rtsp_media_factory_set_launch (factory2, argv[2]);
  gst_rtsp_mount_points_add_factory (mounts, "/test2", factory2);
----------------
cd ~/gst-rtsp-server-1.14.4
make
sudo make install

-------------
(check installation with Material/cam.sh)

raspivid -t 0 -w 640 -h 480 -fps 30/1 -b 3000000 -g 5 -vf -hf -cd H264 -n -fl -ih -o - | gst-launch-1.0 fdsrc ! h264parse ! video/x-h264,stream-format=byte-stream ! tee name=streams ! omxh264dec ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! shmsink socket-path=/tmp/camera2 wait-for-connection=false sync=false streams. ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! shmsink socket-path=/tmp/camera1 wait-for-connection=false sync=false

gst-rtsp-server-1.14.4/examples/test-launch "shmsrc socket-path=/tmp/camera1 do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay name=pay0 pt=96 config-interval=1" "shmsrc socket-path=/tmp/camera2 do-timestamp=true ! video/x-raw, format=I420, width=640, height=480, framerate=30/1 ! omxh264enc ! video/x-h264,profile=high  ! rtph264pay name=pay0 pt=96 config-interval=1"

client:
gst-launch-1.0 rtspsrc location=rtsp://192.168.1.96:8554/test ! rtph264depay ! avdec_h264 !  xvimagesink sync=false
and
gst-launch-1.0 rtspsrc location=rtsp://192.168.1.96:8554/test2 ! rtph264depay ! avdec_h264 !  xvimagesink sync=false

----------------------------------------------------------------------------------------------------
sudo apt-get install -y cmake
sudo apt-get install -y python-numpy python3-numpy libpython-dev libpython3-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libtiff-dev zlib1g-dev libjpeg-dev libpng-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev

(sudo apt-get install libgtk2.0-dev)

sudo apt-get install -y git
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git
cd ~/opencv 
git checkout 4.1.0
cd ~/opencv_contrib
git checkout 4.1.0

mkdir ~/opencv/build
cd ~/opencv/build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
    -D OPENCV_GENERATE_PKGCONFIG=YES \
    -D BUILD_TESTS=OFF \
    -D BUILD_PERF_TESTS=OFF \
    -D BUILD_EXAMPLES=OFF ..

=>  GStreamer:                   YES (1.14.4)

sudo vi /etc/dphys-swapfile
CONF_SWAPSIZE=2048
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start

make -j4
(more than 4 hours on PI3)
(make &)
sudo make install
sudo ldconfig -v

----------
Check installation

python3
import cv2
cv2.__version__
=> '4.1.0'

-------
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

----------------------------------------------------------------------------------------------------
Put /home/pi/cam.sh from Material

/etc/rc.local
su root -c /home/pi/cam.sh &

----------------------------------------------------------------------------------------------------
    <module name="telemetry" type="transparent">
      <configure name="MODEM_PORT" value="UART3"/>
      <configure name="MODEM_BAUD" value="B115200"/>
    </module>
or 
    <module name="extra_dl">
      <configure name="EXTRA_DL_PORT" value="UART3"/>
      <configure name="EXTRA_DL_BAUD" value="B115200"/>
    </module>

    <process name="Extra">
      <mode name="default">
        <message name="AUTOPILOT_VERSION"        period="11.1"/>
        <message name="DL_VALUE"                 period="1.1"/>
        ....     
      </mode>
    </process>


git clone https://github.com/paparazzi/pprzlink.git

mkdir ~/pprzlink_test;cd pprzlink_test

/home/pi/pprzlink/tools/generator/gen_messages.py --protocol 2.0 --lang C_standalone --no-validate -o pprzlink/my_pprz_messages.h /home/pi/pprzlink/message_definitions/v1.0/messages.xml telemetry --opt ALIVE,GPS,IMU_ACCEL_SCALED,IMU_GYRO_SCALED,AIR_DATA,ACTUATORS

get pprz_uart_out.c from Material, compile and run

cam_rec.sh  gst-rtsp-server-1.14.4  opencv  opencv_contrib  pprzlink  pprzlink_test  proxy.tar  test

--------------------------------------
for airborne get proxy.zip 
unzip proxy
rm proxy.zip

bridge.c
//  strcpy(arg.netipdest,"192.168.1.255");
  strcpy(arg.netipdest,"127.0.0.1");

make

----------------------------------------------------------------------------------------------------
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

cd /opt/vc/src/hello_pi/libs/ilclient
make
cd
git clone https://github.com/svpcom/wifibroadcast_osd.git
cd wifibroadcast_osd/fpv_video
make

/etc/rc.local
su root -c /home/pi/groundpi-svpcom.sh &
or
su root -c /home/pi/airpi-svpcom.sh &



Put shell in /home/pi
~/Projects/vto-tools/OnboardCompagnon/Raspberry/scripts/Material/
airpi-svpcom.sh
or 
groundpi-svpcom.sh groundpi-joystick.sh


------------------------------
cat /etc/os-release 
PRETTY_NAME="Raspbian GNU/Linux 10 (buster)"

(git clone https://github.com/aircrack-ng/rtl8812au)
git clone https://github.com/svpcom/rtl8812au.git

sudo apt install dkms
(10 minutes)

cd rtl8812au
sed -i 's/CONFIG_PLATFORM_I386_PC = y/CONFIG_PLATFORM_I386_PC = n/g' Makefile
sed -i 's/CONFIG_PLATFORM_ARM64_RPI = n/CONFIG_PLATFORM_ARM64_RPI = y/g' Makefile
sed -i 's/^dkms build/ARCH=arm dkms build/' dkms-install.sh
sed -i 's/^MAKE="/MAKE="ARCH=arm\ /' dkms.conf
sudo ./dkms-install.sh
(10 minutes)

?
vi include/rtl_autoconf.h
#define CONFIG_USE_EXTERNAL_POWER 
?
sudo dkms status
=> rtl8812au, 5.6.4.2, 4.19.75-v7+, armv7l: installed
(sudo dkms remove rtl8812au/5.6.4.2 --all)

------------------------------
sudo mv /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant-wlan0.conf

sudo vi /etc/dhcpcd.conf
denyinterfaces wlan1

??????????????
sudo vi /etc/udev/rules.d/76-netnames.rules
SUBSYSTEM=="net", ACTION=="add", ATTR{address}=="b8:27:eb:be:ba:55", NAME="wlan0"
SUBSYSTEM=="net", ACTION=="add", ATTR{address}=="00:13:ef:f2:18:98", NAME="wlan1"
(update with suitable mac address)


???????????????

----------------------------------------------------------------------------------------------------
Shutdown Pin5(GPIO3) to Ground
PowerOff / PowerOn

/boot/config.txt
dtoverlay=gpio-shutdown

----------------------------------------------------------------------------------------------------
use gparted to add user rw FAT32 partition 

/etc/fstab
...
PARTUUID=...-03  /data           vfat    nofail,umask=0000 0       0

git clone https://github.com/marklister/overlayRoot.git
cd overlayRoot
sudo bash install

check
/etc/overlayRoot.conf
/etc/fstab

sudo dphys-swapfile swapoff
sudo dphys-swapfile uninstall
sudo update-rc.d dphys-swapfile remove

reboot
sudo mount -o remount,rw /ro
sudo chroot /ro
...
exit
 
or remove init=/sbin/overlayRoot.sh 
from /boot/cmdline.txt

----------------------------------------------------------------------------------------------------
Give access to storage via USB 
(with previously created fat32 partition /dev/mmcblk0p3 before)

PI zero can be access with single USB (power + data)

/boot/config.txt
dtoverlay=dwc2

/etc/modules
dwc2
reboot

/etc/rc.local
modprobe g_mass_storage file=/dev/mmcblk0p3 &


# Monitor and kill if usb connection is detected
tail -F /var/log/syslog | grep --line-buffered 'g_mass_storage gadget: high-speed config' | while read;do kill `ps -ef | grep gst-launch-1.0 | grep filesink | awk '{print $2}'`;done &

# Do not launch if USB is connected  
dmesg | grep -q 'g_mass_storage gadget: high-speed config' | gst-launch-1.0 -e shmsrc socket-path=/tmp/camera1 do-timestamp=true ! h264parse ! matroskamux ! filesink location=/data/file0.mkv &





