Some usefull applications:

Install 
https://github.com/enacuavlab/compagnon-software

https://github.com/rbonghi/jetson_stats

Jtop
- Jetpack: 4.6 [L4T 32.6.1]
- CUDA: 10.2.300
- OPENCV: 4.1.1 compiled CUDA: NO

-----------------------------------------------------------
Remove OPENCV compiled without CUDA:

sudo apt-get purge '*opencv*'

Jtop
- OPENCV: Not installed

Compile opencv on target with following script

https://qengineering.eu/install-opencv-4.5-on-jetson-nano.html
Running on xavier nx

Opencv 4.6.0
wget https://github.com/Qengineering/Install-OpenCV-Jetson-Nano/raw/main/OpenCV-4-6-0.sh
sudo chmod 755 ./OpenCV-4-6-0.sh
./OpenCV-4-6-0.sh 
... 4 hours later

cd opencv/build
make
sudo make install

Optional:
rm OpenCV-4-6-0.sh 
sudo rm -rf ~/opencv
sudo rm -rf ~/opencv_contrib 

Jtop
- OpenCV: 4.6.0 COmpiles CUDA: YES


-----------------------------------------------------------
Backup the SD card

Plug in host
demsg -w
=> sdx


Copy the entire SD card 
sudo dd bs=4M if=/dev/sdx of=./xaviernx.img status=progress
=> 30 Gb

sudo losetup --show --find --partscan ./xaviernx.img
=> /dev/loop18

sudo gparted /dev/loop18
- shrink the partition to 17 Gb
(
old end: 62521310
e2fsck -f -y -v -C 0 '/dev/loop18p1'
resize2fs -p '/dev/loop18p1' 18120704K)
new end: 36243455
)

fdisk -lu /dev/loop18
=>
fdisk -lu /dev/loop18
Disk /dev/loop18: 29,83 GiB, 32010928128 bytes, 62521344 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: gpt
Disk identifier: 3B2F1072-A4E6-42C3-ADBD-4534BAA17CCD

Device        Start      End  Sectors  Size Type
/dev/loop18p1  2048 36263935 36261888 17,3G Linux filesystem


sudo losetup --detach /dev/loop18

sudo chmod ugo+xwr ./xaviernx.img
truncate --size=$[(36263935+33+1)*512] ./xaviernx.img
(End + 33, for GPT)

ls -lah ./xaviernx.img
=> 18G

gdisk ./xaviernx.img
"
x
e
w
"
=>
Final checks complete. About to write GPT data. THIS WILL OVERWRITE EXISTING
PARTITIONS!!
"

sudo losetup --show --find --partscan ./xaviernx.img
sudo gparted /dev/loop18
sudo losetup --detach /dev/loop18

bzip2 ./xaviernx.img
(10 minutes)
=>
./xaviernx.img.bz2
7 Gb

-----------------------------------------------------------
Restore the SD card

bunzip2 xaviernx.img.bz2

plug SD
dmesg 
=> sdx

sudo dd bs=4M if=./xaviernx.img of=/dev/sdx status=progress

sync

Replug SD
dmesg
=>
[18825.324118] GPT:Primary header thinks Alt. header is not at the end of the disk.
[18825.324125] GPT:36263968 != 62521343
[18825.324128] GPT:Alternate GPT header not at the end of the disk.
[18825.324130] GPT:36263968 != 62521343
[18825.324132] GPT: Use GNU Parted to correct GPT errors.

sudo gparted /dev/sdx
=>
Not all of the space available to /dev/sdb appears to be used, you can fix the GPT to use all of the space (an extra 26257375 blocks) or continue with the current setting? 

fix

expand 
(resize2fs -p '/dev/sdb1')

