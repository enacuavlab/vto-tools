#!/bin/bash

width=640
height=480
framerate="30/1"
keyframerate=5
bitrate=3000000
extraparams="-vf -hf -cd H264 -n -fl -ih -pf high -if both -ex sports -mm average -awb horizon"
annotation="ENAC"

SHMSINKARG="wait-for-connection=false sync=false"
SHMPATH1=/tmp/camera1
SHMSINK1="! shmsink socket-path=$SHMPATH1 $SHMSINKARG"
SHMPATH2=/tmp/camera2
SHMSINK2="! shmsink socket-path=$SHMPATH2 $SHMSINKARG"
SHMPATH3=/tmp/camera3

SHMSRCARG="do-timestamp=true !"
SHMSRC1="shmsrc socket-path=$SHMPATH1 $SHMSRCARG"
SHMSRC2="shmsrc socket-path=$SHMPATH2 $SHMSRCARG"
SHMSRC3="shmsrc socket-path=$SHMPATH3 $SHMSRCARG"

VIDEOFMT="video/x-raw, format=I420, width=$width, height=$height, framerate=$framerate"

VIDEOSRCTEST="gst-launch-1.0 videotestsrc ! "$VIDEOFMT" ! omxh264enc"

VIDEOSRCCAM="/usr/bin/raspivid -t 0 -w "$width" -h "$height" -fps "$framerate" -b "$bitrate" -g "$keyframerate" "$extraparams" -a "$annotation" -ae 22 -o - "

STREAMPARSE="h264parse"
STREAMFMT="video/x-h264,stream-format=byte-stream"
STREAMCMD="gst-launch-1.0 fdsrc ! $STREAMPARSE ! $STREAMFMT"

CLIENTIP=192.168.1.46
CLIENTPORT=5000
CLIENTUDPPAY="! rtph264pay name=pay0 pt=96 config-interval=1 "
CLIENTUDPSINK=$CLIENTUDPPAY" ! udpsink host=$CLIENTIP port=$CLIENTPORT"

SERVERFMT1="$STREAMFMT,alignment=au"
SERVERFMT="$VIDEOFMT ! omxh264enc ! video/x-h264,profile=high " 
SERVEREXE=/home/pi/gst-rtsp-server-1.14.4/examples/test-launch
SERVERPARAM1="$SHMSRC1 $SERVERFMT1"
SERVERPARAM2="$SHMSRC2 $SERVERFMT"
SERVERPARAM3="$SHMSRC3 $SERVERFMT"

QUEUE="! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 "
TEEARG="! tee name=streams ! omxh264dec "
TEENAME=" streams. "
TEECMD="$STREAMCMD $TEEARG $QUEUE $SHMSINK2 $TEENAME $QUEUE $SHMSINK1"

#------------------------------------------------------------------------------
rm $SHMPATH1
rm $SHMPATH2
rm $SHMPATH3

#$VIDEOSRCTEST $SHMSINK1 &
#$VIDEOSRCTEST $CLIENTUDPSINK

$VIDEOSRCCAM | $TEECMD &

#$VIDEOSRCCAM | $STREAMCMD $SHMSINK1 &
#$VIDEOSRCCAM | $STREAMCMD $CLIENTUDPSINK

sleep 1
/home/pi/testcv/airpicv &
#/home/pi/RaspiCV/build/raspicv -v -w 640 -h 480 -fps 30 -t 0 -o /dev/null -x /dev/null -r /dev/null -rf gray &

sleep 1
#gst-launch-1.0 $SERVERPARAM1 $CLIENTUDPSINK &
#gst-launch-1.0 $SERVERPARAM2 $CLIENTUDPSINK &
gst-launch-1.0 $SERVERPARAM3 $CLIENTUDPSINK &

#sleep 1
#$SERVEREXE "\"$SERVERPARAM1 $CLIENTUDPPAY\"" &
#$SERVEREXE "\"$SERVERPARAM2 $CLIENTUDPPAY\"" &
#$SERVEREXE "\"$SERVERPARAM3 $CLIENTUDPPAY\"" &

#------------------------------------------------------------------------------
#client
#gst-launch-1.0 rtspsrc location=rtsp://192.168.43.1:8554/test ! rtph264depay ! avdec_h264 !  xvimagesink sync=false
#gst-launch-1.0 -vvv udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false
