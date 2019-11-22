-------------------------------------------------------------------------------
Install Paparazzi on PI3 debian strech (Debian_9.0)
-------------------------------------------------------------------------------
wget -q "http://download.opensuse.org/repositories/home:/flixr:/paparazzi-uav/Debian_9.0/Release.key" -O- | sudo apt-key add -

echo "deb http://download.opensuse.org/repositories/home:/flixr:/paparazzi-uav/Debian_9.0/ ./" | tee -a /etc/apt/sources.list

sudo apt-get update 
sudo apt-get install paparazzi-dev

sudo apt-get update
sudo apt-get install gcc-arm-none-eabi gdb-arm-none-eabi

git clone https://github.com/enacuavlab/paparazzi.git
cd paparazzi
git checkout demo_vto

sudo cp conf/system/udev/rules/*.rules /etc/udev/rules.d/ && sudo udevadm control --reload-rules

make
./paparazzi

export PAPARAZZI_HOME=/home/pi/paparazzi
export PAPARAZZI_SRC=/home/pi/paparazzi

copy 
var/aircrafts/Karpet/*

rm /home/ppi/paparazzi/conf/conf.xml
ln -s /home/pi/paparazzi/conf/airframes/ENAC/conf_enac_vto.xml /home/ppi/paparazzi/conf/conf.xml




---------------------------------------------------------
#sudo apt-get install python-pip
#sudo pip install numpy
#sudo pip install ivy

#git clone https://gitlab.com/ivybus/ivy-python.git
#cd ivy-python/
#sudo ./setup.py install

---------------------------------------------------------

sudo apt-get install python3-pip
sudo pip3 install numpy
sudo pip3 install ivy-python
sudo pip3 install lxml

---------------------------------------------------------
/home/pi/paparazzi/sw/ground_segment/tmtc/server
/home/pi/paparazzi/sw/ground_segment/tmtc/link  -udp 
/home/pi/paparazzi/sw/ground_segment/python/natnet3.x/natnet2ivy.py  -ac 115 115  -s 192.168.1.230 -f 5

sudo -E /home/pi/paparazzi/sw/ground_segment/joystick/input2ivy  -ac Karpet frsky_lite.xml

---------------------------------------------------------

devadm info -q all -n /dev/input/js0
P: /devices/platform/soc/3f980000.usb/usb1/1-1/1-1.2/1-1.2:1.0/0003:0483:5710.0001/input/input0/js0
N: input/js0
S: input/by-id/usb-FrSky_FrSky_Taranis_Joystick_00000000001B-joystick
S: input/by-path/platform-3f980000.usb-usb-0:1.2:1.0-joystick
E: DEVLINKS=/dev/input/by-path/platform-3f980000.usb-usb-0:1.2:1.0-joystick /dev/input/by-id/usb-FrSky_FrSky_Taranis_Joystick_00000000001B-joystick
E: DEVNAME=/dev/input/js0
E: DEVPATH=/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.2/1-1.2:1.0/0003:0483:5710.0001/input/input0/js0
E: ID_BUS=usb
E: ID_FOR_SEAT=input-platform-3f980000_usb-usb-0_1_2_1_0
E: ID_INPUT=1
E: ID_INPUT_JOYSTICK=1
E: ID_MODEL=FrSky_Taranis_Joystick
E: ID_MODEL_ENC=FrSky\x20Taranis\x20Joystick
E: ID_MODEL_ID=5710
E: ID_PATH=platform-3f980000.usb-usb-0:1.2:1.0
E: ID_PATH_TAG=platform-3f980000_usb-usb-0_1_2_1_0
E: ID_REVISION=0200
E: ID_SERIAL=FrSky_FrSky_Taranis_Joystick_00000000001B
E: ID_SERIAL_SHORT=00000000001B
E: ID_TYPE=hid
E: ID_USB_DRIVER=usbhid
E: ID_USB_INTERFACES=:030000:
E: ID_USB_INTERFACE_NUM=00
E: ID_VENDOR=FrSky
E: ID_VENDOR_ENC=FrSky
E: ID_VENDOR_ID=0483
E: MAJOR=13
E: MINOR=0
E: SUBSYSTEM=input
E: TAGS=:uaccess:seat:
E: USEC_INITIALIZED=51622900


SUBSYSTEM=="input", ATTRS{name}=="*Controller Touchpad", RUN+="/bin/rm %E{DEVNAME}", ENV{ID_INPUT_JOYSTICK}=""

sudo -E /home/pi/paparazzi/sw/ground_segment/joystick/input2ivy  -ac Karpet frsky_lite.xml -b 192.168.1.255:2010
