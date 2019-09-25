2 seconds LAG !?

-------------------------------------------------------------------------------
git clone https://github.com/mpromonet/v4l2rtspserver.git
cd v4l2rtspserver
cmake . && make
(build with internet)


v4l2rtspserver -F15 -H 720 -W1280 -P 8555 /dev/video0

ffplay rtsp://raspberrypi_ip:8555/unicast
or vlc

