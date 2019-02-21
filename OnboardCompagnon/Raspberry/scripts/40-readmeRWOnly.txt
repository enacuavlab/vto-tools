------------------------------------------------------------
READ ONLY
------------------------------------------------------------
https://learn.adafruit.com/read-only-raspberry-pi/

(wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/read-only-fs.sh)
or scp from archive
sudo bash read-only-fs.sh

Boot-time R/W jumper: NO
Install GPIO-halt: NO
Enable watchdog: NO

add in /etc/bash.bashrc
alias rw='sudo mount -o remount,rw /'
alias ro='sudo mount -o remount,ro /'

READ ONLY INSTALL (if hotspot)
-----------------
add to /etc/fstab
tmpfs /var/lib/misc tmpfs nodev,nosuid 0 0


