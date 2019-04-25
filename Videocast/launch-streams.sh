#!/bin/bash

#------------------------------------------------------------------------------
net rpc service start castscreen_srv -I optitrack -U pprz%pprz

remote_pid=$(ssh pprz@192.168.1.236 \
"ffmpeg \
  -f x11grab -r 15 -s 1920x1080 -i :0.0+0,0 \
  -c:v h264_nvenc \
  -tune zerolatency \
  -f rtp rtp://192.168.1.237:35010 > /dev/null 2>&1 & echo \$!")

echo "Successfully started service: 192.168.1.237:35010"

#------------------------------------------------------------------------------
ffmpeg \
  -f lavfi -i anullsrc=r=44100 \
  -f lavfi -i testsrc=size=1920x1080:rate=25 \
  -i rtsp://pprz:vtoenac@192.168.1.232/axis-media/media.amp?resolution=1920x1080 \
  -filter_complex "[1:v] setpts=PTS [A];\
                   [2:v] setpts=PTS+1/TB [B];\
                   [A][B]hstack" \
  output.avi  & 
#  -c:v h264_nvenc \
#  -f flv "rtmp://a.rtmp.youtube.com/live2/rghc-mqk1-ubx3-5501" >/dev/null 2>&1 & 

mosaic_pid=$!
    
echo "Webcast started"    
read -p "Press to stop"

#------------------------------------------------------------------------------
kill -9 $mosaic_pid

ssh pprz@192.168.1.236 "kill -9 $remote_pid"

net rpc service stop castscreen_srv -I optitrack -U pprz%pprz


echo "Webcast stopped"

#-f lavfi -i testsrc=size=1920x1080:rate=25 \
#-i rtsp://pprz:vtoenac@192.168.1.232/axis-media/media.amp?resolution=1920x1080 \
#-protocol_whitelist file,udp,rtp -i windows/optitrack.sdp \
#-f x11grab -video_size 1920x1080 -r 25  -i :0.0+3840,0 \
#-protocol_whitelist file,udp,rtp -i huppe.sdp \

#  -filter_complex "[1:v] setpts=PTS+1/TB [A];\
#                   [2:v] setpts=PTS+1/TB [B];\
#                   [3:v] setpts=PTS+1/TB [C];\
#                   [4:v] setpts=PTS [D];\
#                   [A][B]hstack[top];\
#                   [C][D]hstack[bottom];\
#                   [top][bottom]vstack" \
                   

#ffplay -fflags nobuffer rtsp://pprz:vtoenac@192.168.1.232/axis-media/media.amp?resolution=1920x1080
#ffplay -fflags nobuffer -protocol_whitelist file,udp,rtp -i windows/optitrack.sdp
