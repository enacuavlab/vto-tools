/*
gcc udp.c -lpthread -lm -o udp

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
#include <math.h>


#define DATAPORT 5555

#define MAX_PACKETSIZE 1024

#define FORMAT	"%f,%f,%f,%f,%f,%f,%f,%f,%f"
#define ARGUMENTS &u[0][0],&u[0][1],&u[0][2],&u[1][0],&u[1][1],&u[1][2],&u[2][0],&u[2][1],&u[2][2]
#define MAGPOS 0
#define GYRPOS 1
#define ACCPOS 2

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


void update_imu(float c[3][3],float dt,float *q){  // W X Y Z
  float E[3];
  for(int i=0;i<3;i++)E[i]=c[GYRPOS][i]*dt;
  q[0] = cos(E[0]/2) * cos(E[1]/2) * cos(E[2]/2) + sin(E[0]/2) * sin(E[1]/2) * sin(E[2]/2);
  q[1] = sin(E[0]/2) * cos(E[1]/2) * cos(E[2]/2) - cos(E[0]/2) * sin(E[1]/2) * sin(E[2]/2);
  q[2] = cos(E[0]/2) * sin(E[1]/2) * cos(E[2]/2) + sin(E[0]/2) * cos(E[1]/2) * sin(E[2]/2);
  q[3] = cos(E[0]/2) * cos(E[1]/2) * sin(E[2]/2) - sin(E[0]/2) * sin(E[1]/2) * cos(E[2]/2);
}


void to_euler(float q[4],float *a){  // roll,picth,yaw
  a[0]=atan2(2*(q[0]*q[1]+q[2]*q[3]),1-2*(q[1]*q[1]+q[2]*q[2])); // roll (x-axis rotation)
  float sinp = 2*(q[0]*q[2]-q[3]*q[1]);  
  if (abs(sinp)>=1) {                                            // pitch (y-axis rotation)                       
    if(sinp<0.)a[1]=-M_PI/2;
    else a[1]=-M_PI/2;
  } else a[1]=asin(sinp);
  a[2]=atan2(2*(q[0]*q[3]+q[1]*q[2]),1-2*(q[2]*q[2]+q[3]*q[3]));  // yaw (z-axis rotation)
}


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
  int stamp;
  int rcv;
  struct sockaddr_in their;
  int addr_len;
  char buf[MAX_PACKETSIZE];
  int fd = *((int*)arg);
  struct timeval tv,tv_st,tv_res;

  timerclear(&tv_st);
  while(1) {
    rcv = recvfrom(fd,(char *)buf,MAX_PACKETSIZE,0,(struct sockaddr *)&their,(socklen_t*)&addr_len);
    if(rcv>0) {
      gettimeofday(&tv,NULL);
      if (timerisset(&tv_st)){
        timersub(&tv,&tv_st,&tv_res);
        //printf("sub %ld.%06ld\n",tv_res.tv_sec,tv_res.tv_usec);
      }
      memcpy(&tv_st,&tv,sizeof(tv));
      float u[3][3]; 
      sscanf(buf,FORMAT,ARGUMENTS);
      float c[3][3];
      apply_calibration(u,c);
      float q[4]; // W X Y Z
      update_imu(c,.5,(float *)&q);
      float a[3];
      to_euler(q,(float *)a);  // roll,picth,yaw
      printf("%f\n",a[0]);
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
