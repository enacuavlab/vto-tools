----------------------------------------
FLASH 
----------------------------------------
https://www.armbian.com/bananapi/
Armbian_20.02.5_Bananapi_buster_current_5.4.26.7z

flash SD
and configure network
plug the SD and boot

Then use ssh
shutdown -h now
(shutdown -r now)

!!!!
DO NOT USE COMMAND
"HALT"
USE 
"SHUTDOWN -H NOW"
!!!

----------------------------------------
CONFIGURE SD
----------------------------------------
sudo vi /etc/wpa_supplicant/wpa_supplicant.conf
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
network={
  ssid="Livebox-1aa4"
  psk="E89831065C74F706AFC0E95F63"
}

---------
or for two wifi adapers
sudo vi /etc/network/interfaces

auto eth0
iface eth0 inet dhcp

#auto eth0
#iface eth0 inet static
#address 192.168.3.2
#netmask 255.255.255.0

#auto wlan0
#iface wlan0 inet dhcp
#    wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf


---------
sudo vi /etc/udev/rules.d/10-network-device.rules 
SUBSYSTEM=="net", ACTION=="add", ATTR{address}=="00:0f:13:38:21:90", NAME="wlan0"

sudo udevadm control --reload-rules && udevadm trigger

----------------------------------------
CONFIGURE throught ssh
----------------------------------------
Login: root
passwd: 1234
sudo adduser pprz
usermod -aG sudo pprz

----------------------------------------
Router configuration for Openmediavault access from outside
----------------------------------------
- DHCP => static IP for omv equipment
- NAT/PAT => HTTP 80 TCP, HTTPS 443 TCP, SSH 22 TCP

----------------------------------------
INSTALL Openmediavault 
----------------------------------------
armbian-config
Software / Softy / OMV

reboot

http://192.168.3.2
(http://xp31.hopto.org)
Username: admin
Password: openmediavault

omv-firstaid
Change Control Panel administrator password
reboot

System Setting
- Certificates / SSL add
- General settings
  Enable SSL/TLS + Certifacicate file
  Force SSL/TLS
Save & Apply configuration changes

https://192.168.3.2
https://xp31.hopto.org/


