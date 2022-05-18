sudo mkdir -p /var/run/netns

-----------------------------------------
# Check docker image
docker image ls
=> wifiproxy
=> ubuntu

# Remove docker image
docker image rm wifiproxy

# Build docker image
cd dockerproxy
docker build -t wifiproxy .

---------------------------------------
# Run docker image for each drone building containers
(needed sudo password)
cd ..
./TELLO-ED4310.sh

# Check docker containers
docker ps
=> wifiproxy .. TELLO-ED4310

# Bash in containers
docker exec -it TELLO-ED4310 /bin/bash
=> root@..:/# ps, ifconfig, ping ...

# Switch on the drone

# Check connection from python app
./runtello.py ?
=> TELLO-ED4310 created
=> TELLO-ED4310 connected

# Run commands from python app
./runtello.py TELLO-ED4310

# Run video stream on port define in drone configuration launcher file (TELLO-ED4310.sh)
gst-launch-1.0 -v udpsrc port=11112 caps="video/x-h264, stream-format=(string)byte-stream" ! decodebin ! videoconvert ! autovideosink sync=false

---------------------------------------
# Kill docker container for each drone
docker kill $(docker ps -q)
sudo rm /var/run/netns/*
(docker system prune)
