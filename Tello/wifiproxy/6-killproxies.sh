#!/bin/bash

docker ps -aq
docker kill 
docker network prune
