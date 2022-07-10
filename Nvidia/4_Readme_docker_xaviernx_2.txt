After internal eMMC flashed, flash external SD with carrier board drivers
--------------------------------------------------------------------------

docker system prune
docker run --name jetpackcontainer --privileged -v /dev/bus/usb:/dev/bus/usb/ -v /dev:/dev jetpackimage

docker exec -it jetpackcontainer /bin/bash

https://connecttech.com/resource-center/kdb377-booting-off-external-media-cti-jetson-carriers/
https://connecttech.com/ftp/dropbox/create_sd_image.sh

docker ps
=> 27fd52bc2a72   jetpackimage
docker cp  create_sd_image.sh 27fd52bc2a72:/home/jetpack/nvidia/nvidia_sdk/JetPack_4.6_Linux_JETSON_XAVIER_NX_TARGETS/Linux_for_Tegra

cd /home/jetpack/nvidia/nvidia_sdk/JetPack_4.6_Linux_JETSON_XAVIER_NX_TARGETS/Linux_for_Tegra
chmod +x create_sd_image.sh
(10 minutes)

Disable auto-mount on host (dconf-editor)
Plug SD on host 
dmesg -w
=> sdx

sudo ./create_sd_image.sh /dev/sdx
=> Success: Created sd card with rootfs. Safe to remove the card.
(10 minutes)
unmount sdx

docker commit jetpackcontainer jetpackimage
dmes
plug SD on XavierNX carrier board (quark)

USB-C cable connected
PowerOn xavier nx
Press quark board recovery button (> 10 Sec)
dmesg -w 
=> APX

cd /home/jetpack/nvidia/nvidia_sdk/JetPack_4.6_Linux_JETSON_XAVIER_NX_TARGETS/Linux_for_Tegra
sudo ./flash.sh cti/xavier-nx/quark/rpi-imx219 external

PowerOff xavier nx
UART/USB(FTDI) cable connected

screen /dev/ttyUSB0 115200
=> login console


ssh pprz@192.168.3.2
=> OK


-----------------------------------------------------------------------------------------
XavierNX won't boot anymore from emmc !
SD card must be set up and present to boot XavierNX !

-----------------------------------------------------------------------------------------
Previously !
Xavier NX boot sequence: SD, NV

[0002.126] I> boot-dev-order :-
[0002.130] I> 1.sd
[0002.132] I> 2.usb
[0002.133] I> 3.nvme
[0002.135] I> 4.emmc
[0002.137] I> 5.net
Booting from internal eMMC (16 Gb): /dev/mmcblk0

Booting from external device: 
- NVME
- microSD: /dev/mmcblk0p1

------------------------------------------------------------------------
Continuing installing applications on SD
(internet connection needed)

2.5)
sdkmanager --cli downloadonly --logintype devzone --product Jetson --target JETSON_XAVIER_NX_TARGETS --targetos Linux --version 4.6 --deselect 'Jetson OS' --select 'Jetson SDK Components' --license accept --staylogin true

CUDA, CUDA-X AI, Computer Vision, NVIDIA Container Runtime, Multimedia, Developer Tools


2.6) 
run rules outoff docker, to brige ethernet and wifi (internet)

sudo iptables -I FORWARD -i enxe4b97ab11842 -o wlp59s0 -j ACCEPT
sudo iptables -I FORWARD -i wlp59s0 -o enxe4b97ab11842 -j ACCEPT
sudo iptables -t nat -I POSTROUTING -o wlp59s0 -j MASQUERADE
sudo sysctl net.ipv4.ip_forward=1

2.7)
ssh pprz@192.168.3.2
ping www.google.com
=> PING www.google.com (216.58.214.164) 56(84) bytes of data.

sdkmanager --cli install --logintype devzone --product Jetson --target JETSON_XAVIER_NX_TARGETS --targetos Linux --version 4.6 --deselect 'Jetson OS' --select 'Jetson SDK Components' --license accept --staylogin true 












/boot/extlinux/extlinux.conf
DEFAULT primary
LABEL primary
      LINUX /boot/Image 
      #FDT /boot/2_tegra194-xavier-nx-cti-NGX004-AVT-2CAM.dtb
