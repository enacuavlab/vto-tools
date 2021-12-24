/*
gcc natnet2pprz.c -lpthread -lrt -o natnet2pprz
*/

/*
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
#include <sys/time.h>
#include <signal.h>
#include <time.h>

#define GROUNDPORT 5000
#define BOARDPORT  5010

#define MAXMSGSIZE 250
#define STX 0x99
#define ID  56


struct g_struct_t {
  struct timeval tv;
  int len;
  char buf[MAXMSGSIZE];
} g_var;
pthread_cond_t g_cnd = PTHREAD_COND_INITIALIZER;
pthread_mutex_t g_mtx = PTHREAD_MUTEX_INITIALIZER;


void compute_check(char *ptr, int lg, uint8_t *ck_a,uint8_t *ck_b) {
  *ck_a=0;*ck_b=0;
  for (int c=0;c<lg;c++) {
    *ck_a = (*ck_a + c) % 256;
    *ck_b = (*ck_b + *ck_a) % 256;
  }
}


int build_pprz(void *buf) {
  float course,pos[3],vel[3];
  uint32_t tow;
  uint8_t acid=114,chcka,chckb;

  int cpt=0;
  char *ptr=(void*)buf;
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

  compute_check((void *)buf,40,&chcka,&chckb);
  ptr[cpt++]=chcka;
  ptr[cpt++]=chckb;

  return(42);
}


int processinput(void *buf) {
/*
Timestamp : 17036.533
3066576
Valid: True
Id: 116
-3.432912 -2.937729 0.040714
-0.007760 -0.004241 -0.003297 0.999956
*/

  int lg=build_pprz(buf);
  usleep(1000000);
  return(lg);
}


void sighler () {
  struct timeval tv;
  gettimeofday(&tv,NULL);
  printf("Tick %ld.%06ld\n",tv.tv_sec,tv.tv_usec);
}


int  init_timer(timer_t *timerid,struct itimerspec *in) {
  int Ret;

  pthread_attr_t attr;
  pthread_attr_init( &attr );

  struct sched_param parm;
  parm.sched_priority = 255;
  pthread_attr_setschedparam(&attr, &parm);

  struct sigevent sig;
  sig.sigev_notify = SIGEV_THREAD;
  sig.sigev_notify_function = sighler;
  sig.sigev_value.sival_int =20;
  sig.sigev_notify_attributes = &attr;

  Ret = timer_create(CLOCK_REALTIME, &sig, timerid);
  if (Ret == 0) {
    in->it_interval.tv_sec = 2;
    in->it_interval.tv_nsec = 0;
    in->it_value.tv_sec = in->it_interval.tv_sec;
    in->it_value.tv_nsec = in->it_interval.tv_nsec;
  }

  return(Ret);
}


void* recvloop(void *arg) {
  struct timeval tv;
  int one=1;
  bool once=true;
  int rcv;
  struct sockaddr_in from;
  int from_len;
  char buf[MAXMSGSIZE];
  int sockfd = -1;

  struct itimerspec in, out;
  timer_t timerid;
  int ret=init_timer(&timerid,&in);

  printf("recvloop\n");
  sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
  if(setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (char*)&one, sizeof(one))>=0){
    memset(&from, 0, sizeof(from));
    from.sin_family = AF_INET;
    from.sin_addr.s_addr = htonl(INADDR_ANY);
    from.sin_port = htons(GROUNDPORT);
    if (bind(sockfd, (struct sockaddr*)&from, sizeof(struct sockaddr)) >= 0) {
      while(1) {
	usleep(100000);
        //rcv = recvfrom(sockfd,(char *)buf,MAXMSGSIZE,0,(struct sockaddr *)&from,(socklen_t*)&from_len);
        pthread_mutex_lock(& g_mtx);
	gettimeofday(&tv,NULL);
	memcpy(&g_var.tv,&tv,sizeof(tv));
	g_var.len = rcv;
	memcpy(g_var.buf,buf,rcv);
        pthread_mutex_unlock(& g_mtx);
        pthread_cond_signal(& g_cnd);
        printf("rcv %ld.%06ld\n",tv.tv_sec,tv.tv_usec);
	if(once) {
	  once=false;
	  timer_settime(timerid,0,&in,&out);
	  printf("START TIMER\n");
	}
      }
    }
  }
  return NULL;
}


void* sndloop(void *arg) {
  struct timeval tv,tv_snd,tv_res,tv_ref={4,0};
  int one=1;
  int snd;
  struct sockaddr_in to;
  char buf[MAXMSGSIZE];
  int lg=0;
  int sockfd = -1;
  bool reqsnd=false;

  printf("sndloop\n");

  timerclear(&tv_snd);
  sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
  if(setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (char*)&one, sizeof(one))>=0){
    memset(&to, 0, sizeof(to));
    to.sin_family = AF_INET;
    to.sin_port = htons(BOARDPORT);
    while(1) {
      pthread_mutex_lock(& g_mtx);
      pthread_cond_wait(& g_cnd, & g_mtx);
      memcpy(&tv,&g_var.tv,sizeof(tv));
      snd = g_var.len;
      memcpy(buf,g_var.buf,snd);
      pthread_mutex_unlock(& g_mtx);

      printf("before proc %ld.%06ld\n",tv.tv_sec,tv.tv_usec);
      lg = processinput(buf);
      gettimeofday(&tv,NULL);
      printf("after proc %ld.%06ld\n",tv.tv_sec,tv.tv_usec);

      if (timerisset(&tv_snd)) {
	timersub(&tv,&tv_snd,&tv_res);
        printf("sub %ld.%06ld\n",tv_res.tv_sec,tv_res.tv_usec);
	if(!timercmp(&tv_res,&tv_ref,<))reqsnd=true;
      } else reqsnd=true;

      if(reqsnd) {
	reqsnd=false;
	memcpy(&tv_snd,&tv,sizeof(tv));
        printf("snd %ld.%06ld\n",tv.tv_sec,tv.tv_usec);
        //snd = sendto(sockfd,(char *)buf,lg,0,(struct sockaddr *)&to,sizeof(to));
      }
    }
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

