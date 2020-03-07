#!/bin/bash

#export GROUNDED=true;
export GROUNDED=false;

#------------------------------------------------------------------------------
# CAMERA AND STREAM CONFIGURATION
#------------------------------------------------------------------------------
width=640
height=480
framerate="30/1"
keyframerate=5
bitrate=3000000
extraparams="-cd H264 -n -fl -ih -pf high -if both -ex sports -mm average -awb horizon"
#extraparams="-vf -hf -cd H264 -n -fl -ih -pf high -if both -ex sports -mm average -awb horizon"
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

# VIDEOSRCMV also cast to /tmp/camera3
VIDEOSRCMV="/home/pi/RaspiCV/build/raspicv -t 0 -w "$width" -h "$height" -fps "$framerate" -b "$bitrate" -g "$keyframerate" "$extraparams" -a "$annotation" -ae 22 -x /dev/null -r /dev/null -rf yuv -o - "

STREAMPARSE="h264parse"
#STREAMPARSE="h264parse config-interval=1 " 
STREAMFMT="video/x-h264,stream-format=byte-stream"
STREAMCMD="gst-launch-1.0 fdsrc ! $STREAMPARSE ! $STREAMFMT"

CLIENTIP=192.168.1.46
#CLIENTIP=192.168.43.181
CLIENTPORT0=5000
CLIENTPORT1=5001
UDPPAY="! rtph264pay name=pay0 pt=96 config-interval=1 "
CLIENTUDPPORT0=$UDPPAY" ! udpsink host=$CLIENTIP port=$CLIENTPORT0"
CLIENTUDPPORT1=$UDPPAY" ! udpsink host=$CLIENTIP port=$CLIENTPORT1"

HOSTUDPPORT=$UDPPAY" ! udpsink host=127.0.0.1 port=5600"

SERVERFMT1="$STREAMFMT,alignment=au"
SERVERFMT="$VIDEOFMT ! omxh264enc ! video/x-h264,profile=high " 
SERVEREXE=/home/pi/gst-rtsp-server-1.14.4/examples/test-launch
SERVERPARAM1="$SHMSRC1 $SERVERFMT1"
SERVERPARAM2="$SHMSRC2 $SERVERFMT"
SERVERPARAM3="$SHMSRC3 $SERVERFMT"

if [ -f "/data/file0.mkv" ]; then
  filename="/data/file`ls /data/file* | wc -l`.mkv"
else 
  filename="/data/file0.mkv" 
fi
FILE="$SHMSRC1 $STREAMPARSE ! matroskamux ! filesink location=$filename"

QUEUE="! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 "
TEEARG="! tee name=streams ! omxh264dec "
TEENAME=" streams. "
TEECMD="$STREAMCMD $TEEARG $QUEUE $SHMSINK2 $TEENAME $QUEUE $SHMSINK1"

#------------------------------------------------------------------------------
VIDEOPARAM1="$SHMSRC1 $SERVERFMT1 ! fdsink "
VIDEOCMD="/home/pi/wifibroadcast_osd/fpv_video/fpv_video"
UDPSRCCMD="gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! video/x-h264,stream-format=byte-stream "

#------------------------------------------------------------------------------
# EXECUTION 
#------------------------------------------------------------------------------
rm $SHMPATH1
rm $SHMPATH2
rm $SHMPATH3

if ($GROUNDED); then
echo "GROUNDED"

#---------
sleep 1
$UDPSRCCMD $SHMSINK1 &
 
#---------
sleep 1
gst-launch-1.0 $VIDEOPARAM1 | $VIDEOCMD &

#--------
sleep 1
gst-launch-1.0 $SERVERPARAM1 $CLIENTUDPPORT0 &

#------------------------------------------------------------------------------
else
echo "FLYING"

#---------
#$VIDEOSRCTEST $SHMSINK1 &
#$VIDEOSRCTEST $CLIENTUDPPORT0 &

#$VIDEOSRCCAM | $TEECMD &
#$VIDEOSRCCAM | $STREAMCMD $SHMSINK1 &
#$VIDEOSRCCAM | $STREAMCMD $CLIENTUDPPORT0 &

#$VIDEOSRCMV | $TEECMD &

#------------------------------------------------------------------------------
#sleep 1
#/home/pi/opencv_test/test &


#------------------------------------------------------------------------------
# FILE RECORD 
#
# Monitor and kill if usb connection is detected (for pi zero)
#tail -F /var/log/syslog | grep --line-buffered 'g_mass_storage gadget: high-speed config' | while read;do kill `ps -ef | grep gst-launch-1.0 | grep filesink | awk '{print $2}'`;done &

# Do not launch if USB is connected (for pi zero) 
#sleep  1
#dmesg | grep -q 'g_mass_storage gadget: high-speed config' || gst-launch-1.0 -e $FILE &

#------------------------------------------------------------------------------
# NETWORK CAST
#
#sleep 1
#gst-launch-1.0 $SERVERPARAM1 $HOSTUDPPORT &
#sleep 1
#gst-launch-1.0 $SERVERPARAM1 $CLIENTUDPPORT0 &
#sleep 1
#gst-launch-1.0 $SERVERPARAM2 $CLIENTUDPPORT0 &
#sleep 2
#gst-launch-1.0 $SERVERPARAM3 $CLIENTUDPPORT0 &

#client: gst-launch-1.0 -vvv udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false
#client: gst-launch-1.0 -vvv udpsrc port=5001 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false


sleep 2
$SERVEREXE "\"$SERVERPARAM1 $UDPPAY\"" "\"$SERVERPARAM3 $UDPPAY\"" &
#$SERVEREXE "\"$SERVERPARAM2 $UDPPAY\"" "\"$SERVERPARAM3 $UDPPAY\"" &
#$SERVEREXE "\"$SERVERPARAM1 $UDPPAY\"" &
#$SERVEREXE "\"$SERVERPARAM2 $UDPPAY\"" &
#$SERVEREXE "\"$SERVERPARAM3 $UDPPAY\"" &

#client: gst-launch-1.0 rtspsrc location=rtsp://192.168.43.1:8554/test ! rtph264depay ! avdec_h264 !  xvimagesink sync=false
#client: gst-launch-1.0 rtspsrc location=rtsp://192.168.43.1:8554/test2 ! rtph264depay ! avdec_h264 !  xvimagesink sync=false

fi

/home/pi/svpcom.sh &
