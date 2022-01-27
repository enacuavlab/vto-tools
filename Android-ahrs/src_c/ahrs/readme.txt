https://blakejohnsonuf.com/projects/
https://github.com/bjohnsonfl/Madgwick_Filter


stdbuf -oL -eL ./test_madgwickFilter | awk -F "[ ,]" -W interactive -v start="$(date +%s%3N)" '{cmd="(date +'%s%3N')";cmd | getline d;print d-start,$1,$2,$3;close(cmd)}' | feedgnuplot --stream 0.01 --exit --domain --lines --xlen 10000

