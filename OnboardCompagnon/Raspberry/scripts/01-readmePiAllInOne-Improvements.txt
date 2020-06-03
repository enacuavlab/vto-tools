---------------------------------
sudo vi /etc/network/interfaces
"
source-directory /etc/network/interfaces.d

auto eth0
iface eth0 inet static
address 192.168.3.2
netmask 255.255.255.0

auto wlan0
iface wlan0 inet dhcp
    wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf

allow-hotplug wlan1
iface wlan1 inet manual
  pre-up iw phy phy1 interface add mon1 type monitor
  pre-up iw dev wlan1 del
  pre-up ifconfig mon1 up
  pre-up iw dev mon1 set channel 36
"

---------------------------------
sudo vi wpa_supplicant.conf 
"
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=FR

network={
  ssid="Androidxp"
  psk="pprzpprz"
}
network={
  ssid="pprz_routerrrrrrrrrrrrr"
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
"

---------------------------------
No extra udev rules

---------------------------------
sudo vi /etc/dhcpcd.conf
"
denyinterfaces wlan1
"

---------------------------------
svpcom.sh
"
WFB_DEV="mon1"
"
