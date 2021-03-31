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

sdkmanager --cli downloadonly --logintype devzone --targetos Linux --product Jetson --version 4.5.1 --target=P3668-0000 --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --downloadfolder /mnt/hgfs/vmshare/nvidia/Downloads/nvidia/os_sdkm_downloads
=> Downloads/nvidia/xaviernx_os_sdkm_downloads (2Gb)

sdkmanager --cli install --logintype devzone --targetos Linux --product Jetson --version 4.5.1 --target P3668-0000 --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --offline --downloadfolder /mnt/hgfs/vmshare/nvidia/Downloads/nvidia/os_sdkm_downloads

=> TARGET COMPONENTS:
  - Jetson OS
    - Jetson OS image          OS image ready
        - Drivers for jetson : OS image ready
        - File System and OS : OS image ready

---------------------------------------------------------------------------------------
https://connecttech.com/resource-center/l4t-board-support-packages/
https://connecttech.com/ftp/Drivers/CTI-L4T-XAVIER-NX-AVT-32.5-V002.tgz
(500mB)
                                  
cd ~/nvidia/nvidia_sdk/JetPack_4.5.1_Linux_JETSON_XAVIER_NX_DEVKIT/Linux_for_Tegra
cp /mnt/hgfs/vmshare/connecttech/CTI-L4T-XAVIER-NX-AVT-32.5-V002.tgz .
tar -xzf CTI-L4T-XAVIER-NX-AVT-32.5-V002.tgz
rm CTI-L4T-XAVIER-NX-AVT-32.5-V002.tgz
cd CTI-L4T
sudo ./install.sh

sudo apt-get install binutils

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
(name server:8.8.8.8)

(***)
Connect ETH
ssh pprz@192.168.3.2

---------------------------------------------------------------------------------------
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

-------------------------------------------------------------------------
sdkmanager --cli downloadonly --logintype devzone --targetos Linux --product Jetson --version 4.5.1 --target=P3668-0000 --deselect 'Jetson OS' --select 'Jetson SDK Components' --license accept --downloadfolder /mnt/hgfs/vmshare/nvidia/Downloads/nvidia/cmp_sdkm_downloads
(2.5G)

wireless internet & ethernet
from host & target ping www.google.com

sdkmanager --cli install --logintype devzone --targetos Linux --product Jetson --version 4.5.1 --target P3668-0000 --deselect 'Jetson OS' --select 'Jetson SDK Components' --license accept --offline --downloadfolder /mnt/hgfs/vmshare/nvidia/Downloads/nvidia/cmp_sdkm_downloads

      - OpenCV on Target: Failed
      - VisionWorks on Target: Failed
      - VPI on Target: Failed
      - NVIDIA Container Runtime with Docker integration (Beta): Failed

  ===== Installation failed - Total 11 components =====
  ===== 0 succeeded, 4 failed, 7 up-to-date, 0 skipped =====

-------------------------------------------------------------------------
sudo apt install python3-pip
sudo apt-get install libhdf5-serial-dev hdf5-tools libhdf5-dev zlib1g-dev zip libjpeg8-dev liblapack-dev libblas-dev gfortran

sudo pip3 install -U pip testresources setuptools==49.6.0
sudo pip3 install -U numpy==1.19.4 future==0.18.2 mock==3.0.5 h5py==2.10.0 keras_preprocessing==1.1.1 keras_applications==1.0.8 gast==0.2.2 futures protobuf pybind11
sudo pip3 install --pre --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v45 tensorflow
pip3 install torch
pip3 install torchvision
#pip3 install torchaudio
pip3 install serial

-------------------------------------------------------------------------
Install compagnon-software.git
2/32Gb free

-------------------------------------------------------------------------
-------------------------------------------------------------------------
Share wireless internet with ethernet

Ubuntu
sudo sysctl net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -o wlp59s0 -j MASQUERADE

Jetpack 
/etc/NetworkManager/system-connections
dns=8.8.8.8,8.8.4.4

