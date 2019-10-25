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

