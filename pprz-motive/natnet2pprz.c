/*
gcc natnet2pprz.c -lpthread -o natnet2pprz
*/

/*

Timestamp : 17036.533
3066576
Valid: True
Id: 116
-3.432912 -2.937729 0.040714
-0.007760 -0.004241 -0.003297 0.999956


 STX , LENGTH, SENDER, DESTINATION, CLASS, ID, PAYLOAD, CHCKA, CHCKB
        msg = PprzMessage("datalink", "REMOTE_GPS_LOCAL")
        msg['ac_id'] = id_dict[i]
        msg['pad'] = 0
        msg['enu_x'] = pos[0]
        msg['enu_y'] = pos[1]
        msg['enu_z'] = pos[2]
        vel = compute_velocity(i)
        msg['enu_xd'] = vel[0]
        msg['enu_yd'] = vel[1]
        msg['enu_zd'] = vel[2]
        msg['tow'] = int(1000. * stamp) # TODO convert to GPS itow ?
        # convert quaternion to psi euler angle
        dcm_0_0 = 1.0 - 2.0 * (quat[1] * quat[1] + quat[2] * quat[2])
        dcm_1_0 = 2.0 * (quat[0] * quat[1] - quat[3] * quat[2])
        msg['course'] = 180. * np.arctan2(dcm_1_0, dcm_0_0) / 3.14

      <message name="REMOTE_GPS_LOCAL" id="56" link="forwarded">
      <description>
        Position and speed in local frame from a remote GPS or motion capture system
        Global position transformations are handled onboard if needed
      </description>
      <field name="ac_id"   type="uint8"/>
      <field name="pad"     type="uint8"/>
      <field name="enu_x"   type="float" unit="m"/>
      <field name="enu_y"   type="float" unit="m"/>
      <field name="enu_z"   type="float" unit="m"/>
      <field name="enu_xd"  type="float" unit="m/s"/>
      <field name="enu_yd"  type="float" unit="m/s"/>
      <field name="enu_zd"  type="float" unit="m/s"/>
      <field name="tow"     type="uint32"/>
      <field name="course"  type="float" unit="deg"/>
    </message>
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
#include <stdint.h>

#define GROUNDPORT 5000
#define BOARDPORT  5010

#define MAXMSGSIZE 250
#define STX 0x99
#define ID  56


pthread_cond_t cnd = PTHREAD_COND_INITIALIZER;
pthread_mutex_t mtx = PTHREAD_MUTEX_INITIALIZER;


void compute_check(char *ptr, int lg, uint8_t *ck_a,uint8_t *ck_b) {
  *ck_a=0;*ck_b=0;
  for (int c=0;c<lg;c++) {
    *ck_a = (*ck_a + c) % 256;
    *ck_b = (*ck_b + *ck_a) % 256;
  }
}


void build_pprz() {
  char msg[MAXMSGSIZE];
  float course,pos[3],vel[3];
  uint32_t tow;
  uint8_t acid=114,chcka,chckb;

  int cpt=0;
  char *ptr=(void*)msg;
  ptr[cpt++]=STX;   // STX
  ptr[cpt++]=10;    // LENGTH
  ptr[cpt++]=0;     // SENDER
  ptr[cpt++]=0;     // DESTINATION
  ptr[cpt++]=0;     // CLASS
  ptr[cpt++]=ID;    // ID

  memcpy(&ptr[cpt++],&acid,1);      // acid
  bzero(&ptr[cpt++],1);             // pad
  memcpy(&ptr[cpt+=(3*4)],pos,3*4); // enu_x,enu_y,enu_z
  memcpy(&ptr[cpt+=(3*4)],vel,3*4); // enu_xd,enu_yd,enu_zd
  memcpy(&ptr[cpt+=4],&tow,4);      // tow
  memcpy(&ptr[cpt+=4],&course,4);   // course

  compute_check((void *)msg,40,&chcka,&chckb);
  ptr[cpt++]=chcka;
  ptr[cpt++]=chckb;
}


void* recvloop(void *arg) {
  int one=1;
  int rcv;
  struct sockaddr_in from;
  int from_len;
  char buf[MAXMSGSIZE];
  int sockfd = -1;

  printf("recvloop\n");
  sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
  if(setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (char*)&one, sizeof(one))>=0){
    memset(&from, 0, sizeof(from));
    from.sin_family = AF_INET;
    from.sin_port = htons(GROUNDPORT);
    if (bind(sockfd, (struct sockaddr*)&from, sizeof(struct sockaddr)) >= 0) {
      while(1) {
        rcv = recvfrom(sockfd,(char *)buf,MAXMSGSIZE,0,(struct sockaddr *)&from,(socklen_t*)&from_len);
        pthread_cond_signal(& cnd);
      }
    }
  }
  return NULL;
}


void* sndloop(void *arg) {
  int one=1;
  int snd;
  struct sockaddr_in to;
  char buf[MAXMSGSIZE];
  int lg=0;
  int sockfd = -1;

  printf("sndloop\n");
  sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
  if(setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (char*)&one, sizeof(one))>=0){
    memset(&to, 0, sizeof(to));
    to.sin_family = AF_INET;
    to.sin_port = htons(BOARDPORT);
    pthread_mutex_lock(& mtx);
    while(1) {
      pthread_cond_wait(& cnd, & mtx);
      snd = sendto(sockfd,(char *)buf,lg,0,(struct sockaddr *)&to,sizeof(to));
    }
    pthread_mutex_unlock(& mtx);
  }
  return NULL;
}


int main( int argc, char*argv[]) {
  pthread_t gThr,bThr;
  printf("natnet2pprz\n");
  if(pthread_create(&gThr, NULL, &recvloop, NULL) <0)  exit(-1);
  if(pthread_create(&bThr, NULL, &sndloop, NULL) <0)  exit(-1);
  pthread_join(gThr,NULL);
  pthread_join(bThr,NULL);

  return(0);
}

