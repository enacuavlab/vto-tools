-------------------------------------------------------------------------------
https://madennis.gitbooks.io/px4dev/content/en/qgc/video_streaming_wifi_broadcast.html
-------------------------------------------------------------------------------
Installation on PI3 (and PI0)

Install raspbian strech light (configure ssh, wpa)
Boot and connect to mobile hotspot (nmap -sn 192.168.43.0/24)
Configure (raspi-config)
Reboot and add swap (/etc/dphys-swapfile CONF_SWAPSIZE=1024)


Switch uart to bluetooth, and disable bluetooth.


Install gstreamer:
sudo apt-get update
sudo apt-get install gstreamer1.0-tools
sudo apt-get install gstreamer1.0-plugins-bad
sudo apt-get install gstreamer1.0-plugins-good


Install rpicamsrc:
sudo apt-get install dh-autoreconf
sudo apt-get install libgstreamer1.0-dev and libgstreamer-plugins-base1.0-dev
sudo apt-get install gstreamer1.0-libav gstreamer1.0-omx
sudo apt-get install git
git clone https://github.com/thaytan/gst-rpicamsrc.git
cd gst-rpicamsrc
./autogen.sh
make
sudo make install


rename /etc/wpa_suppicant/wpa_supplicant.conf to /etc/wpa_suppicant/wpa_supplicant-wlan0.conf


sudo apt-get install libpcap-dev libsodium-dev
git clone https://github.com/svpcom/wifibroadcast
cd wifibroadcast
make

copy drone.key and gs.key


Check which had the camera 
raspistill -o toto.jpg

gst-launch-1.0 rpicamsrc bitrate=10000000 ! video/x-h264,width=640,height=480,framerate=25/1,profile=high ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.43.181 port=5600
gst-launch-1.0 udpsrc port=5600 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false

(iwlist wlan1 channel)
sudo ifconfig wlan1 down
sudo iw dev wlan1 set monitor otherbss
sudo iw reg set FR
(sudo iw reg get)
sudo ifconfig wlan1 up
sudo iw dev wlan1 set channel 36 HT40+
(36 / 38 / 40 ...)
(sudo iw dev wlan1 info)

gst-launch-1.0 rpicamsrc bitrate=10000000 ! video/x-h264,width=640,height=480,framerate=25/1,profile=high ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=127.0.0.1 port=5600

cd wifibroadcast
sudo ./wfb_tx -p 1 -u 5600 -K drone.key wlan1
(PI0 8% CPU)


Idem 
sudo ifconfig wlan1 down
...

cd wifibroadcast
sudo ./wfb_rx -p 1 -c 192.168.43.181 -u 5000 -K gs.key wlan1

/etc/rc.local
su pi -c /home/pi/airpi1.sh &
sleep 2
su root -c /home/pi/airpi2.sh &


gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false



