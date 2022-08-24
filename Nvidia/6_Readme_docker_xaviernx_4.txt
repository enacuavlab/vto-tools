sudo pip3 install jetson-stats
sudo jtop

-------------------------------------------------------------------------------

https://forums.developer.nvidia.com/t/pytorch-for-jetson-version-1-11-now-available/72048

sudo apt-get install python3-pip libopenblas-base libopenmpi-dev libomp-dev
pip3 install Cython
pip3 install numpy torch-1.10.0-cp36-cp36m-linux_aarch64.whl

sudo apt-get install libjpeg-dev zlib1g-dev libpython3-dev libavcodec-dev libavformat-dev libswscale-dev
git clone --branch v0.11.1 https://github.com/pytorch/vision torchvision   # see below for version of torchvision to download
cd torchvision
export BUILD_VERSION=0.11.1  # where 0.x.0 is the torchvision version  
python3 setup.py install --user

cd ../  # attempting to load torchvision from build dir will result in import error
pip install 'pillow<8' 


python3
=> Python 3.6.9 (default, Mar 15 2022, 13:55:28) 

import torch
print(torch.__version__)
=> 1.10.0
print('CUDA available: ' + str(torch.cuda.is_available()))
=> CUDA available: True
print('cuDNN version: ' + str(torch.backends.cudnn.version()))
=> cuDNN version: 8201
a = torch.cuda.FloatTensor(2).zero_()
print('Tensor a = ' + str(a))
=> Tensor a = tensor([0., 0.], device='cuda:0')
b = torch.randn(2).cuda()
print('Tensor b = ' + str(b))
=> Tensor b = tensor([-1.7729, -0.5889], device='cuda:0')
c = a + b
print('Tensor c = ' + str(c))
=> Tensor c = tensor([-1.7729, -0.5889], device='cuda:0')

import torchvision
print(torchvision.__version__)
=> v0.11.0


-------------------------------------------------------------------------------

pip3 install tqdm seaborn
( pandas, matplotlib, scipy, kiwisolver, pillow ... : 1 hour)


pip3 install scikit-build

git clone https://github.com/ultralytics/yolov5  # clone
cd yolov5
pip install -r requirements.txt  # install
