------------------------------------------------------------
HOTSPOT ROUTER
------------------------------------------------------------
http://www.raspberryconnect.com/network/item/331-raspberry-pi-auto-wifi-hotspot-switch-no-internet-routing

1)
sudo apt-get install hostapd
sudo apt-get install dnsmasq
sudo systemctl disable hostapd
sudo systemctl disable dnsmasq

sudo vi /etc/hostapd/hostapd.conf
#2.4GHz setup wifi 80211 b,g,n
interface=wlan0
driver=nl80211
ssid=RPiHotspot
hw_mode=g
channel=8
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=1234567890
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP TKIP
rsn_pairwise=CCMP
country_code=FR
ieee80211n=1
ieee80211d=1

sudo vi /etc/default/hostapd
DAEMON_CONF="/etc/hostapd/hostapd.conf"

sudo vi /etc/dnsmasq.conf
no-resolv
interface=wlan0
bind-interfaces
dhcp-range=10.0.0.3,10.0.0.20,12h

sudo vi /etc/network/interfaces
source-directory /etc/network/interfaces.d

sudo vi /etc/dhcpcd.conf
nohook wpa_supplicant

sudo vi /etc/systemd/system/autohotspot.service
[Unit]
Description=Automatically generates an internet Hotspot when a valid ssid is not in range
After=multi-user.target
[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/autohotspot
[Install]
WantedBy=multi-user.target

sudo systemctl enable autohotspot.service

2)
scp autohotspot pi@:/usr/bin/
sudo chmod +x /usr/bin/autohotspot

3)
sudo vi /etc/wpa_supplicant/wpa_supplicant.conf

READ ONLY INSTALL
-----------------
add to /etc/fstab
tmpfs /var/lib/misc tmpfs nodev,nosuid 0 0


REMOVE HOT SPOT ROUTER
----------------------
sudo systemctl disable autohotspot
sudo vi /etc/dhcpcd.conf
#nohook wpa_supplicant
