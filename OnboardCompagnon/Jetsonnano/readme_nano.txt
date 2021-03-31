VMware Ubuntu1804 50Gb 2Gb  2 CPU USB-3 NAT (one single file)
(ubuntu-18.04.5-live-server-amd64.iso)
Network,French (keyboard), Open-ssh server, no proxy

Options after setup: Shared folders (read & write)

(sudo mkdir /mnt/hgfs
sudo vmhgfs-fuse .host:/ /mnt/hgfs -o allow_other)

(sudo dhcpclient ens33)

ip address
ssh pprz@
sudo apt-get update
sudo apt-get upgrade

---------------------------------------------------------------------------------------
sudo lvm 
lvm> lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
lvm> exit
sudo resize2fs /dev/ubuntu-vg/ubuntu-lv

---------------------------------------------------------------------------------------
ssh pprz@192.168.x.y
sudo apt-get install /mnt/hgfs/vmshare/nvidia/sdkmanager_1.4.1-7402_amd64.deb 

Internet connection needed without proxy or you'll get
"Session expired. Please log in again", instead of
"SDK Manager is waiting for you to complete login."
(use browser to internet on another machine for credentials)

Jetson Nano (Developer Kit version) (P3448-0000)   
Jetson Xavier NX (Developer Kit version) (P3668-0000) 

sdkmanager --cli downloadonly --logintype devzone --targetos Linux --product Jetson --version 4.5 --target=P3448-0000 --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --downloadfolder /mnt/hgfs/vmshare/nvidia/Downloads/nvidia/os_sdkm_downloads
=> Downloads/nvidia/os_sdkm_downloads (1.7Gb)

sdkmanager --cli install --logintype devzone --targetos Linux --product Jetson --version 4.5 --target P3448-0000 --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --offline --downloadfolder /mnt/hgfs/vmshare/nvidia/Downloads/nvidia/os_sdkm_downloads

=> TARGET COMPONENTS:
  - Jetson OS
    - Jetson OS image          OS image ready
        - Drivers for jetson : OS image ready
        - File System and OS : OS image ready

/home/pprz/nvidia/nvidia_sdk/JetPack_4.5_Linux_JETSON_NANO_DEVKIT/Linux_for_Tegra/tools
sudo ./jetson-disk-image-creator.sh -o sd-blob.img -b jetson-nano -r 200
=> sd-blob.img (5.2Gb)

Virtual machine / Removal devices
sudo dd if=sd-blob.img of=/dev/sd? bs=1M oflag=direct

-------------------------------------------------------------------------
First boot with USB keyboard, mouse, HDMI display
Configure static IP
192.168.3.2
255.255.255.0
192.168.3.1
8.8.8.8

-------------------------------------------------------------------------
ssh pprz@192.168.3.2


-------------------------------------------------------------------------
-------------------------------------------------------------------------
ssh pprz@192.168.x.y

https://developer.nvidia.com/embedded/linux-tegra

wget https://developer.nvidia.com/embedded/l4t/r32_release_v5.1/r32_release_v5.1/t210/jetson-210_linux_r32.5.1_aarch64.tbz2
wget https://developer.nvidia.com/embedded/l4t/r32_release_v5.1/r32_release_v5.1/sources/t210/public_sources.tbz2
wget https://developer.nvidia.com/embedded/l4t/r32_release_v5.1/r32_release_v5.1/t210/tegra_linux_sample-root-filesystem_r32.5.1_aarch64.tbz2
(1.4Gb)

git clone https://github.com/alliedvision/linux_nvidia_jetson.git
(without proxy)

mkdir /home/pprz/linux_nvidia_jetson/avt_build/resources/driverPackage
mkdir /home/pprz/linux_nvidia_jetson/avt_build/resources/gcc

cp jetson-210_linux_r32.5.1_aarch64.tbz2 ~/linux_nvidia_jetson/avt_build/ressources/driverPackage
cp public_sources.tbz2 ~/linux_nvidia_jetson/avt_build/ressources/public_sources
cp tegra_linux_sample-root-filesystem_r32.5.1_aarch64.tbz2 ~/linux_nvidia_jetson/avt_build/resources/rootf
cp gcc-linaro-7.3.1-2018.05-x86_64_aarch64-linux-gnu.tar.xz ~/linux_nvidia_jetson/avt_build/resources/gcc

setup.sh
FILE_DRIVER_PACKAGE_NANO="jetson-210_linux_r32.5.1_aarch64.tbz2"
FILE_ROOTFS_NANO="tegra_linux_sample-root-filesystem_r32.5.1_aarch64.tbz2"
FILE_PUBLICSOURCES_NANO="public_sources.tbz2"
FILE_GCC_64="gcc-linaro-7.3.1-2018.05-x86_64_aarch64-linux-gnu.tar.xz"

deploy.sh
DEDICATED_VERSION="32.5.1"

./setup.sh workdir nano
./build.sh workdir nano all all
./deploy.sh workdir nano tarball
=> AlliedVision_NVidia_nano_L4T_32.5.1_4.9.140-g84fcaed28.tar.gz (30Mb)

Copy the tarball to the target board. Extract the tarball.

sudo cp tegra210-p3448-0000-p3449-0000-a02.dtb /boot/avt_tegra210-p3448-0000-p3449-0000-a02.dtb
sudo cp Image /boot/avt_Image
sudo tar zxf modules.tar.gz -C /

/boot/extlinux/extlinux.conf
      LINUX /boot/avt_Image
      FDT /boot/avt_tegra210-p3448-0000-p3449-0000-a02.dtb

Reboot the board.
(dtc -s -I fs /proc/device-tree -O dts > log)


-------------------------------------------------------------------------

sdkmanager --cli downloadonly --logintype devzone --targetos Linux --product Jetson --version 4.5 --target=P3448-0000 --deselect 'Jetson OS' --select 'Jetson SDK Components' --license accept --downloadfolder /mnt/hgfs/vmshare/nvidia/Downloads/nvidia/cmp_sdkm_downloads

wireless internet & ethernet
ping www.google.com

sdkmanager --cli install --logintype devzone --targetos Linux --product Jetson --version 4.5 --target P3448-0000 --deselect 'Jetson OS' --select 'Jetson SDK Components' --license accept --offline --downloadfolder /mnt/hgfs/vmshare/nvidia/Downloads/nvidia/cmp_sdkm_downloads


-------------------------------------------------------------------------
-------------------------------------------------------------------------
Share wireless internet with ethernet

Ubuntu
sudo sysctl net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -o wlp59s0 -j MASQUERADE

Jetpack 
/etc/NetworkManager/system-connections
dns=8.8.8.8,8.8.4.4

