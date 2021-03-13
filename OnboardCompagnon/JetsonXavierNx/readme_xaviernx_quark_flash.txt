VMware Ubuntu1804 50Gb 1Gb  2 CPU USB-3 NAT (one single file)
(ubuntu-18.04.5-live-server-amd64.iso)
Network,French (keyboard), Open-ssh server
Options after setup: Shared folders 

(sudo mkdir /mnt/hgfs)
(sudo vmhgfs-fuse .host:/ /mnt/hgfs -o allow_other)

(sudo dhcpclient ens33)

ip address
ssh pprz@
sudo apt-get update
sudo apt-get install qemu-user-static binutils python

---------------------------------------------------------------------------------------
sudo lvm 
lvm> lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
lvm> exit
resize2fs /dev/ubuntu-vg/ubuntu-lv

---------------------------------------------------------------------------------------
https://connecttech.com/resource-center/l4t-board-support-packages/
https://connecttech.com/ftp/Drivers/CTI-L4T-XAVIER-NX-32.5-V001.tgz

From CTI-L4T-XAVIER-NX-32.5-V001/readme.txt
"
=> Install JetPack from NVIDIA's Source packages
1. Go to https://developer.nvidia.com/embedded/linux-tegra  
   download the "L4T Driver Package (BSP)" and "Sample Root Filesystem" files for Xavier NX. 
     ("Tegra186_Linux_R32.5.0_aarch64.tbz2", "Tegra_Linux_Sample-Root-Filesystem_R32.5.0_aarch64.tbz2")

2. Create a directory named ~/nvidia/nvidia_sdk/JetPack_4.5_Linux_JETSON_XAVIER_NX_DEVKIT/ 
   copy the "Tegra186_Linux_R32.5.0_aarch64.tbz2" file you downloaded into that directory.

3. Unzip the tarball with "sudo tar jxf Tegra186_Linux_R32.5.0_aarch64.tbz2". 
   You should now have a new directory called Linux_for_Tegra in your folder. 
   Change directories into that and then copy the "Tegra_Linux_Sample-Root-Filesystem_R32.5.0_aarch64.tbz2" 
   file you downloaded into the rootfs folder.

4. Change into the rootfs folder and unzip the tarball with 
   "sudo tar jxf Tegra_Linux_Sample-Root-Filesystem_R32.5.0_aarch64.tbz2" 

5. You can change directories back to 
   ~/nvidia/nvidia_sdk/JetPack_4.5_Linux_JETSON_XAVIER_NX_DEVKIT/Linux_for_Tegra/ and 
   - run "sudo ./apply_binaries.sh" if you wish to flash one of NVIDIA's devkits, 
   - or move on to installing CTI's BSP with the instructions below.
"
"
=> Install BSP in Jetpack
1. Copy the CTI-L4T-XAVIER-NX-32.5-V###.tgz package into
   ~/nvidia/nvidia_sdk/JetPack_4.5_Linux_JETSON_XAVIER_NX_DEVKIT/Linux_for_Tegra/

2. Extract the BSP:
   tar -xzf CTI-L4T-XAVIER-NX-32.5-V###.tgz

3. Change into the CTI-L4T directory:
   cd ./CTI-L4T

4. Run the install script (as root or sudo) to automatically install the BSP files to the correct locations:
   sudo ./install.sh
   cd ..

5. The CTI-L4T BSP is now installed on the host system and it should now be able to flash the Xavier-NX.

6. To flash on the Xavier-NX use the following (do not add ".conf"):
   CTI Assisted Flashing:  sudo ./cti-flash.sh
   Manual Flash:  sudo ./flash.sh cti/xavier-nx/quark mmcblk0p1
"
cd ..
sudo ./flash.sh --no-flash cti/xavier-nx/quark-imx219 mmcblk0p1
sudo ./flash.sh cti/xavier-nx/quark-imx219 mmcblk0p1
(30 min)

-------------------------------------------------------------------------
(*)
Plug USB-C 
Press recovery mode button
PowerON Xavier
(0.29mmA)
Virtual Machine / Removal devices / NVIDIA APX (connect / disconnect from host)

(**)
Connect FTDI (USB <-> UART)
screen /dev/ttyUSB0 115200
minicom -D /dev/ttyUSB0 -8 -b 115200
PowerOn Nvidia
Tab,Escape ..

(***)
Connect ETH
ssh pprz@192.168.3.2

-------------------------------------------------------------------------
Share wireless internet with ethernet

Ubuntu
sudo sysctl net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -o wlp59s0 -j MASQUERADE

Jetpack 
/etc/NetworkManager/system-connections
dns=8.8.8.8,8.8.4.4

