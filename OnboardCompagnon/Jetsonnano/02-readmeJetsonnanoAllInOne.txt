
https://developer.nvidia.com/embedded/downloads

SD Card image method:
  For Jetson Nano Developer kit
  https://developer.nvidia.com/embedded/jetson-nano-developer-kit
  => jetson-nano-4gb-jp441-sd-card-image.zip (6Go)

Etcher: flash SD (30 min)
Put not modified SD
Do not plug Ethernet nor Wifi adapter
First setup needs : Monitor, keyboard, mouse
Boot and set minimal configuration with desktop
Reboot
Shutdown

Remove SD, an update network configuration on it (*)
Put SD, connect wifi adapter or ethernet and boot

---------
nmap -sn 192.168.43.1/24

--------------------------
ssh

sudo vi /etc/hosts
sudo vi /etc/hostname

sudo apt-get update
sudo apt-get upgrade
(382Mo)

sudo apt install v4l-utils

-------------------------------------------------------------------------------
Step (1): on unchanged installation setup
-------------------------------------------------------------------------------

- RPI Camera V2 (IMX219) OK

sudo dmesg 
 media: Linux media interface: v0.10
 Linux video capture interface: v2.00

/sys/firmware/devicetree/base/cam_i2cmux/i2c@0/rbpcv2_imx219_a@10
                             /host1x/i2c@546c0000/rbpcv2_imx219_a@10

/dev/video0

v4l2-ctl --list-formats-ext -d /dev/video0
...
 Pixel Format: 'RG10'
 Name : 10-bit Bayer RGRG/GBGB
  Size: Discrete 1280x720
    Interval: Discrete 0.033s (30.000 fps)
...
OK for bayer acquisition only:
gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM), width=1280, height=720, framerate=30/1' ! omxh264enc ! video/x-h264, stream-format=byte-stream ! rtph264pay ! udpsink host=192.168.3.1 port=5000
gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false


NOK 
gst-launch-1.0 v4l2src device=/dev/video0 ...

-------------------------------------------------------------------------------
Step (2): on modified installation with Allied Vision drivers
-------------------------------------------------------------------------------

- ALVIUM 1800 C-240c (IMX392) OK

/sys/firmware/devicetree/base/cam_i2cmux/i2c@0/avt_csi2@3c
/dev/video0 video1

v4l2-ctl --list-formats-ext -d /dev/video0
...
  Index       : 4
  Type        : Video Capture
  Pixel Format: 'XR24'
  Name        : 32-bit BGRX 8-8-8-8
    Size: Discrete 1936x1216
      Interval: Discrete 0.029s (34.713 fps)

  Index       : 5
  Type        : Video Capture
  Pixel Format: 'VYUY'
  Name        : VYUY 4:2:2
    Size: Discrete 1936x1216
      Interval: Discrete 0.029s (34.713 fps)
---
gst-launch-1.0 nvarguscamerasrc ! fakesink
=> No cameras available


v4l2-ctl -c auto_gain=1,red_balance=2000,blue_balance=1700
exposure=70000000

gst-launch-1.0 v4l2src device=/dev/video0 ! video/x-raw,format=BGRx,width=1936,height=1216,pixel-aspect-ratio=1/1,framerate=34/1,colorimetry=sRGB,interlace-mode=progressive ! nvvidconv ! 'video/x-raw(memory:NVMM),width=640,height=480,framerate=34/1' ! omxh264enc ! video/x-h264, stream-format=byte-stream ! rtph264pay mtu=1400 ! udpsink host=192.168.3.1 port=5000 sync=false async=false
or
gst-launch-1.0 v4l2src device=/dev/video0 ! nvvidconv ! 'video/x-raw(memory:NVMM),width=640,height=480,framerate=34/1' ! omxh264enc ! video/x-h264, stream-format=byte-stream ! rtph264pay mtu=1400 ! udpsink host=192.168.3.1 port=5000 sync=false async=false

gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false


------------------------------------------------------------------------------------------------------------
(*) CONFIGURE 

sudo vi /etc/wpa_supplicant/wpa_supplicant.conf
network={
  ssid="Androidxp"
  psk="pprzpprz"
}
network={
  ssid="pprz_router"
  key_mgmt=NONE
}
network={
  ssid="Livebox-7EA4"
  psk="6vNVEJNeLCYLubnbuk"
}
network={
  ssid="Livebox-1aa4"
  psk="E89831065C74F706AFC0E95F63"
}

---------
sudo vi /etc/network/interfaces

auto eth0
iface eth0 inet static
address 192.168.3.2
netmask 255.255.255.0

auto wlan0
iface wlan0 inet dhcp
    wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf


------------------------------------------------------------------------------------------------------------
(**) AlliedVision

Option 1) Install precompiled kernel containing drivers (V4L2 ...) for Alvium MIPI CSI-2 cameras

https://www.alliedvision.com/en/products/software/embedded-software-and-drivers/
- "precompiled kernel"
  "nano"
  AlliedVision_NVidia_nano_L4T_32.4.2_4.9.140-ga01070fee.tar.gz (30Mo)

  scp AlliedVision_NVidia_nano_L4T_32.4.2_4.9.140-ga01070fee.tar.gz pprz@192.168.3.2:/home/pprz
  ssh pprz@1921.68.3.2
  tar xf AlliedVision_NVidia_nano_L4T_32.4.2_4.9.140-ga01070fee.tar.gz
  cd ~/AlliedVision_NVidia__L4T_32.4.2_4.9.140-ga01070fee
  uname  -a
  => Linux nano 4.9.140-tegra #1 SMP PREEMPT Fri Oct 16 12:32:46 PDT 2020 aarch64 aarch64 aarch64 GNU/Linux
  sudo ./install.sh
  => Allied Vision MIPI CSI-2 camera driver for NVidia Jetson Nano (kernel 4.9.140)
  sudo shutdown now




Option 2) Compile from source
 
https://github.com/alliedvision/linux_nvidia_jetson


------------------------------------------------------------------------------------------------------------
(***) Tests

RPI Camera V2 (IMX219)
ALVIUM 1800C-240 (IMX392)

/dev/video0 video1
/dev/v4l-subdev0 v4l-subdev1

v4l2-ctl --list-formats-ext -d /dev/video0

gst-launch-1.0 v4l2src device=/dev/video0 ! video/x-raw,format=BGRx,width=1936,height=1216,pixel-aspect-ratio=1/1,framerate=34/1,colorimetry=sRGB,interlace-mode=progressive ! nvvidconv ! 'video/x-raw(memory:NVMM),width=640,height=480,framerate=34/1' ! omxh264enc ! video/x-h264, stream-format=byte-stream ! rtph264pay mtu=1400 ! udpsink host=192.168.3.1 port=5000 sync=false async=false

gst-launch-1.0 v4l2src device=/dev/video0 ! nvvidconv ! 'video/x-raw(memory:NVMM),width=640,height=480,framerate=34/1' ! omxh264enc ! video/x-h264, stream-format=byte-stream ! rtph264pay mtu=1400 ! udpsink host=192.168.3.1 port=5000 sync=false async=false





gst-launch-1.0 udpsrc port=5000 ! application/x-rtp,encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! queue ! avdec_h264 ! xvimagesink sync=false async=false -e
