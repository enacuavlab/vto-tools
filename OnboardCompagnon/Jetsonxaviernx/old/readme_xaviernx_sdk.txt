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

---------------------------------------------------------------------------------------
sudo lvm 
lvm> lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
lvm> exit
sudo resize2fs /dev/ubuntu-vg/ubuntu-lv

---------------------------------------------------------------------------------------
sudo apt-get install /mnt/hgfs/vmshare/sdkmanager_1.4.1-7402_amd64.deb 

Internet connection needed without proxy or you'll get
"Session expired. Please log in again", instead of
"SDK Manager is waiting for you to complete login."
(use browser to internet on another machine for credentials)

sdkmanager --cli downloadonly --logintype devzone --product Jetson  --host --target P3668-0000 --targetos Linux --version 4.5 --flash skip  --license accept  --downloadfolder /mnt/hgfs/vmshare/Downloads/nvidia/sdkm_downloads
=> All green Downloaded
=> Downloads/nvidia/sdkm_downloads (6.9Gb)

sdkmanager --cli install --logintype devzone --targetos Linux --product Jetson --version 4.5 --target=P3448-0000 --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --offline --downloadfolder /mnt/hgfs/vmshare/nvidia/Downloads/nvidia/sdkm_downloads


=> HOST COMPONENTS: Installed
=> TARGET COMPONENTS:
  - Jetson OS: OS image ready
  - Jetson SDK Components: Install Pending


---------------------------------------------------------------------------------------
https://connecttech.com/resource-center/l4t-board-support-packages/
https://connecttech.com/ftp/Drivers/CTI-L4T-XAVIER-NX-32.5-V001.tgz
                                    CTI-L4T-XAVIER-NX-AVT-32.5-V002.tgz

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
sudo ./flash.sh cti/xavier-nx/quark-avt mmcblk0p1
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
Option to switch camera type

Unchange kernel-dtb partition previously flashed with tegra194-xavier-nx-cti-NGX004-AVT-2CAM.dtb
and add alternate DTB in boot file:

/boot/extlinux/extlinux.conf

      FDT /boot/tegra194-xavier-nx-cti-NGX004-IMX219-2CAM.dtb
      APPEND ...

(nano dev kit with IMX219 or from allied vision same file name 
FDT /boot/tegra210-p3448-0000-p3449-0000-a02.dtb
)

-------------------------------------------------------------------------
sudo fdisk -l |grep GiB
=>
Disk /dev/mmcblk1: 29.7 GiB, 31914983424 bytes, 62333952 sectors
Disk /dev/mmcblk0: 14.7 GiB, 15758000128 bytes, 30777344 sectors

sudo blkid
=> 
/dev/mmcblk1p1: UUID="cb377b7d-54dd-4e02-95d6-2fb06ca806c5" TYPE="ext4" PARTUUID="3be52ecb-01"

/etc/fstab
UUID=cb377b7d-54dd-4e02-95d6-2fb06ca806c5       /alt    ext4    defaults        0 2

sudo mkdir /alt
sudo mount -a
cd /usr
sudo mv local share src /alt
sudo ln -s /alt/* .
sudo sync
sudo reboot

sudo apt-get update
sudo apt install python3-pip
sudo apt-get install libhdf5-serial-dev hdf5-tools libhdf5-dev zlib1g-dev zip libjpeg8-dev liblapack-dev libblas-dev gfortran

sudo pip3 install -U pip testresources setuptools==49.6.0
sudo pip3 install -U numpy==1.19.4 future==0.18.2 mock==3.0.5 h5py==2.10.0 keras_preprocessing==1.1.1 keras_applications==1.0.8 gast==0.2.2 futures protobuf pybind11
sudo pip3 install --pre --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v45 tensorflow
       pip3 install torch
   48  pip3 install torchvision
   49  pip3 install torchaudio
   50  df
   51  python3
sudo pip3 install torch
sudo pip3 install torchvision
   54  pip3 install serial

-------------------------------------------------------------------------
With already flashed OS, install SDK components via Ethernet and USB
SSH IP address
=> 

sdkmanager --cli install --logintype devzone --product Jetson  --host --target P3668-0000 --targetos Linux --version 4.5  --flash skip  --license accept  --offline  --downloadfolder /mnt/hgfs/vmshare/Downloads/nvidia/sdkm_downloads

>>>> ERROR <<<<

-------------------------------------------------------------------------
-------------------------------------------------------------------------
Share wireless internet with ethernet

Ubuntu
sudo sysctl net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -o wlp59s0 -j MASQUERADE

Jetpack 
/etc/NetworkManager/system-connections
dns=8.8.8.8,8.8.4.4

