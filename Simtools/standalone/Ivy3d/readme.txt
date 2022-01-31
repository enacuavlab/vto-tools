ivy3d.py
--------
  This is the visualization application.
  It takes position and attitude inputs from Ivy bus, and display 3D motion from models
  Inputs can be provided by five following applications

  ex: ivy3d.py
  ex: ivy3d.py 115 ROTORCRAFT_FP model_115 0.9,0.1,0.1
  ex: ivy3d.py 115 LTP_ENU model_115 0.1,0.5,0.5 
  ex: ivy3d.py 115 ROTORCRAFT_FP model_115 0.9,0.1,0.1 115 LTP_ENU model_115 0.1,0.5,0.5 
  ex: ivy3d.py 115 ROTORCRAFT_FP model_115 0.9,0.1,0.1 116 ROTORCRAFT_FP model_116 0.1,0.5,0.5 


track2ivy.py
------------
  This is the batch track player. 
  It takes position and attitude inputs from Optitrack/Motive csv file, and broadcast them on Ivy bus.
  Paparazzi is not needed

  ex: track2ivy.py samples/motivetrack_212_213_swarm.csv
  => ground GROUND_REF 212 LTP_ENU -2.311988,0.366909,0.080000 0.,0.,0. -0.999987,0.000542,0.004973,-0.000633 0.,0.,0. 0.
  => ground GROUND_REF 213 LTP_ENU -0.133346,0.392919,0.083475 0.,0.,0. -0.999767,0.011718,0.009899,-0.015185 0.,0.,0. 0.


paparazzi/sw/ground_segment/python/natnet3.x/natnet2ivy.py + NatNetClient.py
----------------------------------------------------------------------------
  This is the realtime track player. 
  It takes position and attitude inputs from Optitrack/Motive rigidbody tracker, and broadcast them on Ivy bus.
  Paparazzi is needed

  ex: natnet2ivy.py -ac 115 115 -ac 116 116  -s 192.168.1.230 -f 5 -gr
  => datalink REMOTE_GPS_LOCAL acid pos vel course
  => ground GROUND_REF acid LTP_ENU pos vel quat


paparazzi/sw/ground_segment/tmtc/link 
------------------------------------
  This is the realtime pprz track interface
  It can be used with real or simulated (nps) flights
  Paparazzi is needed

  ex: link  -udp
  ex: link  -d /dev/ttyUSB0 -transport xbee -s 57600

  ex:
    paparazzi/sw/ground_segment/tmtc/server -n
    paparazzi/sw/ground_segment/tmtc/link -udp
    paparazzi/sw/ground_segment/cockpit/gcs
    paparazzi/sw/simulator/pprzsim-launch -a ULYSSE_218 -t nps

  => 116 ROTORCRAFT_FP -371 -478 10 0 0 0 251 -57 52 0 0 10 52 0 0


paparazzi/sw/logalizer/play
---------------------------
  This is the batch pprz log player. 
  It takes inputs from onground or postprocessed onboard files, and broadcast them on Ivy bus
  Paparazzi is not needed

  ex: play samples/20_12_08__09_36_27_SD_no_GPS.log
  => replay116 ROTORCRAFT_FP 0 0 0 0 0 0 -329 90 51 0 0 0 51 0 0

 
ivymonPy/ivymon.py
------------------
  This is the ivy record and player. 
  It records and replay all or selected ivy messages.
  Paparazzi is not needed

