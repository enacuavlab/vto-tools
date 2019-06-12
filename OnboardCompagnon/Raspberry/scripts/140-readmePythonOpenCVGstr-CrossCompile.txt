https://github.com/opencv/opencv/wiki/Intel%27s-Deep-Learning-Inference-Engine-backend
https://solarianprogrammer.com/2018/12/18/cross-compile-opencv-raspberry-pi-raspbian/

-------------------------------------------------------------------------------------
Raspbian "armhf": ARMv6 + VFPv2 (PI I, PI ZERO)
deb http://archive.raspbian.org/raspbian stretch main contrib non-free
deb-src http://archive.raspbian.org/raspbian stretch main contrib non-free

Debian "armhf": ARMv7 
deb http://deb.debian.org/debian stretch main
deb-src http://deb.debian.org/debian stretch main

-------------------------------------------------------------------------------------
RPI
-------------------------------------------------------------------------------------
From fresh installed raspbian strech lite (10 minutes)
 
python 
=> Python 2.7.13 (default, Sep 26 2018, 18:42:22) 
python3
=> Python 3.5.3 (default, Sep 27 2018, 17:25:39) 


sudo apt-get update

sudo -s
#!/bin/sh
apt-get install -y --no-install-recommends \
  python-numpy \
  python3-numpy \
  libpython-dev \
  libpython3-dev \
  libgstreamer1.0-dev \
  libgstreamer-plugins-base1.0-dev \
  libtiff-dev \
  zlib1g-dev \
  libjpeg-dev \
  libpng-dev \
  libavcodec-dev \
  libavformat-dev \
  libswscale-dev \
  libv4l-dev \
  libxvidcore-dev \
  libx264-dev


-------------------------------------------------------------------------------------
HOST 
-------------------------------------------------------------------------------------
Build VM from debian netinst iso
Install minimal configuration with user root and pprz
(unset "environnement de bureau Debian","serveur d'impression","utilitaires usuels du système")

Edit virtual machine settings 
- DD 15Gb 
- / Hardware Memory 2Gb
- / Options / VmWare Tools Updates / Update manually

-------------------------------------------------------------------------------------
logging root
apt-get install fuse
mkdir /mnt/tools
mount /dev/cdrom /mnt/tools
cp /mnt/tools/VMwareTools-10.2.5-8068393.tar.gz .

gunzip
tar xvf
./vmware-tools-distrib/vmware-install.pl


Virtual Machine Setting / Options / SharedFolder
ls /mnt/hgfs/...

-------------------------------------------------------------------------------------
apt-get install sudo
adduser pprz sudo

sudo dd if=/dev/zero of=/swapfile1 bs=1G count=1
sudo chmod 600 /swapfile1
sudo mkswap /swapfile1
sudo swapon /swapfile1
sudo vi /etc/fstab
/swapfile1  swap  swap  defaults  0 0

reboot
sudo swapon --show

-------------------------------------------------------------------------------------
Poweroff PI and plug its SD to host with an USB adapter

sudo mkdir /media/rootfs
sudo mount /dev/sdb2 /media/rootfs
ls /media/pprz/rootfs

mkdir /home/pprz/rootfs /home/pprz/rootfs/usr
cp -R /media/rootfs/lib /home/pprz/rootfs
cp -R /media/rootfs/usr/lib /home/pprz/rootfs/usr
cp -R /media/rootfs/usr/include /home/pprz/rootfs/usr
cp -R /media/rootfs/usr/local /home/pprz/rootfs/usr
(du -sh /home/pprz/rootfs => 708M)

cd /home/pprz/rootfs
find . -lname "/lib/*" -exec sh -c 'ln -snf "/home/pprz/rootfs$(readlink "$0")" "$0"' {} \;

-------------------------------------------------------------------------------------

get https://github.com/raspberrypi/tools
and unzip tools-master.zip on host (361,4M)

.bashrc
export PATH=$HOME/tools-master/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian-x64/bin:$PATH
(running a 64 bit VM, ubuntu compiler comming second if it is in the distrib)

loggin / logout / loggin
arm-linux-gnueabihf-gcc -v
=> gcc version 4.8.3 20140303 (prerelease) (crosstool-NG linaro-1.13.1+bzr2650 - Linaro GCC 2014.03) 

-------------------------------------------------------------------------------------
https://github.com/opencv/opencv/archive/4.1.0.tar.gz
opencv-4.1.0.tar.gz (88,2M)

-------------------------------------------------------------------------------------

sudo -s
#!/bin/sh
ap-get install -y pkg-config cmake
ap-get install -y python python3
(check same version with RPIs)


-------------------------------------------------------------------------------------
#!/bin/bash
cd ~/opencv-4.1.0 && mkdir opencv_build && cd opencv_build
export PKG_CONFIG_SYSROOT_DIR=/home/pprz/rootfs
export PKG_CONFIG_LIBDIR=/home/pprz/rootfs/usr/lib/arm-linux-gnueabihf/pkgconfig:/home/pprz/rootfs/usr/lib/pkgconfig
cmake -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_SYSROOT="/home/pprz/rootfs" \
      -DCMAKE_INSTALL_PREFIX="/opt/opencv-4.1.0" \
      -DCMAKE_TOOLCHAIN_FILE="../platforms/linux/arm-gnueabi.toolchain.cmake" \
      -DCMAKE_C_FLAGS="-isystem /home/pprz/rootfs/usr/include -isystem /home/pprz/rootfs/usr/include/python3.5m -mcpu=arm1176jzf-s -mfpu=vfp -mfloat-abi=hard -marm" \
      -DCMAKE_CXX_FLAGS="-isystem /home/pprz/rootfs/usr/include -isystem /home/pprz/rootfs/usr/include/python3.5m -mcpu=arm1176jzf-s -mfpu=vfp -mfloat-abi=hard -marm" \
      -DBUILD_OPENCV_PYTHON2=ON \
      -DBUILD_OPENCV_PYTHON3=ON \
      -DPYTHON2_INCLUDE_PATH="/usr/include/python2.7" \
      -DPYTHON3_INCLUDE_PATH="/usr/include/python3.5" \
      -DPYTHON2_LIBRARIES="/usr/lib/arm-linux-gnueabihf/libpython2.7.so" \
      -DPYTHON3_LIBRARIES="/usr/lib/arm-linux-gnueabihf/libpython3.5m.so" \
      -DPYTHON2_NUMPY_INCLUDE_DIRS="/usr/lib/python2.7/dist-packages/numpy/core/include" \
      -DPYTHON3_NUMPY_INCLUDE_DIRS="/usr/lib/python3/dist-packages/numpy/core/include" \
      -DBUILD_TESTS=OFF \
      -DBUILD_PERF_TESTS=OFF \
      ..

      -DPYTHON2_EXECUTABLE="/usr/bin/python2.7" \
      -DPYTHON3_EXECUTABLE="/usr/bin/python3.5" \

------------------------------------------------------------------------------------
(not sudo, to keep user PATH)
cd ~/opencv/opencv_build
time make
=> 14 min

sudo make install/strip
(sudo to access /opt)
 
cd /opt
tar -cjvf ~/opencv-4.1.0-armhf.tar.bz2 opencv-4.1.0

Plug the SD card USB adpter
sudo mkdir /media/rootf
sudo mount /dev/sdb2 /media/rootfs
cp ~/opencv-4.1.0-armhf.tar.bz2 /media/rootfs/opt

-------------------------------------------------------------------------------------
RPI
-------------------------------------------------------------------------------------
sudo tar xf opencv-4.1.0-armhf.tar.bz2 -C /opt

sudo ln -s /opt/opencv-4.1.0/lib/python3.5/dist-packages/cv2/python-3.5/cv2.cpython-35m-x86_64-linux-gnu.so /opt/opencv-4.1.0/lib/python3.5/dist-packages/cv2/python-3.5/cv2.so

.bashrc
export PYTHONPATH=/opt/opencv-4.1.0/lib/python3.5/dist-packages/:/opt/opencv-4.1.0/lib/python2.7/dist-packages/:$PYTHONPATH
export LD_LIBRARY_PATH=/opt/opencv-4.1.0/lib/:$LD_LIBRARY_PATH

-------------------------------------------------------------------------------------
/usr/lib/arm-linux-gnueabihf/pkgconfig/opencv.pc
---------
libdir = /opt/opencv-4.1.0/lib
includedir = /opt/opencv-4.1.0/include/opencv4

Name: OpenCV
Description: OpenCV (Open Source Computer Vision Library) is an open source computer vision and machine learning software library.
Version: 4.1.0
Libs: -L${libdir} -lopencv_aruco -lopencv_bgsegm -lopencv_bioinspired -lopencv_calib3d -lopencv_ccalib -lopencv_core -lopencv_datasets -lopencv_dnn_objdetect -lopencv_dnn -lopencv_dpm -lopencv_face -lopencv_features2d -lopencv_flann -lopencv_freetype -lopencv_fuzzy -lopencv_gapi -lopencv_hfs -lopencv_highgui -lopencv_imgcodecs -lopencv_img_hash -lopencv_imgproc -lopencv_line_descriptor -lopencv_ml -lopencv_objdetect -lopencv_optflow -lopencv_phase_unwrapping -lopencv_photo -lopencv_plot -lopencv_reg -lopencv_rgbd -lopencv_saliency -lopencv_shape -lopencv_stereo -lopencv_stitching -lopencv_structured_light -lopencv_superres -lopencv_surface_matching -lopencv_text -lopencv_tracking -lopencv_videoio -lopencv_video -lopencv_videostab -lopencv_xfeatures2d -lopencv_ximgproc -lopencv_xobjdetect -lopencv_xphoto
Cflags: -I${includedir}

-------------------------------------------------------------------------------------
source .bashrc

python3
import cv2
cv2.__version__
=> '4.1.0'


print(cv2.getBuildInformation())
=> Gstreamer YES

-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------
python2
import cv2

ImportError: /opt/opencv-4.1.0/lib/python2.7/dist-packages/cv2/python-2.7/cv2.so: undefined symbol: PyUnicode_AsUnicode

-------------------------------------------------------------------------------------

-------------------------------------------------------------------------------------
sudo apt-get install gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-omx

raspivid -t 0 -w 640 -h 480 -o - | gst-launch-1.0 fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.43.181 port=5000

On laptop
gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false

-------------------------------------------------------------------------------------

-------------------------------------------------------------------------------------
ULTRALOW LATENCY
-------------------------------------------------------------------------------------
apt-get install autoconf automake libtool pkg-config libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libraspberrypi-dev
git clone https://github.com/thaytan/gst-rpicamsrc.git
cd gst-rpicamsrc/
./autogen.sh --prefix=/usr --libdir=/usr/lib/arm-linux-gnueabihf/
make
sudo make install
sudo reboot


gst-launch-1.0 rpicamsrc bitrate=10000000 ! 'video/x-h264,width=640,height=480,framerate=25/1' ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.43.181 port=5000

gst-launch-1.0 rpicamsrc bitrate=10000000 ! 'video/x-raw,width=640,height=480,framerate=25/1' ! omxh264enc target-bitrate=1000000 control-rate=variable ! 'video/x-h264,profile=(string)high' ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.43.181 port=5000


On laptop
gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false

-------------------------------------------------------------------------------------

#!/usr/bin/python3

import picamera
import picamera.array
import socket
import cv2
import subprocess

#gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false

#raspivid -t 0 -w 640 -h 480 -o - | gst-launch-1.0 fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.43.181 port=5000



gstreamer = subprocess.Popen([
  'gst-launch-1.0',
  'fdsrc',
  '!', 'h264parse',
  '!', 'rtph264pay', 'config-interval=1', 'pt=96',
  '!', 'udpsink', 'host=192.168.43.181', 'port=5000'
  ], stdin=subprocess.PIPE)

class MyOutput(object):
  def __init__(self):
    self.size = 0
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  def write(self, buf):
    self.size += len(buf)
    self.sock.sendto(buf, ('192.168.43.181', 1234))

  def flush(self):
    print('%d bytes would have been written' % self.size)


with picamera.PiCamera() as camera:
  camera.resolution = (640, 480)
  with picamera.array.PiMotionArray(camera, size=(320, 240)) as output:
    camera.start_recording(
      gstreamer.stdin, 
      bitrate=1000000,
      format='h264', 
      motion_output=output,
      resize=(320, 240))
    camera.wait_recording(20)
    camera.stop_recording()
    print('Captured %d frames' % output.array.shape[0])
    print('Frames are %dx%d blocks big' % (
      output.array.shape[2], output.array.shape[1]))

print("hello")

-------------------------------------------------------------------------------------
sudo apt-get install python3-pip
pip3 install imutils
pip3 install picamera

https://answers.opencv.org/question/202017/how-to-use-gstreamer-pipeline-in-opencv/
#!/usr/bin/python3
import cv2
from imutils.video import VideoStream
from multiprocessing import Process

def send():
    #vs = VideoStream(usePiCamera=True, resolution=(640, 480)).start()
    cap_send = cv2.VideoCapture('videotestsrc ! video/x-raw,framerate=20/1 ! videoscale ! videoconvert ! appsink', cv2.CAP_GSTREAMER)
    out_send = cv2.VideoWriter('appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! rtph264pay ! udpsink host=127.0.0.1 port=5000',cv2.CAP_GSTREAMER,0, 20, (320,240), True)

    if not cap_send.isOpened() or not out_send.isOpened():
        print('VideoCapture or VideoWriter not opened')
        exit(0)

    while True:
        ret,frame = cap_send.read()

        if not ret:
            print('empty frame')
            break

        out_send.write(frame)
        #out_send.write(vs.read())


    cap_send.release()
    out_send.release()
    #vs.release()


if __name__ == '__main__':
    s = Process(target=send)
    s.start()
    s.join()

