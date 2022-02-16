#!/bin/sh
cd ../xp_drone_standalone
test.x86_64

-------------------------------------------------------------------------------
cd ../vto_standalone
test.x86_64 &
cd vto_tools/pprz-motive
stdbuf -oL -eL ./natnet | tee >(socat - udp-sendto:127.0.0.1:5558)

-------------------------------------------------------------------------------
cd ../xp_vto_standalone
test.x86_64 &
../pprzsim-launch -a Explorer_114 -t nps
stdbuf -oL -eL ivyprobe '(.NPS_SPEED_POS.*|.NPS_RATE_ATTITUDE.*)' | ./pprz_nps.py  | tee >(socat - udp-sendto:127.0.0.1:5558)

-------------------------------------------------------------------------------
Android HyperImu apk
cd ../imu_standalone
test.x86_64 &
cd vto_tools/Android-ahrs/...
stdbuf -oL -eL ./test_ahrs 1 | tee >(socat - udp-sendto:127.0.0.1:5558) | awk -F "[ ,]" -W interactive -v start="$(date +%s%3N)" '{cmd="(date +'%s%3N')";cmd | getline d;print d-start,$5,$6,$7,$8;close(cmd)}' | feedgnuplot --stream 0.01 --exit --domain --lines --xlen 10000
