Dual datalink(uplink)/telemetry(downlink) on zigbee and wifi
Wifi datalink/telemetry at least same as zigbee datalink/telemetry, for backup purpose
Wifi datalink can optionnaly send own or others ground ref position and at higher rate

Compagnon board: Nvidia xavier NX, raspberry pi ...

proxy-air.py
- mix message for the autopilot
- unique writer on the autopilot UART link
- full datalink is transmitted (stay coherent with zigbee datalink)
- keep sending datalink, even on x-guide stop or crash

socat tee
- dispatch message from the autopilot
- unique reader on the autopilot UART link
- keep sending extra-dl telemetry, even on proxy-air and x-guide stop or crash

x-guide.py
- monitor flight plan block changes, to request fc-rotor setting
- if fc-rotor is set, then it computes and send acceleration to indi guidance

Autpilot
- fc-rotor 
  - if activated, it propagates acceleration setting from the compagnon board
  - can be activated/de-activated on ground station, from setting pannel or flight plan

