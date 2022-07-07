After internal eMMC flashed, and oem-configured, flash external SD with carrier board drivers
----------------------------------------------------------------------------------------------

https://connecttech.com/resource-center/kdb377-booting-off-external-media-cti-jetson-carriers/
https://connecttech.com/ftp/dropbox/create_sd_image.sh

docker ps
=> 249b22738b5f   jetpackimage
docker cp  create_sd_image.sh 249b22738b5f:/home/jetpack/nvidia/nvidia_sdk/JetPack_4.6_Linux_JETSON_XAVIER_NX_TARGETS/Linux_for_Tegra

chmod +x create_sd_image.sh

Plug SD on host 
dmesg -w
=> sdb

sudo ./create_sd_image.sh /dev/sdb
(10 minutes)
unmount sd

plug SD on XavierNX carrier board (quark)

USB-C cable connected
PowerOn xavier nx
Press quark board recovery button (> 10 Sec)
dmesg -w 
=> APX

sudo ./flash.sh cti/xavier-nx/quark/rpi-imx219 external

PowerOff xavier nx
USB-C cable disconnected
UART/USB(FTDI) cable connected

screen /dev/ttyUSB0 115200
Please complete system configuration setup on the serial port provided by Jetson's USB device mode connection. 
e.g. /dev/ttyACMx where x can 0, 1, 2 etc.



sudo minicom -b 115200 -8 -D /dev/ttyUSB0















-----------------------------------------------------------------------------------------
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














/boot/extlinux/extlinux.conf
DEFAULT primary
LABEL primary
      LINUX /boot/Image 
      #FDT /boot/2_tegra194-xavier-nx-cti-NGX004-AVT-2CAM.dtb
