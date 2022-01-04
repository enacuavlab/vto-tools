Google play android application:
HyperImu
Sebastiano Campisi v3.1.3.0

Set application to broadcast
- 3 uncalibrated accel
- 3 uncalibrated mag

Set Ip destination
Start acqusition and broadcast


For Accel and Mag
-----------------
stdbuf -oL -eL socat - udp-recv:5555 | tee 5ms_sample.log
#socat - udp-recvfrom:5555,fork

sudo apt-get install feedgnuplot

* Accel calibration: handle positions to maximize accel values with gravity (Z)
* Mag calibration: rotate around center of gravity, to maximize mag values with norh

stdbuf -oL -eL socat - udp-recv:5555 | awk -F "[ ,]" -W interactive -v start="$(date +%s%3N)" '{cmd="(date +'%s%3N')";cmd | getline d;print d-start,$1,$2,$3;close(cmd)}' | feedgnuplot --stream 0.01 --exit --domain --lines --xlen 10000

stdbuf -oL -eL socat - udp-recv:5555 | awk -F "[ ,]" -W interactive -v start="$(date +%s%3N)" '{cmd="(date +'%s%3N')";cmd | getline d;print d-start,$1,$2,$3;close(cmd)}' | tee 5ms_accelcalibpurpose.log | feedgnuplot --stream 0.01 --exit --domain --lines --xlen 10000

(or 5ms_magcalibpurpose.log)

feedgnuplot --domain --lines 5ms_accelcalibpurpose.log

./filter 20 10 ./5ms_accelcalibpurpose.log | feedgnuplot --exit --domain --lines
...
Tunne to remove highest pics
...
./filter 25 10 ./5ms_accelcalibpurpose.log | feedgnuplot --exit --domain --lines

./filter 25 10 ./5ms_accelcalibpurpose.log > 5ms_accelcalibpurpose.filtered

(./filter 10 11 ./5ms_magcalibpurpose.log > 5ms_magcalibpurpose.filtered)

./scale 9.81 10 ./5ms_accelcalibpurpose.filtered | feedgnuplot --exit --domain --lines

./scale 9.81 10 ./5ms_accelcalibpurpose.filtered > 5ms_accelcalibpurpose.scaled

(./scale 1 11 ./5ms_magcalibpurpose.filtered > 5ms_magcalibpurpose.scaled)


For Mag only
------------
cat 5ms_magcalibpurpose.scaled |  awk '{print $2" "$3" "$4}' | feedgnuplot --domain -3d
