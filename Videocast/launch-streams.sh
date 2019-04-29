#!/bin/bash


# https://gist.github.com/Brainiarc7/7b6049aac3145927ae1cfeafc8f682c1

#------------------------------------------------------------------------------
net rpc service start castscreen_srv -I optitrack -U pprz%pprz

#------------------------------------------------------------------------------
FPS="25"


X11GRAB="-f x11grab -s 1920x1080 -r $FPS"

H264ENCODE="-c:v h264_nvenc -pix_fmt yuv420p -r "$FPS" -g "$(($FPS * 2))

#------------------------------------------------------------------------------
REMOTE="pprz@192.168.1.236"
HOST_URL="-f rtp rtp://192.168.1.237:35010"
X11GRAB_REMOTE=$X11GRAB" -i :0.0+0,0" 
H264ENCODE_REMOTE=$H264ENCODE" -tune zerolatency"

remote_pid=$(ssh $REMOTE \
"ffmpeg \
  $X11GRAB_REMOTE \
  $H264ENCODE \
  $HOST_URL > /dev/null 2>&1 & echo \$!")

echo "Successfully started service: "$HOST_URL

#------------------------------------------------------------------------------
YOUTUBE_URL="rtmp://a.rtmp.youtube.com/live2"
KEY="rghc-mqk1-ubx3-5501"

THREAD_QUEUE="-thread_queue_size 1024"
PROTOCOL_WHITELIST="-protocol_whitelist file,udp,rtp"

AXIS_CAMERA="-i rtsp://pprz:vtoenac@192.168.1.232/axis-media/media.amp"
AXIS_CAMERA_PARAM="resolution=1920x1080&h264profile=baseline&videocodec=h264\
&fps="$FPS"&compression=33&videobitrate=50000&videobitratepriority=framerate"

X11GRAB_LOCAL=$X11GRAB" -i :0.0+3840,0" 

ffmpeg \
  -f lavfi -i anullsrc=r=44100 \
  $THREAD_QUEUE $X11GRAB_LOCAL \
  $THREAD_QUEUE $PROTOCOL_WHITELIST -i huppe.sdp \
  $THREAD_QUEUE $PROTOCOL_WHITELIST -i windows/optitrack.sdp \
  $THREAD_QUEUE $AXIS_CAMERA?$AXIS_CAMERA_PARAM \
  -filter_complex "[1:v] fps=fps=$FPS,setpts=PTS-STARTPTS [A];\
                   [2:v] fps=fps=$FPS,setpts=PTS-STARTPTS [B];\
                   [3:v] fps=fps=$FPS,setpts=PTS-STARTPTS [C];\
                   [4:v] fps=fps=$FPS,setpts=PTS-STARTPTS [D];\
                   [A][B]hstack[top];\
                   [C][D]hstack[bottom];\
                   [top][bottom]vstack" \
  -bsf:a aac_adtstoasc -c:a aac -ac 2 -ar 48000 -b:a 128k \
  -b:v 2400k -minrate:v 2400k -maxrate:v 2400k -bufsize:v 160k \
  -c:v h264_nvenc -pix_fmt nv12 -qp:v 19  \
  -profile:v high -rc:v cbr_ld_hq -level:v 4.1 -r 60 -g 120 -bf:v 3 \
  -f flv "$YOUTUBE_URL/$KEY"  & 

#   $H264ENCODE -threads 4 \

#  -f flv - | ffplay - -fflags nobuffer

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
