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
neutral=0.228768 Sensitivity=9.825374
neutral=0.086537 Sensitivity=9.916677
neutral=0.040723 Sensitivity=9.836582

(./scale 1 11 ./5ms_magcalibpurpose.filtered > 5ms_magcalibpurpose.scaled)
neutral=78.178131 Sensitivity=0.285274
neutral=-0.600000 Sensitivity=0.290429
neutral=43.228127 Sensitivity=0.275624


For Mag only
------------
awk '{print $2" "$3" "$4}' 5ms_magcalibpurpose.scaled | feedgnuplot --domain --3d

LC_NUMERIC="C" awk '{print $2+0.5" "$3" "$4}' 5ms_magcalibpurpose.scaled | feedgnuplot --domain --3d --title "\$2+0.5 \$3 \$4"

To be continued ...
LC_NUMERIC="C" awk '{sinval=$4;radval=atan2(sinval,sqrt(1-sinval*sinval));print sinval" "cos(radval)}' 5ms_magcalibpurpose.scaled


Check Accel and Mag calibrations
---------------------------------
Set android application to broadcast
3 calibrate accel + 3 calibrated mag + 3 uncalibrated mag + 3 uncalibrated accel


stdbuf -oL -eL socat - udp-recv:5555 | LC_NUMERIC="C" awk -F "[ ,]" -W interactive -v start="$(date +%s%3N)" -v neutral="0.33" '{cmd="(date +'%s%3N')";cmd | getline d;print d-start,$1,($4-neutral);close(cmd)}' | feedgnuplot --stream 0.01 --exit --domain --lines --xlen 10000

neutral=0.228768 should be 0.33
neutral=0.086537 should be 0.08
neutral=0.040723 could be

neutral=78.178131 should be 74.5
neutral=-0.600000 could be 
neutral=43.228127 could be


Usage
-----
Set android application to broadcast
3 uncalibrate mag + 3 uncalibrated accel

stdbuf -oL -eL socat - udp-recvfrom:5555,fork | LC_NUMERIC="C" awk -F "[ ,]" -W interactive -v start="$(date +%s%3N)" 'BEGIN{neutral[1]=48.0;neutral[2]=7.0;neutral[3]=18.0;neutral[4]=0.5;neutral[5]=0.1;neutral[6]=0.04;}{cmd="(date +'%s%3N')";cmd | getline d;print d-start,($1-neutral[1]),($2-neutral[2]),($3-neutral[3]),($4-neutral[4]),($5-neutral[5]),($6-neutral[6]);close(cmd)}' | feedgnuplot --stream 0.01 --exit --domain --lines --xlen 1000



stdbuf -oL -eL socat - udp-recvfrom:5555,fork | LC_NUMERIC="C" awk -F "[ ,]" -W interactive -v start="$(date +%s%3N)" 'BEGIN{neutral[1]=48.0;neutral[2]=7.0;neutral[3]=18.0;neutral[4]=0.5;neutral[5]=0.1;neutral[6]=0.04;}{cmd="(date +'%s%3N')";cmd | getline d;print d-start,($1-neutral[1]),($2-neutral[2]),($3-neutral[3]),($4-neutral[4]),($5-neutral[5]),($6-neutral[6]);close(cmd)}' | tee >(socat - udp-sendto:127.0.0.1:5554) | feedgnuplot --stream 0.01 --exit --domain --lines --xlen 10000

socat - udp4-listen:5554,reuseaddr,fork

 
