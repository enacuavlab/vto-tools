#!/bin/bash

#------------------------------------------------------------------------------
REMOTE="pprz@192.168.1.236"

#------------------------------------------------------------------------------
net rpc service stop castscreen_srv -I optitrack -U pprz%pprz
ssh  $REMOTE "killall ffmpeg"
killall ffmpeg
sleep 2

#------------------------------------------------------------------------------
net rpc service start castscreen_srv -I optitrack -U pprz%pprz

# This is the service running in windows
#
#  gst-launch-1.0.exe -v dx9screencapsrc monitor=1 ! video/x-raw,framerate=25/1 ! queue 
#  ! videoconvert ! x264enc ! ""video/x-h264,profile=baseline"" ! h264parse config-interval=-1 
#  ! rtph264pay pt=96 config-interval=-1 ! udpsink host=192.168.1.237 port=35000 sync=true
#
#------------------------------------------------------------------------------
FPS="25"


X11GRAB="-f x11grab -s 1920x1080 -framerate $FPS"

H264ENCODE="-r 25 -g 50 -c:v h264_nvenc -pix_fmt yuv420p -preset fast -profile:v main \
-b:v 16000K -maxrate 24000k -bufsize 6000k"

#------------------------------------------------------------------------------
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
KEY="szyx-ymyu-kz1y-apkw"

FILENAME="/home/pprz/Vidéos/videocast/`date '+%Y_%m_%d__%H_%M_%S'`.mkv"

THREAD_QUEUE="-thread_queue_size 512"
PROTOCOL_WHITELIST="-protocol_whitelist file,udp,rtp"

AXIS_CAMERA="-i rtsp://pprz:vtoenac@192.168.1.232/axis-media/media.amp"
AXIS_CAMERA_PARAM="resolution=1920x1080&h264profile=baseline&videocodec=h264\
&fps="$FPS"&compression=33&videobitrate=50000&videobitratepriority=framerate"

PI_CAMERA="-i rtsp://192.168.1.246/live/livestream"
# This is the command running in raspberry pi to crtmpserver
#   raspivid -n -t 0 -w 1920 -h 1080 -fps 25 -b 2000000 -o - | ffmpeg -i - -vcodec copy -an 
#   -f flv -metadata streamName=livestream tcp://0.0.0.0:6666

X11GRAB_LOCAL=$X11GRAB" -i :0.0+3840,0" 

ffmpeg \
  -f lavfi -i anullsrc=channel_layout=mono:sample_rate=44100 \
  $THREAD_QUEUE $PROTOCOL_WHITELIST -i windows/optitrack.sdp \
  $THREAD_QUEUE $PROTOCOL_WHITELIST -i huppe.sdp \
  $THREAD_QUEUE $X11GRAB_LOCAL \
  $THREAD_QUEUE $AXIS_CAMERA?$AXIS_CAMERA_PARAM \
  -filter_complex "[1:v] fifo,fps=fps=$FPS,setpts=PTS-STARTPTS [A];\
                   [2:v] fifo,fps=fps=$FPS,setpts=PTS-STARTPTS+4/TB [B];\
                   [3:v] fifo,fps=fps=$FPS,setpts=PTS-STARTPTS [C];\
                   [4:v] fifo,fps=fps=$FPS,setpts=PTS-STARTPTS+6/TB [D];\
                   [D][A]hstack[top];\
                   [B][C]hstack[bottom];\
                   [top][bottom]vstack[output]" \
  -map [output] $H264ENCODE \
  -map 0:a -c:a aac \
  -f tee -flags +global_header "$FILENAME|[f=flv]$YOUTUBE_URL/$KEY" &


#  $THREAD_QUEUE $PI_CAMERA \
#  -f lavfi -i testsrc=size=1920x1080:rate=25 \

  
#
# Encoder options to be checked on GCS and Broadcaster
#
#  -c:a aac -strict experimental -ab 128k -ac 2 -ar 44100 -bt 500k \
#  -c:v libx264 -preset ultrafast -tune zerolatency -b:v 1500K -bufsize 750K -minrate 1000K -maxrate 2000K -framerate 30 -threads 0 \

mosaic_pid=$!

net rpc service start castscreen_srv -I optitrack -U pprz%pprz

    
echo "Webcast started"    
read -p "Press to stop"

#------------------------------------------------------------------------------
kill -9 $mosaic_pid

ssh pprz@192.168.1.236 "kill -9 $remote_pid"


echo "Webcast stopped"

#------------------------------------------------------------------------------
#ffplay -fflags nobuffer rtsp://pprz:vtoenac@192.168.1.232/axis-media/media.amp?resolution=1920x1080
#ffplay -fflags nobuffer -protocol_whitelist file,udp,rtp -i windows/optitrack.sdp
