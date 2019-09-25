https://github.com/opencv/opencv/wiki/Intel%27s-Deep-Learning-Inference-Engine-backend
https://solarianprogrammer.com/2018/12/18/cross-compile-opencv-raspberry-pi-raspbian/

-------------------------------------------------------------------------------------
CAUTION !!

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
Libs: -L${libdir} -lopencv_calib3d -lopencv_core -lopencv_dnn -lopencv_features2d -lopencv_flann -lopencv_gapi -lopencv_highgui -lopencv_imgcodecs -lopencv_imgproc -lopencv_ml -lopencv_objdetect -lopencv_photo -lopencv_stitching -lopencv_videoio -lopencv_video
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

