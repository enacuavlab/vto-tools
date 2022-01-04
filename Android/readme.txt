Google play android application:
HyperImu
Sebastiano Campisi v3.1.3.0

socat - udp-recv:5555
#socat - udp-recvfrom:5555,fork
#socat - TCP4-LISTEN:5555




stdbuf -oL -eL socat - udp-recv:5555 | tee 5ms_sample.log

sudo apt-get install feedgnuplot

stdbuf -oL -eL socat - udp-recv:5555 | awk -F "[ ,]" -W interactive -v start="$(date +%s%3N)" '{cmd="(date +'%s%3N')";cmd | getline d;print d-start,$1,$2,$3;close(cmd)}' | feedgnuplot --stream 0.01 --exit --domain --lines --xlen 10000

stdbuf -oL -eL socat - udp-recv:5555 | awk -F "[ ,]" -W interactive -v start="$(date +%s%3N)" '{cmd="(date +'%s%3N')";cmd | getline d;print d-start,$1,$2,$3;close(cmd)}' | tee 5ms_accelcalibpurpose.log | feedgnuplot --stream 0.01 --exit --domain --lines --xlen 10000


feedgnuplot --domain --lines 5ms_accelcalibpurpose.log

./filter 20 10 ./5ms_accelcalibpurpose.log | feedgnuplot --exit --domain --lines
...
Tunne to remove highest pics
...
./filter 25 10 ./5ms_accelcalibpurpose.log | feedgnuplot --exit --domain --lines

./filter 25 10 ./5ms_accelcalibpurpose.log > 5ms_accelcalibpurpose.filtered

./scale 9.81 10 ./5ms_accelcalibpurpose.filtered | feedgnuplot --exit --domain --lines

./scale 9.81 10 ./5ms_accelcalibpurpose.filtered > 5ms_accelcalibpurpose.scaled

