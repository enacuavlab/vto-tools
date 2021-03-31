The hardware configurations of CTI’s products differ from that of the NVIDIA supplied evaluation kit
Install only CTI L4T BSP
Each CTI product use a modified Linux for Tegra (L4T) Device Tree

Board Support Package (BSP)


-------------------------------------------------------------------------------
Create virtual Ubuntu1804-srv1
-------------------------------
VMware Ubuntu1804 40Gb 2Gb  6CPU USB-3 NAT
(ubuntu-18.04.5-live-server-amd64.iso)
Options after setup: Shared folders 
sudo mkdir /mnt/hgfs
sudo vmhgfs-fuse .host:/ /mnt/hgfs -o allow_other

(sudo dhcpclient ens33)
sudo apt-get update
sudo apt-get upgrade

sudo apt-get install python qemu-user-static


Install nvidia tools L4T + tegra linux sample root filesystem
------------------------------------------------------------
Subscribe to nvidia and download 
https://developer.nvidia.com/embedded/linux-tegra
- "L4T Driver Package (BSP)" 
  https://developer.nvidia.com/embedded/L4T/r32_Release_v4.4/r32_Release_v4.4-GMC3/T186/  
    Tegra186_Linux_R32.4.4_aarch64.tbz2 (300,2Mo)
- "Sample Root Filesystem"
  https://developer.nvidia.com/embedded/L4T/r32_Release_v4.4/r32_Release_v4.4-GMC3/T186/
    Tegra_Linux_Sample-Root-Filesystem_R32.4.4_aarch64.tbz2 (1.4Go)

L4T_SDK=/home/pprz/l4t_sdk
mkdir $L4T_SDK
sudo tar xf /mnt/hgfs/share/Tegra186_Linux_R32.4.4_aarch64.tbz2 -C $L4T_SDK
L4T_KERNEL=$L4T_SDK/Linux_for_Tegra
sudo tar xf /mnt/hgfs/share/Tegra_Linux_Sample-Root-Filesystem_R32.4.4_aarch64.tbz2 -C $L4T_KERNEL/rootfs
('sudo' is mandatory)

cd $L4T_KERNEL
sudo ./apply_binaries.sh

(suite...)

flash all system/partitions 
sudo ./flash.sh jetson-xavier-nx-devkit-emmc mmcblk0p1
(sudo ./flash.sh --no-flash jetson-xavier-nx-devkit-emmc mmcblk0p1)

uname -a
Linux xavier 4.9.140-tegra #1 SMP PREEMPT Fri Oct 16 12:25:00 PDT 2020 aarch64 aarch64 aarch64 GNU/Linux


Optionnal after flashing all system
-----------------------------------
sudo ./flash.sh -r -k kernel-dtb jetson-xavier-nx-devkit-emmc mmcblk0p1
cd kernel
scp Image pprz@192.168.3.2:/home/pprz
sudo mv Image /boot

-------------------------------------------------------------------------
Install connect tech 
--------------------
https://connecttech.com/resource-center/l4t-board-support-packages/
https://connecttech.com/ftp/Drivers/CTI-L4T-XAVIER-NX-32.4.4-V001.tgz (491,9Mo)

/*
cd Linux_For_Tegra
tar xf /mnt/hgfs/tmp/CTI-L4T-XAVIER-NX-32.4.4-V001.tgz 
cd CTI-L4T
sudo ./install.sh
*/


cd ..
sudo ./flash.sh cti/xavier-nx/quark-imx219 mmcblk0p1
(sudo ./flash.sh --no-flash cti/xavier-nx/quark mmcblk0p1)


-------------------------------------------------------------------------
(*)Plug USB-C 
PowerON Xavier
Press recovery mode button at least 10 sec.
Virtual Machine / Removal devices / NVIDIA APX (connect / disconnect from host)

(**)Connect FTDI (USB <-> UART)
screen /dev/ttyUSB0 115200
minicom -D /dev/ttyUSB0 -8 -b 115200
PowerOn Nvidia
Tab,Escape ..

(***)Connect ETH
ssh pprz@192.168.3.2

-------------------------------------------------------------------------
-------------------------------------------------------------------------

(...suite)

(https://developer.ridgerun.com/wiki/index.php?title=Compiling_Jetson_Xavier_NX_source_code_L4T_32.4.3)
https://developer.nvidia.com/embedded/linux-tegra
- "L4T Driver Package (BSP) Sources" 
  https://developer.nvidia.com/embedded/L4T/r32_Release_v4.4/r32_Release_v4.4-GMC3/Sources/T186/
    public_sources.tbz2 (176.1Mo)

L4T_SRC=/home/pprz/l4t_src
mkdir $L4T_SRC
tar xf /mnt/hgfs/share/public_sources.tbz2 -C $L4T_SRC
KERNEL_SRC=$L4T_SRC/Linux_for_Tegra/source/public
tar xf $KERNEL_SRC/kernel_src.tbz2 -C $KERNEL_SRC 

sudo apt-get install build-essential libncurses-dev bison flex libssl-dev libelf-dev gcc-aarch64-linux-gnu
sudo apt-get install python qemu-user-static

KERNEL=$KERNEL_SRC/kernel/kernel-4.9
BUILD=$KERNEL_SRC/build
make -C $KERNEL ARCH=arm64 O=$BUILD CROSS_COMPILE=aarch64-linux-gnu- tegra_defconfig
make -C $KERNEL ARCH=arm64 O=$BUILD CROSS_COMPILE=aarch64-linux-gnu- menuconfig

make -C $KERNEL ARCH=arm64 O=$BUILD CROSS_COMPILE=aarch64-linux-gnu- -j6 Image
make -C $KERNEL ARCH=arm64 O=$BUILD CROSS_COMPILE=aarch64-linux-gnu- -j6 dtbs
make -C $KERNEL ARCH=arm64 O=$BUILD CROSS_COMPILE=aarch64-linux-gnu- -j6 modules

MOD=$KERNEL_SRC/modules
make -C $KERNEL ARCH=arm64 O=$BUILD INSTALL_MOD_PATH=$MOD modules_install


cp -rfv $KERNEL_SRC/build/arch/arm64/boot/Image $L4T_KERNEL/kernel
cp -rfv $KERNEL_SRC/build/arch/arm64/boot/dts/* $L4T_KERNEL/kernel/dtb
sudo cp -arfv $KERNEL_SRC/modules/lib $L4T_KERNEL/rootfs

sudo ./flash.sh jetson-xavier-nx-devkit-emmc mmcblk0p1
(sudo ./flash.sh --no-flash jetson-xavier-nx-devkit-emmc mmcblk0p1)

uname -a
Linux xavier 4.9.140 #1 SMP PREEMPT Mon Nov 23 15:04:33 UTC 2020 aarch64 aarch64 aarch64 GNU/Linux


-------------------------------------------------------------------------
-------------------------------------------------------------------------
RPI Camera V2 (IMX219)

gst-launch-1.0 nvarguscamerasrc sensor-id=1  ! 'video/x-raw(memory:NVMM), width=640, height=480, framerate=30/1' ! omxh264enc ! video/x-h264, stream-format=byte-stream ! rtph264pay mtu=1400 ! udpsink host=192.168.1.1 port=5000 sync=false async=false

gst-launch-1.0 udpsrc port=5000 ! application/x-rtp,encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! queue ! avdec_h264 ! xvimagesink sync=false async=false -e


ALVIUM 1800C-240 (IMX392)

gst-launch-1.0 v4l2src device=/dev/video0   ! video/x-raw, format=BGRx
?! 'video/x-raw(memory:NVMM), width=640, height=480, framerate=30/1' ! omxh264enc ! video/x-h264, stream-format=byte-stream ! rtph264pay mtu=1400 ! udpsink host=192.168.1.1 port=5000 sync=false async=false

gst-launch-1.0 udpsrc port=5000 ! application/x-rtp,encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! queue ! avdec_h264 ! xvimagesink sync=false async=false -e

-------------------------------------------------------------------------------
Inspired by:
https://anastas.io/embedded/linux/2020/06/01/mainline-linux-xavier.html
https://developer.ridgerun.com/wiki/index.php?title=Compiling_Jetson_Xavier_NX_source_code_L4T_32.4.3



