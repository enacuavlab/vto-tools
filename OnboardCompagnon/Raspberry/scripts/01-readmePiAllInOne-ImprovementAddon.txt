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
sudo vi /etc/dhcpcd.conf
"
#denyinterfaces wlan0
denyinterfaces wlan1
or
denyinterfaces wlan0
denyinterfaces wlan1
...
# It is possible to fall back to a static IP if DHCP fails:
# define static profile
profile static_eth0
static ip_address=192.168.3.2/24
static routers=192.168.3.1
static domain_name_servers=192.168.3.1

# fallback to static profile on eth0
interface eth0
fallback static_eth0
"
---------------------------------
sudo vi svpcom.sh
"
WFB_DEV="wlan1"
ifconfig $WFB_DEV down
sleep 1
iw dev $WFB_DEV set monitor otherbss
iw reg set DE
ifconfig $WFB_DEV up
iw dev $WFB_DEV set channel 36
#iw $WFB_DEV info
"

---------------------------------
No extra udev rules
---------------------------------
Unchanged
sudo vi /etc/network/interfaces
"
source-directory /etc/network/interfaces.d
"
