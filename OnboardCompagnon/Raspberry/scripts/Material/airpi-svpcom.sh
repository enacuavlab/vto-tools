#!/bin/bash

ifconfig wlan1 down
iw dev wlan1 set monitor otherbss
iw reg set DE
ifconfig wlan1 up
iw dev wlan1 set channel 36
#iw wlan1 info


WIDTH=1280
HEIGHT=720
FPS=30
KEYFRAMERATE=5

EXTRAPARAMS="-vf -hf -cd H264 -n -fl -ih -pf high -if both -ex sports -mm average -awb horizon"

ANNOTATION="ENAC"

BITRATE=3000000 

#------------------------------------------------------------------------------
sleep 1
/home/pi/proxy/exe/bridge &
sleep 1
/home/pi/wifibroadcast-svpcom/wfb_tx -p 2 -u 4242 -K /home/pi/wifibroadcast-svpcom/drone.key wlan1 &
/home/pi/wifibroadcast-svpcom/wfb_rx -p 3 -c 127.0.0.1 -u 4243 -K /home/pi/wifibroadcast-svpcom/gs.key wlan1 &

#------------------------------------------------------------------------------
sleep 1
rm /tmp/camera1
rm /tmp/camera2
ionice -c 1 -n 3 raspivid -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -g $KEYFRAMERATE -t 0 $EXTRAPARAMS -a "$ANNOTATION" -ae 22 -o - | \
	ionice -c 1 -n 4 nice -n -10 gst-launch-1.0 fdsrc ! \
	h264parse ! \
	video/x-h264,stream-format=byte-stream ! \
	tee name=streams ! \
	omxh264dec ! \
	queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! \
	shmsink socket-path=/tmp/camera2 wait-for-connection=false sync=false streams. ! \
	queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! \
	shmsink socket-path=/tmp/camera1 wait-for-connection=false sync=false &

sleep 1
rm /tmp/camera3
/home/pi/opencv_trials/cpp/airpiqrcode &
#/home/pi/opencv_trials/cpp/airpicv &

#sleep 1
#ionice -c 1 -n 4 nice -n -10 gst-launch-1.0 shmsrc socket-path=/tmp/camera3 do-timestamp=true ! \
#	video/x-raw,format=I420,width=$WIDTH,height=$HEIGHT,framerate=$FPS/1 ! \
#	omxh264enc ! video/x-h264,profile=high ! \
#	rtph264pay config-interval=1 pt=96 ! udpsink host=127.0.0.1 port=5600 &

sleep 1
ionice -c 1 -n 4 nice -n -10 gst-launch-1.0 shmsrc socket-path=/tmp/camera1 do-timestamp=true ! \
	video/x-h264,stream-format=byte-stream,alignment=au ! \
	rtph264pay config-interval=1 pt=96 ! udpsink host=127.0.0.1 port=5600 &

sleep 1
/home/pi/wifibroadcast-svpcom/wfb_tx -p 1 -u 5600 -K /home/pi/wifibroadcast-svpcom/drone.key wlan1 &

#sleep 1
#/home/pi/gst-rtsp-server-1.10.4/examples/test-launch "( shmsrc socket-path=/tmp/camera3 do-timestamp=true is-live=true ! video/x-raw,format=I420,width=$WIDTH,height=$HEIGHT,framerate=$FPS/1 ! omxh264enc ! video/x-h264,profile=high ! rtph264pay name=pay0 pt=96 config-interval=1 )" &

#/home/pi/gst-rtsp-server-1.10.4/examples/test-launch "( shmsrc socket-path=/tmp/camera1 do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay name=pay0 pt=96 config-interval=1 )" &

# client gst-launch-1.0 rtspsrc location=rtsp://192.168.1.30:8554/test ! rtph264depay ! avdec_h264 !  xvimagesink sync=false


#------------------------------------------------------------------------------
sleep 1
/home/pi/wifibroadcast-svpcom/wfb_tx -p 4 -u 4244 -K /home/pi/wifibroadcast-svpcom/drone.key wlan1 &

#echo -n "hello" | nc -4u -w0 127.0.0.1 4244
