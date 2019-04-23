#!/bin/bash

# GCS Linux Ubuntu
# Side-by-side streams
# NVIDIA Hardware acceleration H264 encoding

ssh pprz@192.168.1.238 \
"ffmpeg \
            -probesize 20M \
            -f x11grab -r 15 -s 1920x1080 -i :0.0+0,0 \
            -c:v h264_nvenc \
            -f mpegts udp://192.168.1.237:2201 ; pid=$!" & \

ffmpeg \
        -f lavfi -i anullsrc=r=44100 \
        -r 15 -i udp://192.168.1.237:2201 \
        -r 15 -i udp://192.168.1.237:2202 \
        -f x11grab -video_size 1920x1080 -r 15  -i :0.0+3840,0 \
	-i rtsp://pprz:vtoenac@192.168.1.232/axis-media/media.amp \
	-filter_complex "
		[1]scale=1920:1080,setpts=PTS-STARTPTS [upperleft];
		[2]scale=1920:1080,setpts=(PTS-STARTPTS+6/TB) [upperright];
		[3]scale=1920:1080,setpts=(PTS-STARTPTS) [lowerleft];
		[4]scale=1920:1080,setpts=PTS-STARTPTS [lowerright];
        [upperleft][upperright]hstack[top];
        [lowerleft][lowerright]hstack[bottom];
        [top][bottom]vstack
	" \
    -c:v h264_nvenc \
    -f flv "rtmp://a.rtmp.youtube.com/live2/rghc-mqk1-ubx3-5501" & \


#		[2] setpts=(PTS-STARTPTS+6/TB) [upperright];
#        -f x11grab -video_size 1920x1080 -r 15  -i :0.0+3840,0 \
#	rtsp://root:vtoenacpprz@192.168.1.232/axis-media/media.amp \
