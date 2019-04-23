Install pprz proxy

------------------------------------------------------------
Projects/vto-tools/OnboardCompagnon/Raspberry/progs
tar cvf proxy.tar proxy/*

scp proxy.tar pi@192.168.1.xx:/home/pi

ssh pi@192.168.1.xx
pprz

tar xvf proxy.tar
rm proxy.tar
cd proxy
make 


sudo vi /etc/rc.local
/home/pi/proxy/exe/bridge &

