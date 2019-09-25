RASPBIAN
Download, install and run  

------------------------------------------------------------
wget https://downloads.raspberrypi.org/raspbian_lite_latest

connect sd card (/dev/sdxx or /dev/mmcxxx)

check device
lsblk 

copy to suitable device (/dev/sda or /dev/mmcblk0)
unzip -p raspbian_lite_latest | sudo dd of=/dev/sdxx bs=4M status=progress conv=fsync

0+22922 enregistrements lus
0+22922 enregistrements écrits
1866465280 bytes (1,9 GB, 1,7 GiB) copied, 170,993 s, 10,9 MB/s

=> 1 min
sync

Plug/unplug SD


Create file
boot/ssh

Create file with following content
boot/wpa_supplicant.conf
"
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=FR

network={
  ssid="Androidxp"
  psk="pprzpprz"
}
network={
  ssid="pprz_router"
  key_mgmt=NONE
}
network={
  ssid="Livebox-7EA4"
  psk="6vNVEJNeLCYLubnbuk"
}
"

boot
log

nmap -sn 192.168.1.0/24

ssh pi@192.168.1.x
password "raspberry"

sudo raspi-config
1) change user password
7) advanced options
  A1) expand filesystem

  
sudo vi /etc/dphys-swapfile 
CONF_SWAPSIZE=1024
