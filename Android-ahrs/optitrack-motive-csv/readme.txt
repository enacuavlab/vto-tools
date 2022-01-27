awk '{print $0; system("sleep .1");}' xyzw.csv | socat - udp-sendto:127.0.0.1:5554

socat - udp-recv:5554,bind=0.0.0.0,reuseaddr

awk '{print $0;system("sleep .05");}' xyzw.csv | awk -F "[ ,]" -W interactive -v start="$(date +%s%3N)" '{cmd="(date +'%s%3N')";cmd | getline d;print d-start,$1,$2,$3,$4;close(cmd)}' | feedgnuplot --stream 0.01 --exit --domain --lines --xlen 10000

awk '{print $0;system("sleep .05");}' xyzw.csv | tee >(socat - udp-sendto:127.0.0.1:5554) | awk -F "[ ,]" -W interactive -v start="$(date +%s%3N)" '{cmd="(date +'%s%3N')";cmd | getline d;print d-start,$1,$2,$3,$4;close(cmd)}' | feedgnuplot --stream 0.01 --exit --domain --lines --xlen 10000

