https://redirect.armbian.com/region/EU/bananapi/Buster_current_minimal
Armbian_21.02.3_Bananapi_buster_current_5.10.21_minimal.img.xz
162Mo

Flash SD: balenaEtcher

nmap -sn 192.168.1.xxx/24

ssh root@192.168.1.yyy
1234

adduser xp
sudo usermod -aG sudo xp

sudo apt-get update
sudo apt-get upgrade
sudo reboot

sudo apt install armbian-config
sudo armbian-config
Software / Softy / OMV
50min
sudo reboot 
wait 3min

http://192.168.1.yyy
(http://xp31.hopto.org)
Username: admin
Password: openmediavault

omv-firstaid
Change Control Panel administrator password
reboot

----------------------------------------
Router configuration for Openmediavault access from outside
----------------------------------------
- DHCP => static IP for omv equipment
- NAT/PAT => HTTP 80 TCP, HTTPS 443 TCP, SSH 22 TCP

----------------------------------------
INSTALL Openmediavault 
(50 min)
---------------------------------------
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
(Save & Apply configuration changes - 5 minutes each !)
(do modifications and apply one for all)
  - Certificats
    - SSL / add (25 years, france)

System Setting
  Update Management: check update
  Plugins: check update
  OMV-Extras: check (update, omv-update, upgrade)
 

System Setting
- General settings
  - web admin: 
      auto logout = disable
      Enable SSL/TLS (certifcate file), Force SSL/TLS
  - web admin passwd
  - date: use ntp server
  - Network
    Interface add: 
      Eth0: IPV4 DHCP, IPV6 DISABLED, DNS:80.10.246.132
- Storage 
  - Disk: wipe (quick)
  - File system: Create, Ext4, UnMount / Mount
  (5 minutes for 1To)
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
check:
- dev-disk-by-label-data
- dev-disk-by-label-Disk

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
Nas
ssh as user xp
cp -R /srv/dev-disk-by-label-Disk/ref_restricted/mycamera /srv/dev-disk-by-label-Disk/restricted/
rename 's/\.JPG$/\.jpgaux/' *.JPG
rename 's/\.jpgaux$/\.jpg/' *.jpgaux
mkdir /srv/dev-disk-by-label-Disk/restricted/_mycamera


Ubunntu
sudo mkdir /mnt/nas
sudo mount -t cifs -o user=smb_xp,password=xxx,uid=1000,gid=1000 //192.168.1.109/restricted /mnt/nas
cd /mnt/nas
Makefile
=> generate files resized

Nas
ssh as user xp
cp mycamera/* 
/srv/dev-disk-by-label-Disk/appdata/piwigo/config/www/gallery/galleries/mycamera/
cp _mycamera/* /srv/dev-disk-by-label-Disk/appdata/piwigo/config/www/gallery/_data/i/galleries
/srv/dev-disk-by-label-Disk/appdata/piwigo/config/www/gallery/_data/i/galleries/mycamera/


----------------------------------------
Option 1)
1) FTP repositories mycamera to 
/srv/dev-disk-by-label-Disk/appdata/piwigo/config/www/galleries
chown -R xp mycamera
chgrp -R xp mycamera

2) Dashboard "Quick Local Synchronization"
=> update database

3) Browsing (ex: slide show) generate sized file on live  
/srv/dev-disk-by-label-Disk/appdata/piwigo/config/www/gallery/_data/i/galleries

Digikam export option not recommended: 
- use slow http interface to upload, 
- generate partial resizing files on the server (?)
- rename files and dispatch them according to date
(srv/dev-disk-by-label-Disk/appdata/piwigo/config/www/gallery/upload/$year/$month/$day/
rename filename to $year$month$day$)

----------------------------------------
https://blog.dorian-depriester.fr/linux/raspberry/un-cadre-photo-numerique-connecte-avec-un-raspberry-pi

----------------------------------------
INSTALL Cloud Commander 
----------------------------------------
(installation througth omv and docker/portainer fail:
Deployment error No matching manifest for linux/armv7 in the manifest list entry)

Install with root account

apt install nodejs
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

(router NAT/PAT => cloudcommander 8050 TCP)

----------------------------------------
Disable blue yellow green leds
----------------------------------------
https://raw.githubusercontent.com/n1tehawk/bpi_ledset/master/bpi_ledset.c
gcc -o bpi_ledset bpi_ledset.c
cp bpi_ledset /usr/local/sbin
chmod ugo+xwr /usr/local/sbin/bpi_ledset

vi /etc/rc.local
/usr/local/sbin/bpi_ledset eth0 b y g


----------------------------------------
Install syncthing through portainer
----------------------------------------
Check 
- dev-disk-by-label-data
- dev-disk-by-label-Disk

- 
mkdir -p /srv/dev-disk-by-label-data/appdata/syncthing

Portainer web:
Stacks: add stack mysyncthing
"
version: "2.1"
services:
  syncthing:
    image: linuxserver/syncthing
    container_name: syncthing
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Paris
      - UMASK_SET=022
    volumes:
      - /srv/dev-disk-by-label-data/appdata/syncthing/config:/config
    ports:
      - 8384:8384
      - 22000:22000
      - 21027:21027/udp
    restart: unless-stopped
"
Stacks: Deploy 

mkdir /srv/dev-disk-by-label-data/backup_sync
chmod -R ugo+xwr backup_sync

http://192.168.1.112:8384

Configuration / Interface graphique / set user (admin) and password

Configuration / General 
- Nom convivial local de l'appareil
  Bananapi_A
- Chemin parent par défaut pour les nouveaux partages
  /srv/dev-disk-by-label-Disk/backup_sync

Autres appareils
- Ajouter un appareil: ID + Nom convivial

mkdir /srv/dev-disk-by-label-Disk/backup_sync/video

Partages
- Default Folder: Gérer / Supprimer
- Ajouter un Partage
  General: Nom du partage: video
  Partages: Appareil non membres de ce partage

  - Chemin du partage: 
/srv/dev-disk-by-label-data/backup_sync
 
