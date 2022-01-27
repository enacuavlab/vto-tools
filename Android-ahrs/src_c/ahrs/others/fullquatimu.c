/*
gcc udp.c -g -lpthread -lm -o udp

https://github.com/rbv188/IMU-algorithm

The orientation is calculated as a quaternion that rotates the gravity vector from earth frame to sensor frame.
The gravity vector in the sensor frame is the accelerometer readings and the gravity vector in earth frame is (0,0,-1)

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


void quat_from_gyr(float c[3][3],float dt,float *q){
  float alpha = 0.5*dt; // wx,wy,wz in radians per second: time in seconds
  q[1]=alpha*(-c[GYRPOS][0]);
  q[2]=alpha*(-c[GYRPOS][1]);
  q[3]=alpha*(-c[GYRPOS][2]);
  q[0]=1-0.5*(q[1]*q[1]+q[2]*q[2]+q[3]*q[3]);
}


void quat_from_acc(float v[3],float *q){
  float norm_u_norm_v = 1.0;
  float cos_theta = -1.0*v[2];
  float half_cos = 0.7071*sqrt(1.0 + cos_theta);
  q[0] = half_cos;
  float temp = 0.5/half_cos;
  q[1]=-v[1]*temp;
  q[2]=v[0]*temp;
  q[3]=0.0;
}


void quat_conjugate(float q[4],float *q_out){
  q_out[0] =  q[0];
  q_out[1] = -q[1];
  q_out[2] = -q[2];
  q_out[3] = -q[3];
}


void quat_product(float q1[4],float q2[4], float *q_out){
  q_out[0] = (q1[0]*q2[0]) - (q1[1]*q2[1]) - (q1[2]*q2[2]) - (q1[3]*q2[3]);
  q_out[1] = (q1[0]*q2[1]) + (q1[1]*q2[0]) + (q1[2]*q2[3]) - (q1[3]*q2[2]);
  q_out[2] = (q1[0]*q2[2]) - (q1[1]*q2[3]) + (q1[2]*q2[0]) + (q1[3]*q2[1]);
  q_out[3] = (q1[0]*q2[3]) + (q1[1]*q2[2]) - (q1[2]*q2[1]) + (q1[3]*q2[0]);
}


void quat_rotate_vector(float v[3], float q[4], float *v_out){
  float q_vect[4]={0.0,v[0],v[1],v[2]};
  float q_inverse[4];
  quat_conjugate(q,q_inverse);
  float q_tmp[4];
  quat_product(q,q_vect,q_tmp);
  float q_rotvect[4];
  quat_product(q_tmp,q_inverse,q_rotvect);
  v_out[0]=q_rotvect[1];
  v_out[1]=q_rotvect[2];
  v_out[2]=q_rotvect[3];
}


void update_gravity_vector(float v_in[3],float c[3][3],float dt,float *v_out){
  float q_gyro[4];
  quat_from_gyr(c,dt,q_gyro);
  float v_gravity[3];
  quat_rotate_vector(v_in,q_gyro,v_out);
}


float InvSqrt(float x){
/*
  uint32_t i = 0x5F1F1412 - (*(uint32_t*)&x >> 1);
  float tmp = *(float*)&i;
  return tmp * (1.69000231f - 0.714158168f * x * tmp * tmp);
*/
  return(1/sqrt(x));
}


void vector_3d_normalize(float *v_out){
  float one_by_sqrt = InvSqrt(v_out[0]*v_out[0]+v_out[1]*v_out[1]+v_out[2]*v_out[2]);
  v_out[0] = v_out[0]*one_by_sqrt;
  v_out[1] = v_out[1]*one_by_sqrt;
  v_out[2] = v_out[2]*one_by_sqrt;
}


void sensor_gravity_normalized(float c[3][3],float *v_out){
  v_out[0] = c[ACCPOS][0];
  v_out[1] = c[ACCPOS][1];
  v_out[2] = c[ACCPOS][2];
  vector_3d_normalize(v_out);
}


float vector_3d_dot_product(float v1[3],float v2[3]){
  return(v1[0]*v2[0]+v1[1]*v2[1]+v1[2]*v2[2]);
}


float fusion_coeffecient(float virtual_gravity[3], float sensor_gravity[3]){
  float dot = vector_3d_dot_product(sensor_gravity,virtual_gravity);
  if (dot<=0.96)return 40.0;
  return 10.0;
}


void vector_3d_scale(float v1[3], float scale,float *v_out){
  v_out[0]=v1[0]*scale;
  v_out[1]=v1[1]*scale;
  v_out[2]=v1[2]*scale;
}


void vector_3d_sum(float v1[3], float v2[3], float *v_out){
  v_out[0]=v1[0]+v2[0];
  v_out[1]=v1[1]+v2[1];
  v_out[2]=v1[2]+v2[2];
}


void fuse_vector(float virtual_gravity[3],float sensor_gravity[3],float *v_out){
  float fusion = fusion_coeffecient(virtual_gravity, sensor_gravity);
  float v_tmp[3];
  vector_3d_scale(virtual_gravity,fusion,v_tmp);
  vector_3d_sum(v_tmp,sensor_gravity,v_out);
  vector_3d_normalize(v_out);
}


void update_fused_vector(float fused_vector[3],float c[3][3],float dt,float *v_out){
  float virtual_gravity[3];
  update_gravity_vector(fused_vector,c,dt,virtual_gravity);
  float sensor_gravity[3];
  sensor_gravity_normalized(c,sensor_gravity);
  fuse_vector(virtual_gravity,sensor_gravity,v_out);
}


void quat_to_eulerdeg(float q[4],float *a){  // roll,picth,yaw
  a[0]=atan2(2*(q[0]*q[1]+q[2]*q[3]),1-2*(q[1]*q[1]+q[2]*q[2]))*180/3.14;      // roll (x-axis rotation)
  a[1]=asin(2*(q[0]*q[2]-q[3]*q[1]))*180/3.14;                                 // pitch (y-axis rotation)   
  if(q[3]==0.)a[2]=0.0;
  else a[2]=atan2(2*(q[0]*q[3]+q[1]*q[2]),1-2*(q[2]*q[2]+q[3]*q[3]))*180/3.14; // yaw (z-axis rotation)
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
//      printf("%f %f %f %f %f %f %f %f %f\n",u[0][0],u[0][1],u[0][2],u[1][0],u[1][1],u[1][2],u[2][0],u[2][1],u[2][2]);
      float c[3][3];
      apply_calibration(u,c);
//      printf("%f %f %f %f %f %f %f %f %f\n",c[0][0],c[0][1],c[0][2],c[1][0],c[1][1],c[1][2],c[2][0],c[2][1],c[2][2]);
      float fused_vector[3]; 
      update_fused_vector(fused_vector,c,0.5,fused_vector);
//      printf("%f %f %f\n",fused_vector[0],fused_vector[1],fused_vector[2]);
      float q[4]; // W X Y Z
      quat_from_acc(fused_vector,q);
//      printf("%f %f %f %f\n",q[0],q[1],q[2],q[3]);
      float a[3];
      quat_to_eulerdeg(q,a);  // roll,picth,yaw
      printf("%f %f %f\n",a[0],a[1],a[2]);
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
