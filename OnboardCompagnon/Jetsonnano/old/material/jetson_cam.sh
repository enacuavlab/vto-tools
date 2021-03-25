#!/bin/bash

#export GROUNDED=true;
export GROUNDED=false;

#------------------------------------------------------------------------------
# DEBUG
# libargus-fails-on-re-entry-if-killed
#   sudo systemctl restart nvargus-daemon

#------------------------------------------------------------------------------
# CAMERA AND STREAM CONFIGURATION
#------------------------------------------------------------------------------
WIDTH=640
HEIGHT=480
#WIDTH=1280
#HEIGHT=720
FPS=30

IP=192.168.1.46
PORT1=5030
PORT2=5010

CAMPORT=6000

#------------------------------------------------------------------------------
SHMPATH1=/tmp/camera1
SHMPATH2=/tmp/camera2
SHMPATH3=/tmp/camera3

GST="gst-launch-1.0"

SHMCMD=$GST
SHMSRCARG="do-timestamp=true !"
SHMSRC1="shmsrc socket-path=$SHMPATH1 $SHMSRCARG"
SHMSRC2="shmsrc socket-path=$SHMPATH2 $SHMSRCARG"
SHMSRC3="shmsrc socket-path=$SHMPATH3 $SHMSRCARG"

SRCSHM1="$GST $SHMSRC1"
SRCSHM2="$GST $SHMSRC2"
SRCSHM3="$GST $SHMSRC3"

SHMSINKARG="wait-for-connection=false sync=false async=false"
SHMSINK1="shmsink socket-path=$SHMPATH1 $SHMSINKARG"
SHMSINK2="shmsink socket-path=$SHMPATH2 $SHMSINKARG"
SHMSINK3="shmsink socket-path=$SHMPATH3 $SHMSINKARG"

VIDEOSIZE="width=$WIDTH,height=$HEIGHT,framerate=$FPS/1"

FMT="format=I420"
RAWFMT="video/x-raw,$FMT"
RAWFMTSIZE="video/x-raw,$FMT,$VIDEOSIZE !"

RAWNVMM="video/x-raw(memory:NVMM)"
RAWNVMMFMT="$RAWNVMM,$FMT"

CONVFMT="nvvidconv flip_method=2 ! $RAWFMT !"
CONVNVMMFMT="nvvidconv flip_method=2 ! $RAWNVMMFMT !"


CAMCMD="$GST nvarguscamerasrc ! video/x-raw(memory:NVMM),$VIDEOSIZE !"

TSTCMD="$GST videotestsrc ! $RAWFMTSIZE"

H264FMT="video/x-h264,stream-format=byte-stream,alignment=au !"
H264PAY="rtph264pay  name=pay0 pt=96 config-interval=1"
H264ENC="omxh264enc ! $H264FMT"

UDPSINK0="$H264PAY ! udpsink host=127.0.0.1 port=$CAMPORT"

UDPSINK1="$H264PAY ! udpsink host=$IP port=$PORT1"
UDPSINK2="$H264PAY ! udpsink host=$IP port=$PORT2"

BRANCH1="$RAWNVMM ! $CONVNVMMFMT $H264ENC $SHMSINK1"
BRANCH2="$CONVFMT $SHMSINK2"
TEENAME="streams"
TEECMD="tee name=$TEENAME ! $BRANCH1 $TEENAME. ! $BRANCH2"

SERVERCMD="/home/pprz/gst-rtsp-server-1.14.5/examples/test-launch"

#------------------------------------------------------------------------------
# EXECUTION 
#------------------------------------------------------------------------------
rm /tmp/camera*
killall gst-launch-1.0 test-launch test

if ($GROUNDED); then
echo "GROUNDED"
#---------


#------------------------------------------------------------------------------
else
echo "FLYING"
#---------
#                    | omxh264enc --> camera1 (x-h264,I420)
# camcmd (x-raw) --> |
#                    | --> camera2 (x-raw,I420)
#	                                  |
#	                                  | --> VideoCapture (yuv) VideoWriter --> camera3 (x-raw,I420)
#
#---------
# Clients commands :
#gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse \
#	! avdec_h264 ! videoconvert ! autovideosink sync=false
#gst-launch-1.0 rtspsrc location=rtsp://192.168.3.2:8554/test ! rtph264depay ! avdec_h264 !  xvimagesink sync=false
#gst-launch-1.0 rtspsrc location=rtsp://192.168.3.2:8554/test2 ! rtph264depay ! avdec_h264 !  xvimagesink sync=false

#---------
#$TSTCMD $H264ENC $UDPSINK1 &

#$CAMCMD $H264ENC $UDPSINK1 &

#$CAMCMD $H264ENC $UDPSINK0 &

#---------
$CAMCMD $H264ENC $SHMSINK1 &

#$CAMCMD $CONVFMT $SHMSINK2 &

#$CAMCMD $TEECMD &

#---------
while [[ ! -e $SHMPATH1 ]]; do sleep 1; done
$SHMCMD $SHMSRC1 $H264FMT $UDPSINK0 &

while [[ ! -e $SHMPATH1 ]]; do sleep 1; done
$SHMCMD $SHMSRC1 $H264FMT $UDPSINK1 &

#while [[ ! -e $SHMPATH2 ]]; do sleep 1; done
#$SHMCMD $SHMSRC2 $RAWFMTSIZE $H264ENC $UDPSINK2 &

#while [[ ! -e $SHMPATH2 ]]; do sleep 1; done
#/home/pprz/opencv_test/test &

#---------
#while [[ ! -e $SHMPATH1 ]]; do sleep 1; done
#while [[ ! -e $SHMPATH3 ]]; do sleep 1; done
#$SERVERCMD "\"$SHMSRC1 $H264FMT $H264PAY\"" "\"$SHMSRC3 $RAWFMTSIZE $H264ENC $H264PAY\"" &

#------------------------------------------------------------------------------
fi
