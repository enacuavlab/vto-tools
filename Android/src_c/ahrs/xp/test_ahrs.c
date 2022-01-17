/*
If using hotspot without router
sudo route add -net 224.0.0.0 netmask 240.0.0.0 dev wlp59s0

socat - UDP-RECV:5555,bind=0.0.0.0,reuseaddr,ip-add-membership=237.252.249.227:0.0.0.0

gcc test_ahrs.c -g -lpthread -lm -o test_ahrs

stdbuf -oL -eL ./test_ahrs 1 | tee >(socat - udp-sendto:127.0.0.1:5554) | awk -F "[ ,]" -W interactive -v start="$(date +%s%3N)" '{cmd="(date +'%s%3N')";cmd | getline d;print d-start,$1,$2,$3,$4;close(cmd)}' | feedgnuplot --stream 0.01 --exit --domain --lines --xlen 10000

socat - UDP-RECV:5554,bind=0.0.0.0,reuseaddr

*/
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <stdbool.h>
#include <sys/time.h>

#define DATAPORT 5555
//#define MCASTIP "237.252.249.227"
#define MAX_PACKETSIZE 1024

#define FORMAT	"%f,%f,%f,%f,%f,%f,%f,%f,%f"
#define ARGUMENTS &u[0][0],&u[0][1],&u[0][2],&u[1][0],&u[1][1],&u[1][2],&u[2][0],&u[2][1],&u[2][2]
#define MAGPOS 0
#define GYRPOS 1
#define ACCPOS 2

#include "ahrs_1.h"
#include "ahrs_2.h"
#include "ahrs_3.h"
#include "ahrs_4.h"
void (*ahrs_filters[4])(float[3][3],float *) = {ahrs_filters_1,ahrs_filters_2,ahrs_filters_3,ahrs_filters_4};

// Z UP

float ACC_NEUTRAL[3]={0.580,0.020,0.050};
float GYR_NEUTRAL[3]={0.006,-0.002,0.004};
float MAG_NEUTRAL[3]={78.178131,0.600000,43.228127};


void apply_calibration(float u[3][3],float c[][3]){  
  for(int i=0;i<3;i++){
    c[MAGPOS][i]=u[MAGPOS][i]-MAG_NEUTRAL[i];
    c[GYRPOS][i]=u[GYRPOS][i]-GYR_NEUTRAL[i];
    c[ACCPOS][i]=u[ACCPOS][i]-ACC_NEUTRAL[i];
  }
}


void* recvloop(void *arg) {
  int fd=-1;
  int one=1;
  int opt=*((int*)arg);
  struct sockaddr_in their;
  int addr_len;
  char buf[MAX_PACKETSIZE];
  struct timeval tv,tv_st,tv_res;

  fd=socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP);if(fd<0)exit(-1);
  if(setsockopt(fd,SOL_SOCKET,SO_REUSEADDR,(char*)&one,sizeof(one))<0)exit(-1);
  struct sockaddr_in my_addr;
  memset(&my_addr, 0, sizeof(my_addr));
  my_addr.sin_family = AF_INET;
  my_addr.sin_port = htons(DATAPORT);
  my_addr.sin_addr.s_addr = INADDR_ANY;
  if(bind(fd,(struct sockaddr*)&my_addr,sizeof(struct sockaddr))<0)exit(-1); 

#if defined MCASTIP
  struct ip_mreq group;
  group.imr_multiaddr.s_addr=inet_addr(MCASTIP);
  group.imr_interface.s_addr=INADDR_ANY;
  if(setsockopt(fd,IPPROTO_IP,IP_ADD_MEMBERSHIP,(char*)&group,sizeof(group))<0)exit(-1);
#endif

  timerclear(&tv_st);
  while(1) {
    int rcv = recvfrom(fd,(char *)buf,MAX_PACKETSIZE,0,(struct sockaddr *)&their,(socklen_t*)&addr_len);
    if(rcv>0) {
      gettimeofday(&tv,NULL);
      if (timerisset(&tv_st)){
        timersub(&tv,&tv_st,&tv_res);
        //printf("sub %ld.%06ld\n",tv_res.tv_sec,tv_res.tv_usec);
      }
      memcpy(&tv_st,&tv,sizeof(tv));
      float u[3][3]; 
      sscanf(buf,FORMAT,ARGUMENTS);
      if(opt==0)printf("%f %f %f %f %f %f %f %f %f\n",
        u[0][0],u[0][1],u[0][2],u[1][0],u[1][1],u[1][2],u[2][0],u[2][1],u[2][2]);
      else {
        float c[3][3];
        apply_calibration(u,c);
        float q[4];
        ahrs_filters[opt-1](c,q);
        //printf("%f %f %f %f\n",q[0],q[1],q[2],q[3]); // w x y z
	float n=1/sqrt(c[0][0]*c[0][0]+c[0][1]*c[0][1]+c[0][2]*c[0][2]);
        printf("%f %f %f %f %f %f %f\n",q[0],q[1],q[2],q[3],n*c[0][0],n*c[0][1],n*c[0][2]); // w x y z
      }
    }
  }
  return NULL;
}


int main( int argc, char*argv[]) {
  pthread_t gDatThr;
  int opt=0;
  if(argc==2)opt=atoi(argv[1]);
  if (pthread_create(&gDatThr,NULL,&recvloop,&opt) <0)  exit(-1);
  pthread_join(gDatThr,NULL);
  return(0);
}
