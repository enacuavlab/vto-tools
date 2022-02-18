#!/bin/bash

# test1 : computation on ground

sudo /home/pprz/Projects/compagnon-software/wifibroadcast/wfb_tx -K /home/pprz/Projects/compagnon-software/wifibroadcast/gs.key -p 3 -u 4245 wlxfc34972ed583
stdbuf -oL -eL ./natnet | tee >(socat - udp-sendto:127.0.0.1:4245)

sudo /home/pi/Projects/compagnon-software/wifibroadcast/wfb_rx -K /home/pi/Projects/compagnon-software/wifibroadcast/drone.key -p 3 -u 4245 -c 127.0.0.1 wlan1
stdbuf -oL -eL  socat - udp-recv:4245,reuseaddr


# test2 : computation on board

sudo /home/pprz/Projects/compagnon-software/wifibroadcast/wfb_tx -K /home/pprz/Projects/compagnon-software/wifibroadcast/gs.key -p 3 -u 4245 wlxfc34972ed583
socat UDP-RECV:1511,bind=0.0.0.0,reuseaddr,ip-add-membership=239.255.42.99:0.0.0.0 udp-sendto:127.0.0.1:4245

sudo /home/pi/Projects/compagnon-software/wifibroadcast/wfb_rx -K /home/pi/Projects/compagnon-software/wifibroadcast/drone.key -p 3 -u 1511 -c 127.0.0.1 wlan1
./natnet -u
?
./natnet
?
