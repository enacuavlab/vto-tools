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
rm OpenCV-4-6-0.sh 
sudo rm -rf ~/opencv
sudo rm -rf ~/opencv_contrib 
