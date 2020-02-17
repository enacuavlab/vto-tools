
------------------------------------------------------------
READ ONLY
------------------------------------------------------------
Option 1

https://www.raspberrypi.org/forums/viewtopic.php?f=63&t=161416

https://gist.github.com/dzindra/a8e2083a7f037ca244cf70d100c96656

http://wiki.psuter.ch/doku.php?id=solve_raspbian_sd_card_corruption_issues_with_read-only_mounted_root_partition

http://wiki.psuter.ch/doku.php?id=install_raspbian_on_f2fs_root



------------------------------------------------------------
Option 2

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


