Do not install on GIT folders !


sudo rm /opt/unityhub/

https://docs.unity3d.com/hub/manual/InstallHub.html?_ga=2.201535192.892109804.1643533377-1670894999.1642596560#
Unity Hub 3.0

"
sudo sh -c 'echo "deb https://hub.unity3d.com/linux/repos/deb stable main" > /etc/apt/sources.list.d/unityhub.list'
wget -qO - https://hub.unity3d.com/linux/keys/public | sudo apt-key add -
sudo apt update
sudo apt-get install unityhub
"

export HTTPS_PROXY=http://squid:3128
export HTTP_PROXY=http://squid:3128
/opt/unityhub/unityhub-bin

(login ?)

Unity Editor :
LTS Release 2020.3.27f1
Released: 1 Feb. 2022

~/Project/sim_engines/Unity
