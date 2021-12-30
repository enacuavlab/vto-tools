/*
gcc test.c -lpthread -o test

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

#define MAX_PACKETSIZE 1024


int createsocketdata() {
  int sockfd = -1;
  int one=1;

  if ((sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) < 0) exit(-1);
  if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (char*)&one, sizeof(one))  < 0) exit(-1);

  struct sockaddr_in my_addr;
  memset(&my_addr, 0, sizeof(my_addr));
  my_addr.sin_family = AF_INET;
  my_addr.sin_port = htons(DATAPORT);
  my_addr.sin_addr.s_addr = INADDR_ANY;
  if (bind(sockfd, (struct sockaddr*)&my_addr, sizeof(struct sockaddr)) < 0) exit(-1); 

  return(sockfd);
}


void* recvloop(void *arg) {
  int rcv;
  struct sockaddr_in their;
  int addr_len;
  char buf[MAX_PACKETSIZE];
  int fd = *((int*)arg);
  struct timeval tv,tv_st,tv_res;
  float ugyr[3],uacc[3],umag[3],gyr[3],acc[3],mag[3];

  timerclear(&tv_st);
  while(1) {
    rcv = recvfrom(fd,(char *)buf,MAX_PACKETSIZE,0,(struct sockaddr *)&their,(socklen_t*)&addr_len);
    if(rcv>0) {
      gettimeofday(&tv,NULL);
      if (timerisset(&tv_st)){
        timersub(&tv,&tv_st,&tv_res);
        printf("sub %ld.%06ld\n",tv_res.tv_sec,tv_res.tv_usec);
      }
      memcpy(&tv_st,&tv,sizeof(tv));
      printf("%s\n",buf);
      sscanf(buf,"%f,%f,%f,%f,%f,%f,%f,%f,%F",&ugyr[0],&ugyr[1],&ugyr[2],&uacc[0],&uacc[1],&uacc[2],&umag[0],&umag[1],&umag[2]);
      printf("%f %f %f %f %f %f %f %f %f\n",ugyr[0],ugyr[1],ugyr[2],uacc[0],uacc[1],uacc[2],umag[0],umag[1],umag[2]);
    }
  }
  return NULL;
}


int main( int argc, char*argv[]) {
  int gDatSock=-1;
  pthread_t gDatThr;

  gDatSock = createsocketdata();
  if (pthread_create(&gDatThr, NULL, &recvloop, &gDatSock) <0)  exit(-1);
  pthread_join(gDatThr,NULL);
  return(0);
}
