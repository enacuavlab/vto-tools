...

------------------------------------------------------------------------
2)

docker system prune

docker run --name jetpackcontainer --privileged -v /dev/bus/usb:/dev/bus/usb/ -v /dev:/dev jetpackimage

docker exec -it jetpackcontainer /bin/bash

2.1)
sdkmanager --cli downloadonly --logintype devzone --product Jetson --version 4.6 --targetos Linux --target JETSON_XAVIER_NX_TARGETS --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --staylogin true

2.2)
sdkmanager --cli install --logintype devzone --product Jetson --version 4.6 --targetos Linux --target JETSON_XAVIER_NX_TARGETS --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --staylogin true --flash skip

https://connecttech.com/product/quark-carrier-nvidia-jetson-xavier-nx/
https://connecttech.com/ftp/Drivers/CTI-L4T-XAVIER-NX-32.7.2-V003.tgz
22-June-22
CTI-L4T-XAVIER-NX-32.7.2-V003.tgz (500 Mb)

docker ps
=> 8249511561ad   jetpackimage 
docker cp CTI-L4T-XAVIER-NX-32.7.2-V003.tgz 8249511561ad:/home/jetpack/nvidia/nvidia_sdk/JetPack_4.6_Linux_JETSON_XAVIER_NX_TARGETS/Linux_for_Tegra

cd /home/jetpack/nvidia/nvidia_sdk/JetPack_4.6_Linux_JETSON_XAVIER_NX_TARGETS/Linux_for_Tegra
tar -xzf CTI-L4T-XAVIER-NX-32.7.2-V003.tgz
rm CTI-L4T-XAVIER-NX-32.7.2-V003.tgz 
cd ./CTI-L4T
sudo ./install.sh
=> CTI-L4T-XAVIER-NX-32.7.2-V003 Installed!

docker image ls
jetpackimage  30.4GB

docker commit jetpackcontainer jetpackimage

docker image ls
jetpackimage  38.1GB


2.2b)
sudo apt purge binfmt-support qemu-user-static
sudo apt-get update
sudo apt-get install qemu-user-static
cd /home/jetpack/nvidia/nvidia_sdk/JetPack_4.6_Linux_JETSON_XAVIER_NX_TARGETS/Linux_for_Tegra
./tools/l4t_create_default_user.sh -u pprz -p pprz -n xaviernx1 -a



2.3)
cd /home/jetpack/nvidia/nvidia_sdk/JetPack_4.6_Linux_JETSON_XAVIER_NX_TARGETS/Linux_for_Tegra

sudo ./flash.sh --no-flash cti/xavier-nx/quark/rpi-imx219 mmcblk0p1

2.4)
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

 6.Login
screen /dev/ttyUSB0 115200

  eth0: Ethernet, static IP configuration 192.168.3.2/255.255.255.0/192.168.3.1/8.8.8.8,8.8.4,4

  11.Login console
  ifconfig eth0

  12.Plug ethernet
  Configure static on host 192.168.3.1/255.255.255.0/192.168.3.1
  ping 192.168.3.2
  ssh pprz@192.168.3.2


docker commit jetpackcontainer jetpackimage
docker image ls
jetpackimage  62.9GB

------------------------------------------------------------------------
5)

sdkmanager --cli downloadonly --logintype devzone --product Jetson --target JETSON_XAVIER_NX_TARGETS --targetos Linux --version 4.6 --deselect 'Jetson OS' --select 'Jetson SDK Components' --license accept --staylogin true --datacollection enable

sdkmanager --cli install --logintype devzone --product Jetson --target JETSON_XAVIER_NX_TARGETS --targetos Linux --version 4.6 --deselect 'Jetson OS' --select 'Jetson SDK Components' --license accept --staylogin true --datacollection enable

Install / Connect via Ethernet / IPV4 / 192.168.3.2 / pprz / pprz
