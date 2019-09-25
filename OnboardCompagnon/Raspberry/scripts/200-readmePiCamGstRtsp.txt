-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
PI ZERO V1.3 (Wifi + CSI camera v2.1 8 MP 1080p)

Camera H264 encoded stream
Hardware (GPU) H264 decoding / encoding

RTS Server providing H264 streams :
- direct from camera
- decoded / encoded 

+23% CPU with two clients connected
 
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
Install Rasbian on SD
---------------------
lsblk

unzip -p 2018-10-09-raspbian-stretch-lite.zip | sudo dd of=/dev/mmcblk0 bs=4M status=progress conv=fsync
sync

Plug/unplug SD

sudo touch /media/pprz/boot/ssh

sudo vi /media/pprz/boot/wpa_supplicant.conf
"
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=FR

network={
  ssid="Androidxp"
  psk="pprzpprz"
}
network={
  ssid="router_pprz"
  key_mgmt=NONE
}
"

-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
Configure Rasbian on SD
-----------------------
Boot/log
nmap -sn 192.168.43.0/24

ssh pi@192.168.1.x
password "raspberry"

sudo raspi-config
1) change user password
7) advanced options
  A1) expand filesystem
  P1) Camera Enable

Reboot !

ssh pi@192.168.1.x
password "pprz"

sudo vi /etc/dphys-swapfile 
CONF_SWAPSIZE=1024

sudo reboot

top
check swap

-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
Install Gstreamer
-----------------
Check 
sudo apt-get update
sudo apt-get install gstreamer1.0-tools
sudo apt-get install gstreamer1.0-plugins-bad
sudo apt-get install gstreamer1.0-plugins-good


Usage 1) with Raspivid application
----------------------------------
raspivid -t 0 -w 640 -h 480 -o - | gst-launch-1.0 fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.43.181 port=5000

gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false


Usage 2) with v4l2 interface 
----------------------------
sudo modprobe bcm2835-v4l2

gst-launch-1.0 -v v4l2src device=/dev/video0 ! video/x-raw,width=640,height=500,framerate=20/1 ! omxh264enc ! rtph264pay ! udpsink host=192.168.43.181 port=5000

idem client


Usage 3) with rpicamsrc interface: The FASTEST !
--------------------------------------------
sudo apt-get install dh-autoreconf
sudo apt-get install libgstreamer1.0-dev and libgstreamer-plugins-base1.0-dev
sudo apt-get install gstreamer1.0-libav gstreamer1.0-omx


sudo apt-get install git
git clone https://github.com/thaytan/gst-rpicamsrc.git
cd gst-rpicamsrc
./autogen.sh
make
sudo make install

gst-launch-1.0 rpicamsrc bitrate=10000000 ! video/x-raw,width=640,height=480,framerate=20/1 ! omxh264enc ! rtph264pay ! udpsink host=192.168.43.181 port=5000
or
gst-launch-1.0 rpicamsrc bitrate=10000000 ! video/x-raw,width=640,height=480,framerate=20/1 ! omxh264enc ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.43.181 port=5000
or from camera encoded stream
gst-launch-1.0 rpicamsrc bitrate=10000000 ! video/x-h264,width=640,height=480,framerate=25/1,profile=high ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.43.181 port=5000

same client


-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
Install RTSP Server
-------------------
sudo apt-get install libgstreamer-plugins-bad1.0-dev
//sudo apt-get install libglib2.0-dev

gst-launch-1.0 --version
=> gst-launch-1.0 version 1.10.4

wget http://gstreamer.freedesktop.org/src/gst-rtsp-server/gst-rtsp-server-1.10.4.tar.xz
tar -xf gst-rtsp-server-1.10.4.tar.xz 
rm gst-rtsp-server-1.10.4.tar.xz
cd gst-rtsp-server-1.10.4/
./configure

=> configure: No package 'gstreamer-plugins-good-1.0' found
OK

make
sudo make install


~/gst-rtsp-server-1.10.4/examples/test-launch "(rpicamsrc bitrate=1000000 ! video/x-h264,width=640,height=480,framerate=15/1 ! rtph264pay config-interval=1 name=pay0 pt=96 )"
stream ready at rtsp://127.0.0.1:8554/test
=> 3.6% CPU with one client connected

gst-launch-1.0 rtspsrc location=rtsp://192.168.43.116:8554/test ! rtph264depay ! avdec_h264 !  xvimagesink sync=false

 
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
Organize pipelines
------------------

                        | --> camera1 (x-h264) 
 rpicamsrc (x-h264) --> |   
                        | omxh264dec --> camera2 (x-raw,I420) 

gst-launch-1.0 rpicamsrc bitrate=1000000 vflip=true ! \
	video/x-h264,width=640,height=480,framerate=15/1 ! \
	h264parse config-interval=1 ! \
	tee name=streams ! \
	queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! \
	omxh264dec ! \
	shmsink socket-path=/tmp/camera2 wait-for-connection=false sync=false streams. ! \
	queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! \
	shmsink socket-path=/tmp/camera1 wait-for-connection=false sync=false
=> +9.0% CPU

gst-rtsp-server-1.10.4/examples/test-launch \
  "( shmsrc socket-path=/tmp/camera1 do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay config-interval=1 name=pay0 pt=96 )"
=> +2.6% CPU with one client connected

gst-launch-1.0 rtspsrc location=rtsp://192.168.43.116:8554/test ! rtph264depay ! avdec_h264 !  xvimagesink sync=false


-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
Patch RTSP server for 2 streams
-------------------------------

~/gst-rtsp-server-1.10.4/examples/test-launch.c 
patched with second stream 
  GstRTSPMediaFactory *factory2;
  factory2 = gst_rtsp_media_factory_new ();
  gst_rtsp_media_factory_set_launch (factory2, argv[2]);
  gst_rtsp_mount_points_add_factory (mounts, "/test2", factory2);
make


gst-launch-1.0 rpicamsrc ...
=> +9.0% CPU

gst-rtsp-server-1.10.4/examples/test-launch \
  "( shmsrc socket-path=/tmp/camera1 do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay config-interval=1 name=pay0 pt=96 )" \
  "( shmsrc socket-path=/tmp/camera2 do-timestamp=true is-live=true ! video/x-raw,format=I420,width=640,height=480,framerate=15/1 ! omxh264enc ! video/x-h264,profile=high ! rtph264pay name=pay0 pt=96 config-interval=1 )" 

gst-launch-1.0 rtspsrc location=rtsp://192.168.43.116:8554/test ! rtph264depay ! avdec_h264 !  xvimagesink sync=false
=> +2.6% CPU
gst-launch-1.0 rtspsrc location=rtsp://192.168.43.116:8554/test2 ! rtph264depay ! avdec_h264 !  xvimagesink sync=false
=> +7.5% CPU
=> +10% CPU





