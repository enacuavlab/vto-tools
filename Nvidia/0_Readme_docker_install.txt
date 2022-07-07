This will install the wright docker, and settup working directory to unlimited image and container size
--------------------------------------------------------------------------------------------------------

sudo snap remove docker
sudo snap list
=> 
sudo snap remove docker

----------------------------------------------------
dpkg -l | grep -i docker
=>
sudo apt-get purge -y docker docker-ce docker-ce-cli docker-ce-rootless-extras docker-scan-plugin wmdocker 
sudo apt-get autoremove -y docker docker-ce docker-ce-cli docker-ce-rootless-extras docker-scan-plugin wmdocker 

sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd

----------------------------------------------------
https://docs.docker.com/engine/install/ubuntu/

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

sudo vi /etc/systemd/system/docker.service.d/http-proxy.conf 
comment "#" each line

sudo systemctl stop docker.service
systemctl daemon-reload
sudo systemctl start docker.service 

sudo docker run hello-world
docker info

----------------------------------------------------
https://stackoverflow.com/questions/62976159/persisting-docker-data-root-across-reboots

mkdir /home/pprz/Docker

sudo vi /lib/systemd/system/docker.service
ExecStart=/usr/bin/dockerd --data-root /home/pprz/Docker -H fd:// --containerd=/run/containerd/containerd.sock

systemctl daemon-reload
sudo systemctl stop docker.service
sudo systemctl stop docker.socket

docker info
=> 
 Docker Root Dir: /home/pprz/Docker

sudo usermod -aG docker 

