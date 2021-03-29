Get Jetson Nano Developer Kit - JETPACK 4.51
https://developer.nvidia.com/jetson-nano-sd-card-image

jetson-nano-jp451-sd-card-image.zip 
6.4Gb
 
Etcher: flash SD (30 min)
Plug not modified SD
Do not plug Ethernet nor Wifi adapter
First setup needs : Monitor, keyboard, mouse
Boot and set minimal configuration with desktop
Configure ethernet
        iface eth0 inet static
        address 192.168.3.2
        netmask 255.255.255.0
        gateway 192.168.3.1
        dns-nameservers 8.8.8.8
Power off

----------------------------------------
CONFIGURE 
----------------------------------------
Ubuntu
sudo sysctl net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -o wlp59s0 -j MASQUERADE

ssh pprz@192.168.3.2

sudo rm /var/lib/apt/lists/lock
sudo apt-get update
sudo apt-get upgrade
(10 min)

----------------------------------------
proceed installation for rtl8812au and wifibroadcast 
mkdir ~/Projects
cd ~/Projects
git clone --recurse-submodules https://github.com/enacuavlab/compagnon-software.git

----------------------------------------
NVIDIA P3448/3449-A02 (Single CSI port)

wget https://cdn.alliedvision.com/fileadmin/content/software/software/embedded/AlliedVision_NVidia_nano_L4T_32.4.4_4.9.140-gf9e822728.tar.gz

tar -xzf AlliedVision_NVidia_nano_L4T_32.4.4_4.9.140-gf9e822728.tar.gz 

sudo cp -r Image /boot/avt_Image
sudo cp tegra210-p3448-0000-p3449-0000-a02.dtb /boot/avt_tegra210-p3448-0000-p3449-0000-a02.dtb
sudo tar zxf modules.tar.gz -C /

sudo vi /boot/extlinux/extlinux.conf
      LINUX /boot/avt_Image
      FDT /boot/avt_tegra210-p3448-0000-p3449-0000-a02.dtb
      #LINUX /boot/Image
      #FDT /boot/tegra210-p3448-0000-p3449-0000-b00.dtb

(dtc -I fs -O dts -o extracted.dts /proc/device-tree)

=> 4.9.140-gf9e822728
=> 4.9.201-tegra

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










