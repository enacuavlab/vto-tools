#!/bin/bash

#------------------------------------------------------------------------------
REMOTE="pprz@192.168.1.236"

#------------------------------------------------------------------------------
net rpc service stop castscreen_srv -I optitrack2 -U pprz%pprz
ssh  $REMOTE "killall ffmpeg"
killall ffmpeg
sleep 2

#------------------------------------------------------------------------------
net rpc service start castscreen_srv -I optitrack2 -U pprz%pprz

#------------------------------------------------------------------------------
FPS="25"

X11GRAB="-f x11grab -s 1920x1080 -framerate $FPS"

H264ENCODE="-r 25 -g 50 -c:v h264_nvenc -pix_fmt yuv420p -preset fast -profile:v main \
-b:v 16000K -maxrate 24000k -bufsize 6000k"

HOST_URL="-f rtp rtp://192.168.1.237:35010"

X11GRAB_REMOTE=$X11GRAB" -i :0.0+0,0" 

#------------------------------------------------------------------------------
remote_pid=$(ssh $REMOTE \
"ffmpeg \
  $X11GRAB_REMOTE \
  $H264ENCODE \
  $HOST_URL > /dev/null 2>&1 & echo \$!")

echo "Successfully started service: "$HOST_URL


echo "Webcast started"    
read -p "Press to stop"

#------------------------------------------------------------------------------
net rpc service stop castscreen_srv -I optitrack2 -U pprz%pprz
ssh $REMOTE "kill -9 $remote_pid"


echo "Webcast stopped"
