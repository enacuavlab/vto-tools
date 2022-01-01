Google play android application:
HyperImu
Sebastiano Campisi v3.1.3.0

socat - udp-recv:5555
#socat - udp-recvfrom:5555,fork
#socat - TCP4-LISTEN:5555




stdbuf -oL -eL socat - udp-recv:5555 | tee 5ms_sample.log

sudo apt-get install feedgnuplot

stdbuf -oL -eL socat - udp-recv:5555 | awk -F "[ ,]" -W interactive -v start="$(date +%s%3N)" '{cmd="(date +'%s%3N')";cmd | getline d;print d-start,$1;close(cmd)}' | feedgnuplot --stream 0.01 --exit --domain --lines --xlen 10000

stdbuf -oL -eL socat - udp-recv:5555 | awk -F "[ ,]" -W interactive -v start="$(date +%s%3N)" '{cmd="(date +'%s%3N')";cmd | getline d;print d-start,$1;close(cmd)}' | tee 5ms_accelcalibpurpose.log | feedgnuplot --stream 0.01 --exit --domain --lines --xlen 10000

feedgnuplot --domain --lines 5ms_accelcalibpurpose.log
