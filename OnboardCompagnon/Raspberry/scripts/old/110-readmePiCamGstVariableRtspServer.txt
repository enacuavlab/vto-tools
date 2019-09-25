----------------------------------------------------------------------------------
gst-launch-1.0 --version
=> gst-launch-1.0 version 1.10.4

wget http://gstreamer.freedesktop.org/src/gst-rtsp-server/gst-rtsp-server-1.10.4.tar.xz
tar -xf gst-rtsp-server-1.10.4.tar.xz 
rm gst-rtsp-server-1.10.4.tar.xz
cd gst-rtsp-server-1.10.4/

./configure
make
=> 7min
sudo make install

git clone https://github.com/Gateworks/gst-gateworks-apps.git
cd gst-gateworks-apps
make
cd ~

-------------------------------------------------------------------------------------------
gst-gateworks-apps/bin/gst-variable-rtsp-server -p 8554 -m /test -u "( shmsrc socket-path=/tmp/camera1 do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay config-interval=1 name=pay0 pt=96 )"


gst-launch-1.0 rpicamsrc bitrate=1000000 vflip=true ! video/x-h264,width=640,height=480,framerate=15/1 ! h264parse config-interval=1 ! tee name=streams ! queue max-size-bytes=0 max-size-buffers=0 ! shmsink socket-path=/tmp/camera1 wait-for-connection=false sync=false streams. ! queue max-size-bytes=0 max-size-buffers=0 ! omxh264dec ! shmsink socket-path=/tmp/camera2 wait-for-connection=false sync=false


gst-launch-1.0 rtspsrc location=rtsp://192.168.1.80:8554/test ! rtph264depay ! avdec_h264 ! xvimagesink sync=false


-------------------------------------------------------------------------------------------
g++ -g test10.cpp -o test10 `pkg-config --cflags --libs opencv` -D_GLIBCXX_USE_CXX11_ABI=0 -lpthread

