VIDEO stream
This should be installed to stream the  USB connected JEVOIS camera (acting as a UVC camera)
low cpu consumption by using hardware video codec

Option:
Camera streaming can be controlled (start/stop/resolution=jevois program) from the PPRZ-Telemetry

------------------------------------------------------------
Packages info
"avconv" is a fork from "ffmpeg" maintained (ie compiled) by debian
"gstreamer" is used to pipe video tools in a performant way

Install
sudo apt-get install libav-tools
sudo apt-get install gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-omx


-check:
v4l2-ctl --list-formats-ext
v4l2-ctl --set-fmt-video=width=800,height=600
v4l2-ctl --get-fmt-video

MULTICAST (224.1.1.1)
- stream:
gst-launch-1.0 -v v4l2src device=/dev/video0 ! video/x-raw,width=640,height=500,framerate=20/1 ! omxh264enc ! rtph264pay ! udpsink host=224.1.1.1 port=5000
- play:
gst-launch-1.0  udpsrc multicast-group=224.1.1.1 port=5000 ! application/x-rtp, payload=96 ! rtph264depay ! queue ! avdec_h264 ! videoconvert ! autovideosink sync=false


Option:
BROADCAST (192.168.1.255)
- stream:
gst-launch-1.0 -v v4l2src device=/dev/video0 ! video/x-raw,width=640,height=500,framerate=20/1 ! omxh264enc ! rtph264pay ! udpsink host=192.168.1.255 port=5000
- play:
gst-launch-1.0  udpsrc port=5000 ! application/x-rtp, payload=96 ! rtph264depay ! queue ! avdec_h264 ! videoconvert ! autovideosink sync=false
