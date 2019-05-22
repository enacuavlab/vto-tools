-------------------------------------------------------------------------------------
https://solarianprogrammer.com/2018/12/18/cross-compile-opencv-raspberry-pi-raspbian/
https://github.com/opencv/opencv/wiki/Intel's-Deep-Learning-Inference-Engine-backend
-------------------------------------------------------------------------------------
GUEST 

Build VM from netinst
Install minimal configuration with user root and pprz
(unset "environnement de bureau Debian","serveur d'impression","utilitaires usuels du système")

Edit virtual machine settings 
- / Hardware Memory 2Gb
- / Options / VmWare Tools Updates / Update manually

Power On
Virtual Machine / Install Vmware tools

logging root
apt-get install fuse
mkdir /mnt/tools
mount /dev/cdrom /mnt/tools
cp /mnt/tools/VMware... .
gunzip
tar xvf
./.../vmware-install.pl

Virtual Machine Setting / Options / SharedFolder
ls /mnt/hgfs/...

apt-get install sudo
adduser pprz sudo

sudo dd if=/dev/zero of=/swapfile1 bs=1G count=1
sudo chmod 600 /swapfile1
sudo mkswap /swapfile1
sudo swapon /swapfile1:::
sudo vi /etc/fstab
/swapfile1  swap  swap  defaults  0 0

reboot
sudo swapon --show

-------------------------------------------------------------------------------------
opencv-ctx.sh
=> opencv-4.0.0.tar.gz (87,5M)

-------------------------------------------------------------------------------------
#!/bin/sh
sudo -s
dpkg --add-architecture armhf && \
  apt-get update && \
  apt-get install -y --no-install-recommends \
  crossbuild-essential-armhf \
  cmake \
  pkg-config \
  wget \
  xz-utils \
  libpython-dev:armhf \
  libpython3-dev:armhf \
  python-numpy \
  python3-numpy \
  libgstreamer1.0-dev:armhf \
  libgstreamer-plugins-base1.0-dev:armhf \
  libtiff-dev:armhf \
  zlib1g-dev:armhf \
  libjpeg-dev:armhf \
  libpng-dev:armhf \
  libavcodec-dev:armhf \
  libavformat-dev:armhf \
  libswscale-dev:armhf \
  libv4l-dev:armhf \
  libxvidcore-dev:armhf \
  libx264-dev:armhf

-------------------------------------------------------------------------------------
#ARMv6-compatible processor rev 7 : PI ZERO W
#!/bin/sh
cd ~/opencv-4.0.0 && mkdir opencv_build && mkdir opencv_install && cd opencv_build
cmake -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX="../opencv_install" \
      -DCMAKE_CXX_FLAGS="-mcpu=arm1176jzf-s -mfpu=vfp -mfloat-abi=hard -marm" \
      -DOPENCV_CONFIG_INSTALL_PATH="cmake" \
      -DCMAKE_TOOLCHAIN_FILE="../platforms/linux/arm-gnueabi.toolchain.cmake" \
      -DWITH_IPP=OFF \
      -DBUILD_TESTS=OFF \
      -DBUILD_PERF_TESTS=OFF \
      -DOPENCV_ENABLE_PKG_CONFIG=ON \
      -DPKG_CONFIG_EXECUTABLE="/usr/bin/arm-linux-gnueabihf-pkg-config" \
      -DPYTHON2_INCLUDE_PATH="/usr/include/python2.7" \
      -DPYTHON2_NUMPY_INCLUDE_DIRS="/usr/local/lib/python2.7/dist-packages/numpy/core/include" \
      -DPYTHON3_INCLUDE_PATH="/usr/include/python3.5" \
      -DPYTHON3_NUMPY_INCLUDE_DIRS="/usr/local/lib/python3.5/dist-packages/numpy/core/include" \
      -DPYTHON3_CVPY_SUFFIX=".cpython-35m-arm-linux-gnueabihf.so" \
      -DENABLE_NEON=OFF ..

-------------------------------------------------------------------------------------
cd ~/opencv-4.0.0/opencv_build
time make
=> 15 min
make install/strip

cd ~
tar -cjvf ~/opencv-4.0.0-armhf.tar.bz2 opencv-4.0.0/opencv_install/*

-------------------------------------------------------------------------------------
opencv.pc
---------
libdir = /opt/opencv-4.0.0/lib
includedir = /opt/opencv-4.0.0/include/opencv4

Name: OpenCV
Description: OpenCV (Open Source Computer Vision Library) is an open source computer vision and machine learning software library.
Version: 4.0.0
Libs: -L${libdir} -lopencv_aruco -lopencv_bgsegm -lopencv_bioinspired -lopencv_calib3d -lopencv_ccalib -lopencv_core -lopencv_datasets -lopencv_dnn_objdetect -lopencv_dnn -lopencv_dpm -lopencv_face -lopencv_features2d -lopencv_flann -lopencv_freetype -lopencv_fuzzy -lopencv_gapi -lopencv_hfs -lopencv_highgui -lopencv_imgcodecs -lopencv_img_hash -lopencv_imgproc -lopencv_line_descriptor -lopencv_ml -lopencv_objdetect -lopencv_optflow -lopencv_phase_unwrapping -lopencv_photo -lopencv_plot -lopencv_reg -lopencv_rgbd -lopencv_saliency -lopencv_shape -lopencv_stereo -lopencv_stitching -lopencv_structured_light -lopencv_superres -lopencv_surface_matching -lopencv_text -lopencv_tracking -lopencv_videoio -lopencv_video -lopencv_videostab -lopencv_xfeatures2d -lopencv_ximgproc -lopencv_xobjdetect -lopencv_xphoto
Cflags: -I${includedir}

-------------------------------------------------------------------------------------
HOST (strech lite)

python2 and python3 already installed

#!/bin/sh
sudo -s 
apt-get update && \
apt-get install -y --no-install-recommends \
libpython-dev \
libpython3-dev \
python-numpy \
python3-numpy \
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
HOST (strech lite)

Copy 
opencv-4.0.0-armhf.tar.bz2 (11 M)
opencv.pc 

-------------------------------------------------------------------------------------
tar xf opencv-4.0.0-armhf.tar.bz2
sudo mv opencv-4.0.0 /opt
sudo mv opencv.pc /usr/lib/arm-linux-gnueabihf/pkgconfig

echo 'export LD_LIBRARY_PATH=/opt/opencv-4.0.0/lib' >> .bashrc
source .bashrc

cd /opt/opencv-4.0.0/python
sudo python setup.py develop
sudo python3 setup.py develop

-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------
python3
import cv2
cv2.__version__
=> '3.4.4'

print(cv2.getBuildInformation())
=> Gstreamer YES


-------------------------------------------------------------------------------------

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





