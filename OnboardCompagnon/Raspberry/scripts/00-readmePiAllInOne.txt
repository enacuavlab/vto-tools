Raspberry Zero or PI3
(opencv compilation on PI3 = 2hours, not even try on PI0)

Wifibroadcast work tested with 
Ralink RT5572
Realtek RTL8812AU (RTL8812BU not working driver)

----------------------------------------------------------------------------------------------------
unzip -p raspbian_lite_latest | sudo dd of=/dev/sdxx bs=4M status=progress conv=fsync
(2019-09-26-raspbian-buster-lite.zip)
sync

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
7) advanced options
  A1) expand filesystem
Enable Camera
  
sudo vi /etc/dphys-swapfile 
CONF_SWAPSIZE=1024

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
sudo apt-get install gstreamer1.0-tools
sudo apt-get install gstreamer1.0-plugins-bad
sudo apt-get install gstreamer1.0-plugins-good

sudo apt-get install gstreamer1.0-omx

sudo apt-get install libgstreamer-plugins-bad1.0-dev

gst-launch-1.0 --version
=> gst-launch-1.0 version 1.10.4
=> gst-launch-1.0 version 1.14.4

wget http://gstreamer.freedesktop.org/src/gst-rtsp-server/gst-rtsp-server-1.14.4.tar.xz
tar xf gst-rtsp-server-1.14.4.tar.xz 
rm gst-rtsp-server-1.14.4.tar.xz
cd gst-rtsp-server-1.14.4/
./configure


make
sudo make install

----------------------------------------------------------------------------------------------------
sudo apt-get install cmake
sudo apt-get install -y python-numpy python3-numpy libpython-dev libpython3-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libtiff-dev zlib1g-dev libjpeg-dev libpng-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev

sudo apt-get install git
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git
cd opencv 
git checkout 4.1.0
cd opencv_contrib
git checkout 4.1.0

mkdir opencv/build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
    -D BUILD_TESTS=OFF \
    -D BUILD_PERF_TESTS=OFF \
    -D BUILD_EXAMPLES=OFF ..

make -j4
and for link 
make
(1 hour)
sudo make install
sudo ldconfig -v

Get source and compile in /home/pi/opencv_trials/cpp
~/Projects/vto-tools/OnboardCompagnon/Raspberry/scripts/Material/
airpicv.cpp 
or 
groundpicv.cpp

----------------------------------------------------------------------------------------------------
sudo apt-get install libpcap-dev libsodium-dev
git clone https://github.com/svpcom/wifibroadcast
mv wifibroadcast wifibroadcast-svpcom 
cd wifibroadcast-svpcom
make

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

cd /etc/wpa_supplicant
sudo mw wpa_supplicant.conf wpa_supplicant-wlan0.conf

Put shell in /home/pi
~/Projects/vto-tools/OnboardCompagnon/Raspberry/scripts/Material/
airpi-svpcom.sh
or 
groundpi-svpcom.sh groundpi-joystick.sh

----------------------------------------------------------------------------------------------------
sudo apt-get install python-pip
sudo apt-get install python3-pip

sudo pip install future twisted pyroute2
sudo pip3 install future twisted pyroute2

sudo apt-get install socat

sudo apt-get install udptunnel
sudo apt install dnsutils

/etc/ssh/sshd_config
PermitTunnel yes
sudo reboot

----------------------------------------------------------------------------------------------------
for airborne get proxy.zip 
unzip proxy
rm proxy.zip

bridge.c
//  strcpy(arg.netipdest,"192.168.1.255");
  strcpy(arg.netipdest,"127.0.0.1");

make

----------------------------------------------------------------------------------------------------
use gparted to add user rw FAT32 partition 
/etc/fstab
...
PARTUUID=...-03  /data           vfat    nofail,umask=0000 0       0

git clone https://github.com/marklister/overlayRoot.git
cd overlayRoot
sudo bash install

/etc/overlayRoot.conf
/etc/fstab

sudo dphys-swapfile swapoff
sudo dphys-swapfile uninstall
sudo update-rc.d dphys-swapfile remove


sudo mount -o remount,rw /ro
sudo chroot /ro
...
exit


/boot/cmdline.txt
... init=/sbin/overlayRoot.sh

init=...
init=/sbin/overlayRoot.sh

