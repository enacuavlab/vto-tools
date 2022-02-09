#!/bin/sh
/home/pprz/Projects/vto-tools/Simtools/sim_trials/sandbox/vto_standalone/test.x86_64 &
stdbuf -oL -eL /home/pprz/Projects/vto-tools/pprz-motive/natnet | tee >(socat - udp-sendto:127.0.0.1:5554)
