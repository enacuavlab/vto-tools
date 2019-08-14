#!/bin/sh 

#                        | --> camera1 (x-h264) 
# rpicamsrc (x-h264) --> |   
#                        | omxh264dec --> camera2 (x-raw,I420) 
#	                                  |
#	                                  | --> VideoCapture (yuv) VideoWriter --> camera3 (x-raw,I420) 

rm /tmp/cam*
sudo killall gst-launch-1.0 
gst-launch-1.0 rpicamsrc bitrate=1000000 vflip=true ! \
	video/x-h264,width=640,height=480,framerate=15/1 ! \
	h264parse config-interval=1 ! \
	tee name=streams ! \
	queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! \
	omxh264dec ! \
	shmsink socket-path=/tmp/camera2 wait-for-connection=false sync=false streams. ! \
	queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! \
	shmsink socket-path=/tmp/camera1 wait-for-connection=false sync=false &
PID_CAM=$!

sleep 2

#------------------------------------------------------------------------------------------------
# Point to point
#---------------
#gst-launch-1.0 shmsrc socket-path=/tmp/camera1 ! video/x-h264,width=640,height=480,framerate=15/1,stream-format=byte-stream,alignment=au ! rtph264pay config-interval=1  pt=96 ! udpsink host=192.168.43.181 port=5000 sync=false &
#gst-launch-1.0 shmsrc socket-path=/tmp/camera2 ! video/x-raw,format=I420,width=640,height=480,framerate=15/1 ! omxh264enc ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.43.181 port=5000 sync=false &
#echo "gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! avdec_h264 ! xvimagesink sync=false"

# Point to server variable bitrate to be study later
#----------------------------------------------------
#sudo killall gst-variable-rtsp-server 
#gst-gateworks-apps/bin/gst-variable-rtsp-server -p 8554 -m /test -u \
#  "( shmsrc socket-path=/tmp/camera1 do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay config-interval=1 name=pay0 pt=96 )" &
#gst-gateworks-apps/bin/gst-variable-rtsp-server -p 8554 -m /test -u \
#  "( shmsrc socket-path=/tmp/camera2 do-timestamp=true is-live=true ! video/x-raw,format=I420,width=640,height=480,framerate=15/1 ! omxh264enc ! video/x-h264,profile=high ! rtph264pay name=pay0 pt=96 config-interval=1 )" &


#------------------------------------------------------------------------------------------------
./test6 &
PID_APP=$!

sleep 2

#------------------------------------------------------------------------------------------------
# Point to server 
#----------------
# test-launch.c patched with second stream 
#   gst_rtsp_media_factory_set_launch (factory, argv[2]);
#   gst_rtsp_media_factory_set_shared (factory, TRUE);
#   gst_rtsp_mount_points_add_factory (mounts, "/test2", factory);

gst-rtsp-server-1.10.4/examples/test-launch \
  "( shmsrc socket-path=/tmp/camera1 do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay config-interval=1 name=pay1 pt=96 )" \
  "( shmsrc socket-path=/tmp/camera3 do-timestamp=true is-live=true ! video/x-raw,format=I420,width=640,height=480,framerate=15/1 ! omxh264enc ! video/x-h264,profile=high ! rtph264pay name=pay0 pt=96 config-interval=1 )" &
echo "gst-launch-1.0 rtspsrc location=rtsp://192.168.43.73:8554/test ! rtph264depay ! avdec_h264 ! xvimagesink sync=false"

PID_NET=$!

#------------------------------------------------------------------------------------------------
read dummy
sudo kill -9 $PID_NET $PID_APP $PID_CAM
