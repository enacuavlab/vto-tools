#!/bin/bash

PIDFILE=/tmp/wfb.pid

#rm /tmp/fromimu
rm /tmp/camera*
BITRATE_VIDEO1=2000000
BITRATE_VIDEO2=2000000
/home/pi/Projects/RaspiCV/build/raspicv -t 0 -w 640 -h 480 -fps 10/1 -b $BITRATE_VIDEO1 -vf -hf -cd H264 -n -a ENAC -ae 22 -x /dev/null -r /dev/null -rf gray -o - \
   | gst-launch-1.0 fdsrc \
    ! h264parse \
    ! video/x-h264,stream-format=byte-stream,alignment=au \
    ! rtph264pay name=pay0 pt=96 config-interval=1 \
    ! udpsink host=127.0.0.1 port=5600 &
echo $! >> $PIDFILE
sleep 3
gst-launch-1.0 shmsrc socket-path=/tmp/camera3 do-timestamp=true \
  ! video/x-raw, format=BGR, width=640, height=480, framerate=30/1, colorimetry=1:1:5:1  \
  ! v4l2h264enc extra-controls="controls,video_bitrate=$BITRATE_VIDEO2" \
  ! rtph264pay name=pay0 pt=96 config-interval=1 \
  ! udpsink host=127.0.0.1 port=5700 &
echo $! >> $PIDFILE

#v4l2-ctl --device /dev/video0 \
#  --set-fmt-video=width=640,height=480,pixelformat=4 \
#  --set-ctrl video_bitrate=2000000 \
#  --set-parm=30 \
#  --set-ctrl vertical_flip=1 \
#  --stream-mmap=0 --stream-to=- \
#  | gst-launch-1.0 fdsrc \
#    ! h264parse \
#    ! video/x-h264,stream-format=byte-stream,alignment=au \
#    ! rtph264pay name=pay0 pt=96 config-interval=1 \
#    ! udpsink host=127.0.0.1 port=5700  > /dev/null 2>&1 &
#  echo $! >> $PIDFILE
