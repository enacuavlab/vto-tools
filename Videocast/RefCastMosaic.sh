#!/bin/bash

# GCS Linux Ubuntu
# Side-by-side streams
# NVIDIA Hardware acceleration H264 encoding

ffmpeg \
        -f lavfi -i anullsrc=r=44100 \
        -r 15 -i udp://192.168.1.237:2201 \
        -r 15 -i udp://192.168.1.237:2202 \
        -f x11grab -video_size 1920x1080 -r 15  -i :0.0+3840,0 \
        -f lavfi -i testsrc=size=1920x1080:rate=15 \
	-filter_complex "
		[1] setpts=PTS-STARTPTS [upperleft];
		[2] setpts=(PTS-STARTPTS+6/TB) [upperright];
		[3] setpts=(PTS-STARTPTS) [lowerleft];
		[4] setpts=PTS-STARTPTS [lowerright];
        [upperleft][upperright]hstack[top];
        [lowerleft][lowerright]hstack[bottom];
        [top][bottom]vstack
	" \
    -c:v h264_nvenc \
    -f flv "rtmp://a.rtmp.youtube.com/live2/rghc-mqk1-ubx3-5501" & \

ssh pprz@192.168.1.238 \
"ffmpeg \
            -probesize 20M \
            -f x11grab -r 15 -s 1920x1080 -i :0.0+0,0 \
            -c:v h264_nvenc \
            -f mpegts udp://192.168.1.237:2201" & \

#		[2] setpts=(PTS-STARTPTS+6/TB) [upperright];

