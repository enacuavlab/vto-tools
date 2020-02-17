RASPBERRY PI uart
Configure 

------------------------------------------------------------

Initial context
---------------
/dev/ttyAMA0 -> Bluetooth
/dev/ttyS0 -> GPIO serial port (?)


Disable the console
-------------------
sudo systemctl stop serial-getty@ttyAMA0.service
sudo systemctl disable serial-getty@ttyAMA0.service

sudo vi /boot/cmdline.txt
dwc_otg.lpm_enable=0 console=serial0,115200 console=tty1 root=PARTUUID=dc6114e5-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait fastboot noswap ro
remove
console=serial0,115200


Enable UART
-----------
sudo vi /boot/config.txt
add
enable_uart=1


Swap serial
-----------
sudo vi /boot/config.txt
add
dtoverlay=pi3-disable-bt

sudo systemctl stop hciuart
sudo systemctl disable hciuart


Test
-----
Loopback test (pin 14 & 15)
sudo minicom -D /dev/ttyAMA0
Each character shoud be echo
