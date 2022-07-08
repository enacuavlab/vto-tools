This will use the docker image to run nvidia sdkmanager
(Nvidia developper account and web connection needed)
------------------------------------------------------

docker system prune

1a) 
docker run --name jetpackcontainer --privileged -v /dev/bus/usb:/dev/bus/usb/ -v /dev:/dev jetpackimage
(keep running for executions below)

1b)
docker exec -it jetpackcontainer /bin/bash
(run sdkmanager commands below within this bash)

------------------------------------------------------------------------
2) For Jetson nano 

sdkmanager --cli downloadonly --logintype devzone --product Jetson --version 4.6 --targetos Linux --target JETSON_NANO_TARGETS --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --staylogin true

open url link to NVIDIA account
login & confirm

docker image ls
jetpackimage   latest    6b3f68fb6f84   9 minutes ago   944MB
ubuntu         18.04     ad080923604a   4 weeks ago     63.1MB

sdkmanager --cli install --logintype devzone --product Jetson --version 4.6 --targetos Linux --target JETSON_NANO_TARGETS --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --staylogin true --flash skip

docker commit jetpackcontainer jetpackimage

-----------------------------------------------------------------------
sudo du -h ./Docker
21	./Docker

docker image ls
REPOSITORY     TAG       IMAGE ID       CREATED          SIZE
jetpackimage   latest    be67b51ee0c9   18 seconds ago   7.62GB

------------------------------------------------------------------------
4)
Jetson Nano Developer Kit = Jetson module (P3448-0000) + carrier board (P3449-0000)
Jetson Nano Developer Kit (part number 945-13450-0000-000), which includes carrier board revision A02)

 1.Jumper the Force Recovery pins FRC (3 and 4) on J40 button header
 2.Connect only microUSB  (power + data)
   (dmesg => APX)
   (lsusb => NVIDIA Corp. APX)
   
------------------------------------------------------------------------
------------------------------------------------------------------------
5)
cd /home/jetpack/nvidia/nvidia_sdk/JetPack_4.6_Linux_JETSON_NANO_TARGETS/Linux_for_Tegra
sudo ./flash.sh jetson-nano-qspi-sd mmcblk0p1
=> 10 minutes to write 19 partitions !!


docker commit jetpackcontainer jetpackimage

sudo du -h ./Docker
112G	./Docker

docker image ls
REPOSITORY     TAG       IMAGE ID       CREATED         SIZE
jetpackimage   latest    747a52b35594   2 minutes ago   27.8GB
ubuntu         18.04     ad080923604a   5 days ago      63.1MB


------------------------------------------------------------------------
------------------------------------------------------------------------
After flash completed, the board reboot by itself and 
-Notification L4T-README
-Ethernet USB0, NVIDIA Off

sudo screen /dev/ttyACM0 115200
(escape key)
=> System Configuration
user:pprz
password:pprz

Do not configure network
leave default network conf

Install system

Ethernet eth0 static IP 192.168.3.2,...

NVIDIA can be connected with screen or ssh 
ssh pprz@192.168.3.2


------------------------------------------------------------------------
------------------------------------------------------------------------
5)
ssh pprz@192.168.3.2
exit

sdkmanager --cli downloadonly --logintype devzone --product Jetson --target JETSON_NANO_TARGETS --targetos Linux --version 4.6 --deselect 'Jetson OS' --select 'Jetson SDK Components' --license accept --staylogin true

CUDA, CUDA-X AI, Computer Vision, NVIDIA Container Runtime, Multimedia, Developer Tools

sudo du -h /home/pprz/Docker
120G	./Docker

docker commit jetpackcontainer jetpackimage

sdkmanager --cli install --logintype devzone --product Jetson --target JETSON_NANO_TARGETS --targetos Linux --version 4.6 --deselect 'Jetson OS' --select 'Jetson SDK Components' --license accept --staylogin true

!!!!
Not internet connection 
ping nvidia.com
!!!!

docker image ls
REPOSITORY     TAG       IMAGE ID       CREATED         SIZE
jetpackimage   latest    6d125dfab4a0   4 minutes ago   62.2GB
ubuntu         18.04     ad080923604a   4 weeks ago     63.1MB


------------------------------------------------------------------------
------------------------------------------------------------------------
5)
export DOCKERCMD="docker exec -it jetpackcontainer"

export SDKCMD=(sdkmanager --cli install --logintype devzone --product Jetson --target JETSON_NANO_TARGETS --targetos Linux --version 4.6 --deselect 'Jetson OS' --select 'Jetson SDK Components' --license accept --staylogin true --datacollection enable)

$DOCKERCMD "${SDKCMD[@]}"

