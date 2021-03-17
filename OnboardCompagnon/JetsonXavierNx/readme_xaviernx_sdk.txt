VMware Ubuntu1804 40Gb 2Gb  2 CPU USB-3 NAT (one single file)
(ubuntu-18.04.5-live-server-amd64.iso)
Network,French (keyboard), Open-ssh server
Options after setup: Shared folders (read & write)

(sudo mkdir /mnt/hgfs)
(sudo vmhgfs-fuse .host:/ /mnt/hgfs -o allow_other)

(sudo dhcpclient ens33)

ip address
ssh pprz@
sudo apt-get update

---------------------------------------------------------------------------------------
sudo lvm 
lvm> lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
lvm> exit
sudo resize2fs /dev/ubuntu-vg/ubuntu-lv

---------------------------------------------------------------------------------------
sudo apt-get install /mnt/hgfs/vmshare/sdkmanager_1.4.1-7402_amd64.deb 

Internet connection needed
(+ browser on another machine for credentials)

sdkmanager --cli downloadonly --logintype devzone --product Jetson  --host --target P3668-0000 --targetos Linux --version 4.5 --flash skip  --license accept  --downloadfolder /mnt/hgfs/vmshare/Downloads/nvidia/sdkm_downloads

=> All green Downloaded
=> Downloads/nvidia/sdkm_downloads (6.9Gb)

sdkmanager --cli install --logintype devzone --product Jetson  --host --target P3668-0000 --targetos Linux --version 4.5  --flash skip  --license accept  --offline  --downloadfolder /mnt/hgfs/vmshare/Downloads/nvidia/sdkm_downloads

=> HOST COMPONENTS: Installed
=> TARGET COMPONENTS:
  - Jetson OS: OS image ready
  - Jetson SDK Components: Install Pending


---------------------------------------------------------------------------------------
https://connecttech.com/resource-center/l4t-board-support-packages/
https://connecttech.com/ftp/Drivers/CTI-L4T-XAVIER-NX-32.5-V001.tgz

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
(45 min)

(*)
Plug USB-C 
Press recovery mode button (>10sec)
PowerON Xavier
(0.29mmA)
Virtual Machine / Removal devices / NVIDIA APX (connect / disconnect from host)

(**)
Connect FTDI (USB <-> UART)
screen /dev/ttyUSB0 115200
PowerOn Nvidia
Tab,Escape ..

(***)
Connect ETH
ssh pprz@192.168.3.2

-------------------------------------------------------------------------
With already flashed OS, install SDK components via Ethernet and USB
SSH IP address
=> 

sdkmanager --cli install --logintype devzone --product Jetson  --host --target P3668-0000 --targetos Linux --version 4.5  --flash skip  --license accept  --offline  --downloadfolder /mnt/hgfs/vmshare/Downloads/nvidia/sdkm_downloads


-------------------------------------------------------------------------
-------------------------------------------------------------------------
Share wireless internet with ethernet

Ubuntu
sudo sysctl net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -o wlp59s0 -j MASQUERADE

Jetpack 
/etc/NetworkManager/system-connections
dns=8.8.8.8,8.8.4.4

