...

------------------------------------------------------------------------
2)

docker system prune

docker run --name jetpackcontainer --privileged -v /dev/bus/usb:/dev/bus/usb/ -v /dev:/dev jetpackimage

docker exec -it jetpackcontainer /bin/bash

2.1)
sdkmanager --cli downloadonly --logintype devzone --product Jetson --target JETSON_XAVIER_NX_TARGETS --targetos Linux --version 4.6 --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --staylogin true --datacollection enable

2.2)
sdkmanager --cli install --logintype devzone --product Jetson --target JETSON_XAVIER_NX_TARGETS --targetos Linux --version 4.6 --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --staylogin true --datacollection enable --flash skip


https://connecttech.com/product/quark-carrier-nvidia-jetson-xavier-nx/
JetPack 4.6.2 – L4T r32.7.2 22-June-22
CTI-L4T-XAVIER-NX-32.7.2-V003.tgz (500 Mb)

docker ps
=> 8249511561ad   jetpackimage 
docker cp CTI-L4T-XAVIER-NX-32.7.2-V003.tgz 8249511561ad:/home/jetpack/nvidia/nvidia_sdk/JetPack_4.6_Linux_JETSON_XAVIER_NX_TARGETS/Linux_for_Tegra

tar -xzf CTI-L4T-XAVIER-NX-32.7.2-V003.tgz
rm CTI-L4T-XAVIER-NX-32.7.2-V003.tgz 
cd ./CTI-L4T
sudo ./install.sh


docker image ls
jetpackimage  30.4GB

docker commit jetpackcontainer jetpackimage

docker image ls
jetpackimage  38.1GB


2.3)
cd /home/jetpack/nvidia/nvidia_sdk/JetPack_4.6_Linux_JETSON_XAVIER_NX_TARGETS/Linux_for_Tegra

sudo ./flash.sh --no-flash cti/xavier-nx/quark/rpi-imx219 mmcblk0p1


Jetson Xavier NX + Quark (Connecttech carrier board)
flash eMMC(16 GB)

 1.Connect USB-C
 2.PowerOn
=> Green leds fixed

 3.Press Recovery Button (>10sec) 
dmesg -w 
=> Product: APX
   (no /dev/ttyUSB0, no ttyACMx)

 4.Flash 
  First xavierNx flash eMMC(16 GB) (without SD-CARD)
  (10 minutes to flash all partitions)

sudo ./flash.sh cti/xavier-nx/quark/rpi-imx219 mmcblk0p1
=> Reset the board to boot from internal eMMC.

 5.PowerOff
 6.Plug UART/USB(FTDI) adapter

screen /dev/ttyUSB0 115200

 7.PowerOn
 8.Wait 30sec firstboot

=> system configuration setup on the serial port provided by Jetson's USB device mode connection. 
e.g. /dev/ttyUSBx where x can 0, 1, 2 etc.

 9.escape

  10.Initial oem-config 
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
