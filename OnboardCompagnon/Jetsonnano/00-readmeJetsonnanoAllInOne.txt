Jeston Nano

Wifibroadcast work tested with 
OK: Bus 001 Device 004: ID 148f:5572 Ralink Technology, Corp. RT5572 Wireless Adapter
OK: Bus 001 Device 004: ID 0bda:8812 Realtek Semiconductor Corp. RTL8812AU 802.11a/b/g/n/ac 2T2R DB WLAN Adapter

Wifiadapters can be mixed

--------------------------
First setup needs : Monitor, keyboard, mouse
Then use ssh

https://developer.nvidia.com/jetson-nano-sd-card-image
flash 
boot
configure with desktop

--------------------------
sudo vi /etc/network/interfaces.d/eth0
auto eth0
iface eth0 inet static
address 192.168.2.2
netmask 255.255.255.0


sudo vi /etc/network/interfaces.d/wlan0
auto personal_hotspot
iface wlan0 inet dhcp
  wpa-ssid Androidxp
  wpa-psk pprzpprz

auto home_hotspot
iface wlan0 inet dhcp
  wpa-ssid Livebox-7EA4
  wpa-psk 6vNVEJNeLCYLubnbuk

<pre>auto wlan0
iface wlan0 inet dhcp
wpa-ssid Androidxp
wpa-psk pprzpprz
</pre>

auto wifi_option1
iface wlan0 inet dhcp
  wpa-ssid "Androidxp"
  wpa-psk "pprzpprz"

auto wifi_option2
iface wlan0 inet dhcp
  wpa-ssid "Livebox-7EA4"
  wpa-psk "6vNVEJNeLCYLubnbuk"

auto wifi_option3
iface wlan0 inet dhcp
  wpa-ssid "Livebox-1aa4"
  wpa-psk "E89831065C74F706AFC0E95F63"



sudo vi /etc/NetworkManager/Networkmager.conf
managed=true
reboot

--------------------------
ssh

sudo vi /etc/hosts
sudo vi /etc/hostname

sudo apt-get update
sudo apt-get upgrade

--------------------------
Test 1 OK
------
gst-launch-1.0 nvarguscamerasrc ! ... ! udpsink host=192.168.2.1 port=5000 sync=false async=false
option 1)
 'video/x-raw(memory:NVMM), width=(int)1280, height=(int)720, framerate=(fraction)30/1' ! omxh264enc ! video/x-h264, stream-format=byte-stream ! rtph264pay mtu=1400
option 2)
 'video/x-raw(memory:NVMM), width=(int)1280, height=(int)720, framerate=(fraction)30/1' ! nvv4l2h264enc maxperf-enable=1 bitrate=8000000 ! h264parse ! rtph264pay mtu=1400

gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false

Test 2 OK
------
gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM), width=(int)1280, height=(int)720, framerate=(fraction)30/1' ! omxh264enc ! h264parse ! video/x-h264,stream-format=byte-stream ! shmsink socket-path=/tmp/camera1 wait-for-connection=false sync=false
gst-launch-1.0 shmsrc socket-path=/tmp/camera1 do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay name=pay0 pt=96 config-interval=1 ! udpsink host=192.168.2.1 port=5000

gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false

Test 3 KO
------
OK
gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM), width=(int)1280, height=(int)720, framerate=(fraction)30/1, format=(string)NV12' ! nvvidconv flip-method=2 ! 'video/x-raw(memory:NVMM), format=(string)I420' ! omxh264enc ! h264parse ! video/x-h264,stream-format=byte-stream  ! tee name=streams ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! shmsink socket-path=/tmp/camera1 wait-for-connection=false sync=false streams. ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! shmsink socket-path=/tmp/camera2 wait-for-connection=false sync=false

OK
gst-launch-1.0 -e nvarguscamerasrc ! 'video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)30/1' \
! nvvidconv ! 'video/x-raw(memory:NVMM), format=(string)I420' ! tee name=streams \
streams. ! omxh264enc bitrate=8000000 ! 'video/x-h264, stream-format=(string)byte-stream' ! h264parse ! qtmux ! filesink location=toto \
streams. ! omxh264enc bitrate=8000000 ! 'video/x-h264, stream-format=(string)byte-stream' ! h264parse ! qtmux ! filesink location=titi







gst-launch-1.0 shmsrc socket-path=/tmp/camera1 do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay name=pay0 pt=96 config-interval=1 ! udpsink host=192.168.2.1 port=5000
or
gst-launch-1.0 shmsrc socket-path=/tmp/camera1 do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay name=pay0 pt=96 config-interval=1 ! udpsink host=192.168.2.1 port=5000

gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false

--------------------------
gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM), width=1920, height=1080,format=NV12, framerate=30/1' ! omxh264enc ! shmsink socket-path=/tmp/camera1 wait-for-connection=false sync=false

raspivid -t 0 -w 640 -h 480 -fps 30/1 -b 3000000 -g 5 -vf -hf -cd H264 -n -fl -ih -o - | gst-launch-1.0 fdsrc ! h264parse ! video/x-h264,stream-format=byte-stream ! tee name=streams ! omxh264dec ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! shmsink socket-path=/tmp/camera2 wait-for-connection=false sync=false streams. ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! shmsink socket-path=/tmp/camera1 wait-for-connection=false sync=false

gst-launch-1.0 -e nvarguscamerasrc ! 'video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, format=(string)NV12, framerate=(fraction)30/1' ! nvvidconv ! 'video/x-raw(memory:NVMM), format=(string)I420' ! tee name=streams ! omxh264enc bitrate=8000000 ! 'video/x-h264, stream-format=(string)byte-stream' ! h264parse ! shmsink socket-path=/tmp/camera1 wait-for-connection=false sync=false streams. ! omxh264enc bitrate=8000000 ! 'video/x-h264, stream-format=(string)byte-stream' ! h264parse ! qtmux ! filesink location=titi



gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM), width=(int)1280, height=(int)720, framerate=(fraction)30/1, format=(string)NV12' ! nvvidconv flip-method=2 ! 'video/x-raw(memory:NVMM), format=(string)I420'  ! omxh264enc ! tee name=streams ! h264parse ! video/x-h264,stream-format=byte-stream   ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! shmsink socket-path=/tmp/camera1 wait-for-connection=false sync=false streams. ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! shmsink socket-path=/tmp/camera2 wait-for-connection=false sync=false

--------------------------
(gst-launch-1.0 -v nvarguscamerasrc ! 'video/x-raw(memory:NVMM),width=3280, height=2464, framerate=21/1, format=NV12' ! nvvidconv flip-method=0 ! 'video/x-raw, width=820, height=616, format=BGRx' ! videoconvert ! video/x-raw, format=BGR ! appsink)

--------------------------
(git clone https://github.com/aircrack-ng/rtl8812au)
git clone https://github.com/svpcom/rtl8812au.git

sudo apt install dkms

cd rtl8812au
sudo ./dkms-install.sh

/*
vi include/autoconf.h
#define CONFIG_USE_EXTERNAL_POWER 
*/

sudo dkms status
=> rtl8812au, 5.2.20.2, 4.9.140-tegra, aarch64: installed
(sudo dkms remove rtl8812au/5.2.20.2 --all)

--------------------------
sudo iw list

------
RT5572
(20 dBm max)
* 5180 MHz [36] (20.0 dBm) (no IR)
* 5500 MHz [100] (20.0 dBm) (no IR, radar detection)
* 5660 MHz [132] (20.0 dBm) (no IR, radar detection)

---------
RTL8812AU AC-1200
(27 dBm max)
* 5180 MHz [36] (20.0 dBm)
* 5500 MHz [100] (27.0 dBm) (no IR, radar detection)
* 5660 MHz [132] (27.0 dBm) (no IR, radar detection)

---------
RTL8812AU AC-1200 AWUS036ACH
(26 dBm max)
* 5180 MHz [36] (20.0 dBm)
* 5500 MHz [100] (26.0 dBm) (no IR, radar detection)
* 5660 MHz [132] (26.0 dBm) (no IR, radar detection)

------
sudo iw reg get
country DE: DFS-ETSI
(5150 - 5250 @ 80), (N/A, 20), (N/A), NO-OUTDOOR, AUTO-BW
...
(5470 - 5725 @ 160), (N/A, 26), (0 ms), DFS


------
sudo iw reg set RU
sudo iw reg get
  country RU: DFS-ETSI
  (5170 - 5250 @ 80), (N/A, 20), (N/A), AUTO-BW
  ...
  (5650 - 5730 @ 80), (N/A, 30), (0 ms), DFS


--------------------------
sudo ifconfig wlan0 down
sudo iwconfig wlan0 mode monitor
sudo iwconfig wlan0 channel 36

------
sudo ifconfig wlan0 down
sudo iw dev wlan0 set monitor otherbss
sudo iw reg set DE
sudo ifconfig wlan0 up
sudo iw dev wlan0 set channel 36
sudo iw wlan0 info




