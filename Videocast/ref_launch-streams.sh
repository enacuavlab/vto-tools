#!/bin/bash

#------------------------------------------------------------------------------
net rpc service start castscreen_srv -I optitrack -U pprz%pprz

remote_pid=$(ssh pprz@192.168.1.236 \
"ffmpeg \
  -f x11grab -r 25 -s 1920x1080 -i :0.0+0,0 \
  -c:v h264_nvenc \
  -tune zerolatency \
  -f mpegts udp:\/\/192.168.1.237:35010 > /dev/null 2>&1 & echo \$!")

echo "Successfully started service: 192.168.1.237:35010"

#------------------------------------------------------------------------------
ffmpeg \
  -f lavfi -i anullsrc=r=44100 \
  -protocol_whitelist file,udp,rtp -i windows/optitrack.sdp \
  -i rtsp://pprz:vtoenac@192.168.1.232/axis-media/media.amp?resolution=1920x1080 \
  -r 25 -i udp://192.168.1.237:35010 \
  -f x11grab -video_size 1920x1080 -r 25  -i :0.0+3840,0 \
  -filter_complex "[1][2]hstack[top];[3][4]hstack[bottom];[top][bottom]vstack" \
  -c:v h264_nvenc \
  -f flv "rtmp://a.rtmp.youtube.com/live2/rghc-mqk1-ubx3-5501" >/dev/null 2>&1 & 

mosaic_pid=$!
    
echo "Webcast started"    
read -p "Press to stop"

#------------------------------------------------------------------------------
kill -9 $mosaic_pid

ssh pprz@192.168.1.236 "kill -9 $remote_pid"

net rpc service stop castscreen_srv -I optitrack -U pprz%pprz


echo "Webcast stopped"


 
