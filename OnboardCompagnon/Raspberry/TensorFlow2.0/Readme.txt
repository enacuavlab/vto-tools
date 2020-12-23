https://qengineering.eu/install-tensorflow-2.2.0-on-raspberry-pi-4.html
Works on RPI3


sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python-pip
sudo pip uninstall tensorflow
sudo pip3 uninstall tensorflow
sudo apt-get install gfortran
sudo apt-get install libhdf5-dev libc-ares-dev libeigen3-dev
sudo apt-get install libatlas-base-dev libopenblas-dev libblas-dev
sudo apt-get install liblapack-dev cython
sudo -H pip3 install pybind11
sudo -H pip3 install h5py==2.10.0
sudo -H pip3 install --upgrade setuptools
pip install gdown
sudo cp ~/.local/bin/gdown /usr/local/bin/gdown
gdown https://drive.google.com/uc?id=11mujzVaFqa7R1_lB7q0kVPW22Ol51MPg
sudo -H pip3 install tensorflow-2.2.0-cp37-cp37m-linux_armv7l.whl

python3
import tensorflow as tf
tf.__version__
=>'2.2.0'


TensorFlow 2.2.0 C++ API
------------------------
sudo apt-get update
sudo apt-get upgrade
sudo rm -r /usr/local/lib/libtensorflow*
sudo rm -r /usr/local/include/tensorflow
sudo apt-get install wget curl libhdf5-dev libc-ares-dev libeigen3-dev
sudo apt-get install libatomic1 libatlas-base-dev zip unzip
pip install gdown
sudo cp ~/.local/bin/gdown /usr/local/bin/gdown
gdown https://drive.google.com/uc?id=143abOB3eyMvCq6nj6M7co4-v9VLR5SW0
sudo tar -C /usr/local -xzf libtensorflow_2_2_0.tar.gz

