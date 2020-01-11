#!/bin/bash
UDP_PORT=3333
#2373670	ANT	1	494:-38:-35:-34
#2373670	PKT	495:0:495:0:0:0
function DATAOUT () {
  local IFS=$' \t\n:';
  while read A B C D E F G; do
    if [ "ANT" == "$B" ] 
    then
      echo "min:"$E" avr:"$F" max:"$G
    fi
  done
}
DATAOUT < <(socat udp-recv:${UDP_PORT} -)
