Google play android application:
HyperImu
Sebastiano Campisi v3.1.3.0

socat - udp-recv:5555
#socat - udp-recvfrom:5555,fork
#socat - TCP4-LISTEN:5555




stdbuf -oL -eL socat - udp-recv:5555 | tee 5ms_sample.log

sudo apt-get install feedgnuplot

stdbuf -oL -eL socat - udp-recv:5555 | awk -F "[ ,]" -W interactive '{print systime()" "$1}'  | feedgnuplot --stream --exit --domain --timefmt %s --lines

stdbuf -oL -eL socat - udp-recv:5555 | awk -F "[ ,]" -W interactive '{cmd="(date +'%s%3N')";cmd | getline d;print d,$1;close(cmd)}'| feedgnuplot --stream --exit --domain --timefmt %s --lines

stdbuf -oL -eL socat - udp-recv:5555 | awk -F "[ ,]" -W interactive '{cmd="(date +'%s%3N')";cmd | getline d;print d,$1;close(cmd)}'| feedgnuplot --stream --exit --domain --lines
