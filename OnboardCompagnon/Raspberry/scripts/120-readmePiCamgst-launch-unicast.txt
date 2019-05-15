This has one advantage: the stream has almost no delay, which I could never manage to get with any of the methods that stream over RTSP

-------------------------------------------------------------------------------
UDP: Ultra low LAG 
- Sender need to know receiver IP

On the Raspberry Pi:
raspivid -t 0 -w 640 -h 480 -o - | gst-launch-1.0 fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.43.181 port=5000

On laptop
gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false


-------------------------------------------------------------------------------
TCP: 1 second LAG 
- Receiver need to know sender IP

On the Raspberry Pi:
raspivid -n -t 0 -w 640 -h 480 -fps 25 -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=0.0.0.0 port=5000

Display the stream on another computer (substitute IP as appropriate):
gst-launch-1.0 -v tcpclientsrc host=192.168.43.104 port=5000 ! gdpdepay ! rtph264depay ! avdec_h264 ! videoconvert ! autovideosink sync=false



