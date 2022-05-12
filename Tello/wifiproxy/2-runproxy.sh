#!/bin/bash

docker run -d --rm --privileged \
  -e DRONE_AP=$DRONE_AP \
  -e WIFI_DEV=$WIFI_DEV \
  -e VID_PORT=$VID_PORT \
  --name $DRONE_AP \
  wifiproxy
