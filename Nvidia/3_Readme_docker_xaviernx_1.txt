...

------------------------------------------------------------------------
2)

docker system prune

docker run --name jetpackcontainer --privileged -v /dev/bus/usb:/dev/bus/usb/ -v /dev:/dev jetpackimage

docker exec -it jetpackcontainer /bin/bash

2.1)
sdkmanager --cli downloadonly --logintype devzone --product Jetson --version 4.6 --targetos Linux --target JETSON_XAVIER_NX_TARGETS --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --staylogin true

2.2) To prevent chroot exec error:
sudo apt purge binfmt-support qemu-user-static
sudo apt-get update
sudo apt-get install qemu-user-static

sdkmanager --cli install --logintype devzone --product Jetson --version 4.6 --targetos Linux --target JETSON_XAVIER_NX_TARGETS --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --staylogin true --flash skip

https://connecttech.com/product/quark-carrier-nvidia-jetson-xavier-nx/
JetPack 4.6 – L4T r32.6.1 	NX L4T r32.6.1 BSP	NX L4T r32.6.1 Release Notes	04-Mar-22
https://connecttech.com/ftp/Drivers/CTI-L4T-XAVIER-NX-32.6.1-V010.tgz
(keep this version or you wont be able to load compiled drivers: "disagrees about version of symbol module_layout")

docker ps
=> f2b8ea3f8330   jetpackimage 
docker cp CTI-L4T-XAVIER-NX-32.6.1-V010.tgz f2b8ea3f8330:/home/jetpack/nvidia/nvidia_sdk/JetPack_4.6_Linux_JETSON_XAVIER_NX_TARGETS/Linux_for_Tegra

cd /home/jetpack/nvidia/nvidia_sdk/JetPack_4.6_Linux_JETSON_XAVIER_NX_TARGETS/Linux_for_Tegra
tar -xzf CTI-L4T-XAVIER-NX-32.6.1-V010.tgz
rm CTI-L4T-XAVIER-NX-32.6.1-V010.tgz
cd ./CTI-L4T
sudo ./install.sh
=> CTI-L4T-Xavier-NX-32.6.1-V010 Installed!


docker image ls
jetpackimage  30.4GB

docker commit jetpackcontainer jetpackimage

docker image ls
jetpackimage  38.1GB


2.2b) Create user and ethernet primary network

Disable initial configuration menu (oem-config):
sudo apt purge binfmt-support qemu-user-static
sudo apt-get update
sudo apt-get install qemu-user-static
cd /home/jetpack/nvidia/nvidia_sdk/JetPack_4.6_Linux_JETSON_XAVIER_NX_TARGETS/Linux_for_Tegra
sudo ./tools/l4t_create_default_user.sh -u pprz -p pprz -n xaviernx1 -a --accept-license 

./rootfs/etc/default/networking
CONFIGURE_INTERFACES=no

./rootfs/etc/network/interfaces
auto eth0
iface eth0 inet static
  address 192.168.3.2
  netmask 255.255.255.0
  gateway 192.168.3.1
  dns-nameservers 8.8.8.8
  dns-nameservers 8.8.4.4
  dns-search foo


2.3) Optional
cd /home/jetpack/nvidia/nvidia_sdk/JetPack_4.6_Linux_JETSON_XAVIER_NX_TARGETS/Linux_for_Tegra

sudo ./flash.sh --no-flash cti/xavier-nx/quark/rpi-imx219 mmcblk0p1

2.4)
cd /home/jetpack/nvidia/nvidia_sdk/JetPack_4.6_Linux_JETSON_XAVIER_NX_TARGETS/Linux_for_Tegra
Flash Jetson Xavier NX eMMC(16 GB) + Quark (Connecttech carrier board)
without SD card on carrier board

 1.Connect USB-C
 2.Plug UART/USB(FTDI) adapter
 3.PowerOn
 4.Press Recovery Button (>10sec) 
dmesg -w 
=> Product: APX
   (no /dev/ttyUSB0, no ttyACMx)

 5.Flash 
  First xavierNx flash eMMC(16 GB) (without SD-CARD)
  (10 minutes to flash all partitions)

sudo ./flash.sh cti/xavier-nx/quark/rpi-imx219 mmcblk0p1
=> Reset the board to boot from internal eMMC.

 6.Console (auto login)
screen /dev/ttyUSB0 115200

 7.Plug ethernet
 Configure static on host 192.168.3.1/255.255.255.0/192.168.3.1
 ssh pprz@192.168.3.2


docker commit jetpackcontainer jetpackimage
docker image ls
jetpackimage   latest    9ca07a1a1dd1   8 seconds ago   87.3GB
ubuntu         18.04     ad080923604a   4 weeks ago     63.1MB

sudo du -h ./Docker
=>
142G	./Docker

Stop "docker run ..."
sudo du -h ./Docker
=>
83G	./Docker


