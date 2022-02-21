/*
gcc -c natnet_4.c
gcc natnet.c natnet_4.o -lpthread -o natnet

stdbuf -oL -eL ./natnet | tee >(socat - udp-sendto:127.0.0.1:4260)

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

#define DATAPORT 1511
#define MULTICASTIP "239.255.42.99"

#define MAX_PACKETSIZE 32768
#define OPTVAL_REQUEST_SIZE 32768

// NATNET version 
#define MAJOR 128
#define MINOR 150


#define MAX_BODIES  6
struct rigidbody_t {
  bool val;
  uint32_t id;
  float pos[3];
  float ori[4];
};
struct rigidbodies_t {
  uint32_t fr;
  uint32_t nb;
  struct rigidbody_t bodies[MAX_BODIES];
};
struct rigidbodies_t mybodies;


void MyUnpack(char* pData,int major,int minor,void *data);

int createsocketdata(bool multicast) {
  int sockfd = -1;
  int one=1;
  int bufsize = OPTVAL_REQUEST_SIZE;
  int optval = 0;
  int optvalsize = sizeof(int);

  if ((sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) < 0) exit(-1);
  if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (char*)&one, sizeof(one))  < 0) exit(-1);

  struct sockaddr_in my_addr;
  memset(&my_addr, 0, sizeof(my_addr));
  my_addr.sin_family = AF_INET;
  my_addr.sin_port = htons(DATAPORT);
  my_addr.sin_addr.s_addr = INADDR_ANY;
  if (bind(sockfd, (struct sockaddr*)&my_addr, sizeof(struct sockaddr)) < 0) exit(-1); 

  if(multicast) {
    struct ip_mreq group;
    group.imr_multiaddr.s_addr = inet_addr(MULTICASTIP);
    group.imr_interface.s_addr = INADDR_ANY;
    if (setsockopt(sockfd, IPPROTO_IP, IP_ADD_MEMBERSHIP, (char*)&group, sizeof(group)) <0)  exit(-1);
  }
  return(sockfd);
}



void* recvloop(void *arg) {
  int rcv;
  struct sockaddr_in their;
  int addr_len;
  char buf[MAX_PACKETSIZE];
  int fd = *((int*)arg);
  int messageID = 0;
  int nBytes = 0;
  int nBytesTotal = 0;
  struct rigidbody_t *tmp;

  while(1) {
    //printf("In\n");
    rcv = recvfrom(fd,(char *)buf,MAX_PACKETSIZE,0,(struct sockaddr *)&their,(socklen_t*)&addr_len);
    if(rcv>0) {
      MyUnpack(buf,MAJOR,MINOR,(void *)&mybodies);
      if(mybodies.nb>0) {
        //printf("----------------------------------------\n");
        //printf("%d\n",mybodies.fr);
        for (int j = 0; j < mybodies.nb; j++) {
          tmp = &(mybodies.bodies[j]); 
          //printf("Valid: %s\n", (tmp->val) ? "True" : "False");
          //printf("Id: %d\n",tmp->id);
          //printf("%f %f %f\n",tmp->pos[0],tmp->pos[1],tmp->pos[2]);
          //printf("%f %f %f %f\n",tmp->ori[0],tmp->ori[2],-tmp->ori[1],tmp->ori[3]);
          printf("nat %d %f %f %f %f %f %f %f\n",
            tmp->id,tmp->pos[0],tmp->pos[1],tmp->pos[2],tmp->ori[0],tmp->ori[2],-tmp->ori[1],tmp->ori[3]);
        }
        //printf("----------------------------------------\n");
      }
    }
  }
  return NULL;
}


int main( int argc, char*argv[]) {
  bool multicast = 1;
  int gDatSock=-1;
  pthread_t gDatThr;

  if ((argc>1)&&(!strcmp("-u", argv[1]))) multicast=0;
  gDatSock = createsocketdata(multicast);
  if (pthread_create(&gDatThr, NULL, &recvloop, &gDatSock) <0)  exit(-1);
  sleep(5);
  pthread_join(gDatThr,NULL);
  return(0);
}
