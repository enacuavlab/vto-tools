awk '{print $0; system("sleep .1");}' xyzw.csv | socat - udp-sendto:127.0.0.1:5554

awk '{print $0;system("sleep .05");}' xyzw.csv | awk -F "[ ,]" -W interactive -v start="$(date +%s%3N)" '{cmd="(date +'%s%3N')";cmd | getline d;print d-start,$0,$1,$2,$3;close(cmd)}' | feedgnuplot --stream 0.01 --exit --domain --lines --xlen 10000

socat - udp-recv:5554,bind=0.0.0.0,reuseaddr
