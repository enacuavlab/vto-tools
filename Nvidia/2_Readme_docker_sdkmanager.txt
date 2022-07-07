-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
B) Build and run DOCKER with NVIDIA sdkmanager inside
(Nvidia developper account and web connection needed)
-----------------------------------------------------
1) 
docker system prune

docker build --build-arg GID=$(id -g) --build-arg UID=$(id -u) -t jetpackimage .

docker image ls
REPOSITORY     TAG       IMAGE ID       CREATED          SIZE
jetpackimage   latest    de1f14d30c6e   33 seconds ago   735MB
ubuntu         18.04     ad080923604a   5 days ago       63.1MB

docker run --name jetpackcontainer --privileged -v /dev/bus/usb:/dev/bus/usb/ -v /dev:/dev jetpackimage
(keep running for executions below)

(docker system prune)

------------------------------------------------------------------------
2)
export DOCKERCMD="docker exec -it jetpackcontainer"

export SDKCMD=(sdkmanager --cli downloadonly --logintype devzone --product Jetson --target JETSON_NANO_TARGETS --targetos Linux --version 4.6 --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --staylogin true --datacollection enable)

$DOCKERCMD "${SDKCMD[@]}"

open url link to NVIDIA account
login & confirm

docker commit jetpackcontainer jetpackimage

docker image ls
REPOSITORY     TAG       IMAGE ID       CREATED         SIZE
jetpackimage   latest    976905aeeb6c   6 seconds ago   2.51GB
ubuntu         18.04     ad080923604a   5 days ago      63.1MB

------------------------------------------------------------------------
3)
export SDKCMD=(sdkmanager --cli install --logintype devzone --product Jetson --target JETSON_NANO_TARGETS --targetos Linux --version 4.6 --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --staylogin true --datacollection enable  --flash skip)

$DOCKERCMD "${SDKCMD[@]}"

docker commit jetpackcontainer jetpackimage

sudo du -h ./Docker
21	./Docker

docker image ls
REPOSITORY     TAG       IMAGE ID       CREATED          SIZE
jetpackimage   latest    be67b51ee0c9   18 seconds ago   7.62GB

------------------------------------------------------------------------
4)
docker exec -it jetpackcontainer /bin/bash

Jetson Nano Developer Kit = Jetson module (P3448-0000) + carrier board (P3449-0000)
Jetson Nano Developer Kit (part number 945-13450-0000-000), which includes carrier board revision A02)

 1.Jumper the Force Recovery pins FRC (3 and 4) on J40 button header
 2.Connect microUSB alone
   (dmesg => APX)
   (lsusb => NVIDIA Corp. APX)
   
------------------------------------------------------------------------
------------------------------------------------------------------------
5)
docker exec -it jetpackcontainer /bin/bash

cd /home/jetpack/nvidia/nvidia_sdk/JetPack_4.6_Linux_JETSON_NANO_TARGETS/Linux_for_Tegra;sudo ./flash.sh jetson-nano-qspi-sd mmcblk0p1
=> 10 minutes to write 19 partitions !!


#export SDKCMD=(sdkmanager --cli install --logintype devzone --product Jetson --target JETSON_NANO_TARGETS --targetos Linux --version 4.6 --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --staylogin true --datacollection enable --flash all)
#$DOCKERCMD "${SDKCMD[@]}"
#Could not detect correct NVIDIA jetson device connected

sudo du -h ./Docker
35G	./Docker

docker commit jetpackcontainer jetpackimage

sudo du -h ./Docker
53G	./Docker

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
=> System Configuration
user:pprz
password:pprz

Do not configure network
leave default network conf

Install system

Ethernet USB0 auto-connected with 192.168.55.1 on boot
(host 192.168.55.100)

NVIDIA can be connected with screen or ssh (ssh pprs@192.168.55.1)


------------------------------------------------------------------------
------------------------------------------------------------------------
5)
ssh pprz@192.168.55.1
exit


expor DOCKERCMD="docker exec -it jetpackcontainer"

export SDKCMD=(sdkmanager --cli downloadonly --logintype devzone --product Jetson --target JETSON_NANO_TARGETS --targetos Linux --version 4.6 --deselect 'Jetson OS' --select 'Jetson SDK Components' --license accept --staylogin true --datacollection enable)

$DOCKERCMD "${SDKCMD[@]}"

CUDA, CUDA-X AI, Computer Vision, NVIDIA Container Runtime, Multimedia, Developer Tools

sudo du -h ./Docker
58G	./Docker

docker commit jetpackcontainer jetpackimage

sudo du -h ./Docker
60G	./Docker

docker image ls
REPOSITORY     TAG       IMAGE ID       CREATED         SIZE
jetpackimage   latest    5fe81f911f5c   6 minutes ago   30.4GB

------------------------------------------------------------------------
------------------------------------------------------------------------
5)
export DOCKERCMD="docker exec -it jetpackcontainer"

export SDKCMD=(sdkmanager --cli install --logintype devzone --product Jetson --target JETSON_NANO_TARGETS --targetos Linux --version 4.6 --deselect 'Jetson OS' --select 'Jetson SDK Components' --license accept --staylogin true --datacollection enable)

$DOCKERCMD "${SDKCMD[@]}"

