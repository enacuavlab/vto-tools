#!/usr/bin/python3
import socket
import threading
import time
import docker
import subprocess
import sys
import re


def recv():
  print('Start receiving')
  while True: 
    try:
      data, server = sock.recvfrom(1518)
      print(data.decode(encoding="utf-8"))
    except Exception:
      print ('\nExit . . .\n')
      break


def snd(msg):
  sock.sendto(msg.encode(encoding="utf-8"),tello_add)


def check_connection(name):
  ret=False
  res1 = subprocess.run(
    ['docker','exec',i.id,'/bin/bash','-c','iwconfig | grep '+name], capture_output=True, text=True
  )
  if(len(res1.stdout)>0):
    wifidev = res1.stdout.split()[0]
    res2 = subprocess.run(
      ['docker','exec',i.id,'/bin/bash','-c','ip a | grep '+wifidev], capture_output=True, text=True
    )
    tmp=res2.stdout
    left="inet"
    ipwifi=(tmp[1+tmp.index(left)+len(left):tmp.index("/")])
    if (re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', ipwifi)):
      ret=True
  return(ret)


if __name__ == '__main__':

  if(len(sys.argv)==2):
    if(sys.argv[1] == '?'):
      for i in  docker.DockerClient().containers.list():
        print(i.name+" created")
        if(check_connection(i.name)): print(i.name+" connected")
    else:
      for i in  docker.DockerClient().containers.list():
        if(sys.argv[1] == i.name):
          if(check_connection(i.name)): 
            print(i.name+" created & connected")

            tello_add = (docker.DockerClient().containers.get(i.name).attrs['NetworkSettings']['IPAddress'], 8889)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            recvThread = threading.Thread(target=recv)
            recvThread.start()
          
            try:
              sock.sendto('command'.encode(encoding="utf-8"),tello_add)
              sock.sendto('streamon'.encode(encoding="utf-8"),tello_add)
              sock.sendto('battery?'.encode(encoding="utf-8"),tello_add)
              sock.sendto('sdk?'.encode(encoding="utf-8"),tello_add)

              while True:
                time.sleep(0.5)
            except KeyboardInterrupt:
              recvThread.join()
              exit()
