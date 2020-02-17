Backup
------

dd bs=512 count=1 if=/dev/sde of=raspogee/mbr.img
sync

umount /media/pprz/boot
sudo partclone.fat --clone --source /dev/sde1 --output - | bzip2 -9 > raspogee/boot.img
umount /media/pprz/rootfs
sudo partclone.extfs --clone --source /dev/sde2 --output - | bzip2 -9 > raspogee/system.img



Restore
-------

dd bs=512 count=1 of=/dev/sde if=raspogee/mbr.img
sync
sudo partprobe

umount /media/pprz/*
sudo bunzip2 -c raspogee/boot.img | sudo partclone.vfat --restore --source - --output /dev/sde1
sudo bunzip2 -c raspogee/system.img | sudo partclone.extfs --restore --source - --output /dev/sde2

Syncing... 
several minutes
