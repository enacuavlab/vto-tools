sdkmanager --cli downloadonly --logintype devzone --targetos Linux --product Jetson --version 4.5.1 --target=P3668-0000 --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --downloadfolder /home/pprz/Projects/nvidia-sandbox/downloads/nvidia/os_sdkm_downloads

sdkmanager --cli install --logintype devzone --targetos Linux --product Jetson --version 4.5.1 --target P3668-0000 --select 'Jetson OS' --deselect 'Jetson SDK Components' --license accept --offline --downloadfolder /home/pprz/Projects/nvidia-sandbox/downloads/nvidia/os_sdkm_downloads --targetimagefolder /home/pprz/Projects/nvidia-sandbox

wget https://connecttech.com/ftp/Drivers/CTI-L4T-XAVIER-NX-32.5-V001.tgz
cp /home/pprz/Projects/nvidia-sandbox/downloads/connecttech/CTI-L4T-XAVIER-NX-32.5-V001.tgz .
tar -xzf CTI-L4T-XAVIER-NX-32.5-V001.tgz
cd CTI-L4T
sudo ./install.sh

sudo ./flash.sh cti/xavier-nx/quark-imx219 mmcblk0p1




cp /home/pprz/Projects/nvidia-sandbox/downloads/connecttech/CTI-L4T-XAVIER-NX-AVT-32.5-V002.tgz .
tar -xzf CTI-L4T-XAVIER-NX-AVT-32.5-V002.tgz
cd CTI-L4T
sudo ./install.sh

cd ..
sudo ./flash.sh cti/xavier-nx/quark-avt mmcblk0p1
