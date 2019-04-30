#!/bin/bash

# RUN WITHOUT OPTITRACK RTP INPUT !?
# ELSE
# max delay reached. need to consume packet from camera 
#
#------------------------------------------------------------------------------
net rpc service start castscreen_srv -I optitrack -U pprz%pprz

#------------------------------------------------------------------------------
FPS="25"


X11GRAB="-f x11grab -s 1920x1080 -framerate $FPS"

H264ENCODE="-r 25 -g 50 -c:v h264_nvenc -pix_fmt yuv420p -preset fast -profile:v main \
-b:v 16000K -maxrate 24000k -bufsize 6000k"

#------------------------------------------------------------------------------
REMOTE="pprz@192.168.1.236"
HOST_URL="-f rtp rtp://192.168.1.237:35010"

X11GRAB_REMOTE=$X11GRAB" -i :0.0+0,0" 

remote_pid=$(ssh $REMOTE \
"ffmpeg \
  $X11GRAB_REMOTE \
  $H264ENCODE \
  $HOST_URL > /dev/null 2>&1 & echo \$!")

echo "Successfully started service: "$HOST_URL

#------------------------------------------------------------------------------
YOUTUBE_URL="rtmp://a.rtmp.youtube.com/live2"
KEY="rghc-mqk1-ubx3-5501"

THREAD_QUEUE="-thread_queue_size 512"
PROTOCOL_WHITELIST="-protocol_whitelist file,udp,rtp"

AXIS_CAMERA="-i rtsp://pprz:vtoenac@192.168.1.232/axis-media/media.amp"
AXIS_CAMERA_PARAM="resolution=1920x1080&h264profile=baseline&videocodec=h264\
&fps="$FPS"&compression=33&videobitrate=50000&videobitratepriority=framerate"

X11GRAB_LOCAL=$X11GRAB" -i :0.0+3840,0" 

ffmpeg \
  -f lavfi -i anullsrc=r=44100 \
  -f lavfi -i testsrc=size=1920x1080:rate=25 \
  $THREAD_QUEUE $PROTOCOL_WHITELIST -i huppe.sdp \
  $THREAD_QUEUE $X11GRAB_LOCAL \
  $THREAD_QUEUE $AXIS_CAMERA?$AXIS_CAMERA_PARAM \
  -filter_complex "[1:v] fifo,fps=fps=$FPS,setpts=PTS-STARTPTS [A];\
                   [2:v] fifo,fps=fps=$FPS,setpts=PTS-STARTPTS [B];\
                   [3:v] fifo,fps=fps=$FPS,setpts=PTS-STARTPTS [C];\
                   [4:v] fifo,fps=fps=$FPS,setpts=PTS-STARTPTS [D];\
                   [A][B]hstack[top];\
                   [C][D]hstack[bottom];\
                   [top][bottom]vstack" \
  $H264ENCODE \
  -f flv "$YOUTUBE_URL/$KEY"  & 

#   
#    $THREAD_QUEUE $PROTOCOL_WHITELIST -i windows/optitrack.sdp \


mosaic_pid=$!
    
echo "Webcast started"    
read -p "Press to stop"

#------------------------------------------------------------------------------
kill -9 $mosaic_pid

ssh pprz@192.168.1.236 "kill -9 $remote_pid"

net rpc service stop castscreen_srv -I optitrack -U pprz%pprz


echo "Webcast stopped"

#------------------------------------------------------------------------------
#ffplay -fflags nobuffer rtsp://pprz:vtoenac@192.168.1.232/axis-media/media.amp?resolution=1920x1080
#ffplay -fflags nobuffer -protocol_whitelist file,udp,rtp -i windows/optitrack.sdp
