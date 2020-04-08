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
create linux user: xp

----------------------------------------
Router configuration for Openmediavault access from outside
----------------------------------------
- DHCP => static IP for omv equipment
- NAT/PAT => HTTP 80 TCP, HTTPS 443 TCP, SSH 22 TCP

----------------------------------------
INSTALL Openmediavault 
(50 min)
----------------------------------------
apt-get update
apt-get upgrade

armbian-config
Software / Softy / OMV
=> Now installing OpenMediaVault. Be patient, it will take several minutes...
(40 min)

(wget -O - https://github.com/OpenMediaVault-Plugin-Developers/installScript/raw/master/install | sudo bash)
(sudo apt --fix-broken install)

reboot / wait 3 minutes

http://192.168.1.109
(http://xp31.hopto.org)
Username: admin
Password: openmediavault

omv-firstaid
Change Control Panel administrator password
reboot

df -h
=> 1.5 G

System Setting
  Update Management: Update check + install
  Plugins: check
  OMV-Extras: check
Reboot

System Setting
(Save & Apply configuration changes - 5 minutes each !)
- System / Certificates / SSL / add
- General settings
  - web admin: 
      auto logout = disable
      Enable SSL/TLS (certifcate file), Force SSL/TLS
  - web admin passwd
  - date: use ntp server
  - Network
    Interface add: 
      Eth0: IPV4 DHCP, IPV6 DISABLED, DNS:80.10.246.132
  - Update management: Check
- Storage 
!!  Disk: wipe
  File system: Create, Ext4, UnMount / Mount
  (5 minutes)
- Users:
  add SAMBA users smb_xp, smb_vero, smb_kids
- Shared Folders: add
  - restricted: admin:r/w, users:r/w, others:ro
  - public: everyone:r/w
- Services:
  - FTP: disable
  - SMB: 
    - Settings: enable (workgroup "WORKGROUP")
    - Shared: restricted, public:no, ronly:no, browseable:yes

End settup: 
- Users: privileges
   smb_xp: restricted = rw
   smb_vero: restricted = rw
   smb_kids: restricted = ro

  
(router NAT/PAT => samba 139 & 445 TCP)

-------------
Ubuntu Network Share test

nautilus smb://smb_xp@192.168.1.109/restricted => rw
nautilus smb://smb_vero@192.168.1.109/restricted => rw
nautilus smb://smb_kids@192.168.1.109/restricted => ro


----------------------------------------
mkdir -p /srv/dev-disk-by-label-Disk/appdata/dockerfolder

OMV-extras: 
  (Settings: enable Backports)
  Docker:
    Docker Storage: /srv/dev-disk-by-label-Disk/appdata/dockerfolder 
Save
    Docker Install
  Portainer install
OpenWeb
(http://192.168.1.109:9000)

Connect to local

----------------------------------------
INSTALL throught portainer web
 mariadb + piwigo
----------------------------------------

mkdir -p /srv/dev-disk-by-label-Disk/appdata/mariadb-photo
mkdir -p /srv/dev-disk-by-label-Disk/appdata/piwigo

Portainer web:
Stacks: add stack mymariadb
"
version: "2"
services:
  mariadb:
    image: linuxserver/mariadb
    container_name: mariadb
    environment:
      - PUID=1000
      - PGID=1000
      - MYSQL_ROOT_PASSWORD=StrongDatabasePassword
      - TZ=Europe/Paris
      - MYSQL_DATABASE=piwigodb
      - MYSQL_USER=piwigouser
      - MYSQL_PASSWORD=StrongDatabasePassword
    volumes:
      - /srv/dev-disk-by-label-Disk/appdata/mariadb-photo:/config
    ports:
      - 3306:3306
    restart: unless-stopped
"
Stacks: Deploy 


mysql  -u root -p -h localhost -P 3306 --protocol=tcp
StrongDatabasePassword
select host, user, password from mysql.user;
show databases;


Portainer web:
Stacks: add stack mypiwigo
"
version: "2"
services:
  piwigo:
    image: linuxserver/piwigo
    container_name: piwigo
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Paris
    volumes:
      - /srv/dev-disk-by-label-Disk/appdata/piwigo/config:/config
    ports:
      - 8080:80
    restart: unless-stopped
"
Stacks: Deploy

http://192.168.1.109:8080
DB conf:
 Host: 192.168.1.109:3306
 User: piwigouser
 Password: StrongDatabasePassword
 Database name: piwigodb
DB admin:
 User: xpa
 Password: ...


----------------------------------------
INSTALL Cloud Commander 
----------------------------------------
(installation througth omv and docker/portainer fail:
Deployment error No matching manifest for linux/armv7 in the manifest list entry)

sudo apt install nodejs
node -v
=> v10.15.2
curl -sL https://deb.nodesource.com/setup_13.x | bash -
apt-get install -y nodejs
node -v 
=> v13.12.0

npm i cloudcmd -g

cloudcmd --username root --password XXXX --auth --save --no-server

vi /root/.cloudcmd.json
    "port": 8050,

vi /etc/systemd/system/cloudcmd.service
"
[Unit]
Description=Cloud Commander
After=network.target


[Service]
WorkingDirectory=/usr/lib/node_modules/cloudcmd/bin/
ExecStart=/usr/bin/node cloudcmd.js
Restart=on-failure


[Install]
WantedBy=multi-user.target
"

systemctl start cloudcmd
systemctl status cloudcmd
systemctl enable cloudcmd

(router NAT/PAT => cloudcommander 8000 TCP)


