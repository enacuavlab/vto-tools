Build and flash autopilot
-------------------------

    <module name="telemetry" type="transparent">
      <configure name="MODEM_BAUD" value="B115200"/>
      <configure name="MODEM_PORT" value="UART1"/>
    </module>

    <module name="radio_control" type="datalink"/>


------------------------------------------------------------
Install pprz proxy
------------------

Projects/vto-tools/OnboardCompagnon/Raspberry/progs
tar cvf proxy.tar proxy/*

scp proxy.tar pi@192.168.1.xx:/home/pi

ssh pi@192.168.1.xx
pprz

tar xvf proxy.tar
rm proxy.tar

cd proxy
make

./exe/bridge
(/etc/rc.local)

update proxy/from_gcs with
paparazzi/var/aircrafts/karpet/ap/generated/
=> from_gcs/var/generated
paparazzi/var/include/pprzlink
=> from_gcs/var/include
paparazzi/var/share/pprzlink
=> from_gcs/var/include

./exe/...

------------------------------------------------------------
Connect to real wifi router
(no hotspot mobile)

------------------------------------------------------------
Run paparazzi ground station
----------------------------

/home/pprz/Projects/paparazzi/sw/ground_segment/tmtc/server 
/home/pprz/Projects/paparazzi/sw/ground_segment/tmtc/link  -udp 
/home/pprz/Projects/paparazzi/sw/ground_segment/cockpit/gcs 

