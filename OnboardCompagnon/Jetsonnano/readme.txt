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

sdkmanager --cli downloadonly --logintype devzone --targetos Linux --product Jetson --version 4.5 --target=P3448-0000 --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --downloadfolder /mnt/hgfs/vmshare/nvidia/Downloads/nvidia/sdkm_downloads
=> Downloads/nvidia/sdkm_downloads (1.7Gb)

sdkmanager --cli install --logintype devzone --targetos Linux --product Jetson --version 4.5 --target P3448-0000 --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --offline --downloadfolder /mnt/hgfs/vmshare/nvidia/Downloads/nvidia/sdkm_downloads

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

wget https://developer.nvidia.com/embedded/L4T/r32_Release_v4.2/Sources/T210/public_sources.tbz2
wget https://developer.nvidia.com/embedded/L4T/r32_Release_v4.2/t210ref_release_aarch64/Tegra210_Linux_R32.4.2_aarch64.tbz2
wget https://developer.nvidia.com/embedded/L4T/r32_Release_v4.2/t210ref_release_aarch64/Tegra_Linux_Sample-Root-Filesystem_32.4.2_aarch64.tbz2
wget http://releases.linaro.org/components/toolchain/binaries/7.3-2018.05/aarch64-linux-gnu/gcc-linaro-7.3.1-2018.05-x86_64_aarch64-linux-gnu.tar.xz

git clone https://github.com/alliedvision/linux_nvidia_jetson.git

mkdir /home/pprz/linux_nvidia_jetson/avt_build/resources/driverPackage
mkdir /home/pprz/linux_nvidia_jetson/avt_build/resources/gcc

/home/pprz/linux_nvidia_jetson/avt_build/resources/
  rootfs/Tegra_Linux_Sample-Root-Filesystem_R32.4.2_aarch64.tbz2
  driverPackage/Tegra210_Linux_32.4.2_aarch64.tbz2
  public_sources/T210/public_sources.tbz2
  gcc/gcc-linaro-7.3.1-2018.05-x86_64_aarch64-linux-gnu.tar.xz

./setup.sh workdir nano
./build.sh workdir nano all all
./deploy.sh workdir nano tarball
=> AlliedVision_NVidia_nano_L4T_32.4.4_4.9.140-g84fcaed28.tar.gz (30Mb)

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
-------------------------------------------------------------------------
Share wireless internet with ethernet

Ubuntu
sudo sysctl net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -o wlp59s0 -j MASQUERADE

Jetpack 
/etc/NetworkManager/system-connections
dns=8.8.8.8,8.8.4.4

