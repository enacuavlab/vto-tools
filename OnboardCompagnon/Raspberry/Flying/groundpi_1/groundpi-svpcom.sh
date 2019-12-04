#!/bin/bash

#-------------------------------------------------------------------------------
#ifconfig wlan0 down
#sleep 1

#-------------------------------------------------------------------------------
ifconfig wlan1 down
iw dev wlan1 set monitor otherbss
iw reg set DE
ifconfig wlan1 up
iw dev wlan1 set channel 36
iw wlan1 info

sleep 1

/home/pi/wifibroadcast-svpcom/wfb_rx -p 1 -c 127.0.0.1 -u 5000 -K /home/pi/wifibroadcast-svpcom/gs.key wlan1 &

#-------------------------------------------------------------------------------
sleep 1
rm /tmp/camera1
rm /tmp/camera2
ionice -c 1 -n 3 gst-launch-1.0 udpsrc port=5000  ! \
	application/x-rtp, encoding-name=H264,payload=96 ! \
	rtph264depay ! \
	video/x-h264,stream-format=byte-stream ! \
	tee name=streams ! \
	h264parse ! \
	omxh264dec ! \
	queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! \
	shmsink socket-path=/tmp/camera2 wait-for-connection=false sync=false streams. ! \
	queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! \
	shmsink socket-path=/tmp/camera1 wait-for-connection=false sync=false &

sleep 1
ionice -c 1 -n 4 nice -n -10 gst-launch-1.0 shmsrc socket-path=/tmp/camera1 do-timestamp=true ! \
	video/x-h264,stream-format=byte-stream,alignment=au ! \
	fdsink | \
	/home/pi/wifibroadcast_osd/fpv_video/fpv_video &

#sleep 1
#rm /tmp/camera3
#/home/pi/opencv_trials/cpp/groundpiqrcode &
#/home/pi/opencv_trials/cpp/groundpicv &

#-------------------------------------------------------------------------------
#WIDTH=1280
#HEIGHT=720
#FPS=30
#
#sleep 1
#/home/pi/gst-rtsp-server-1.10.4/examples/test-launch "( shmsrc socket-path=/tmp/camera3 do-timestamp=true is-live=true ! video/x-raw,format=I420,width=$WIDTH,height=$HEIGHT,framerate=$FPS/1 ! omxh264enc ! video/x-h264,profile=high ! rtph264pay name=pay0 pt=96 config-interval=1 )" &

sleep 1
/home/pi/gst-rtsp-server-1.10.4/examples/test-launch "( shmsrc socket-path=/tmp/camera1 do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay name=pay0 pt=96 config-interval=1 )" &

# client gst-launch-1.0 rtspsrc location=rtsp://192.168.1.30:8554/test ! rtph264depay ! avdec_h264 !  xvimagesink sync=false


#-------------------------------------------------------------------------------
sleep 1
/home/pi/wifibroadcast-svpcom/wfb_rx -p 2 -c 192.168.1.236 -u 4242 -K /home/pi/wifibroadcast-svpcom/gs.key wlan1 &
#/home/pi/wifibroadcast-svpcom/wfb_rx -p 2 -c 127.0.0.1 -u 4242 -K /home/pi/wifibroadcast-svpcom/gs.key wlan1 &
#sleep 1
#/usr/bin/socat -u udp-recv:4242  UDP-DATAGRAM:192.168.1.255:4242,broadcast &
sleep 1
/home/pi/wifibroadcast-svpcom/wfb_tx -p 3 -u 4243 -K /home/pi/wifibroadcast-svpcom/drone.key wlan1 &

sleep 1
/home/pi/wifibroadcast-svpcom/wfb_rx -p 4 -c 127.0.0.1 -u 4244 -K /home/pi/wifibroadcast-svpcom/gs.key wlan1 &

#nc -lu 4244

#-------------------------------------------------------------------------------
#/home/pi/paparazzi/sw/ground_segment/tmtc/server
#/home/pi/paparazzi/sw/ground_segment/tmtc/link  -udp 
#/home/pi/paparazzi/sw/ground_segment/python/natnet3.x/natnet2ivy.py  -ac 115 115  -s 192.168.1.230 -f 5
