#ifndef ahrs_common_h
#define ahrs_common_h

#include "math.h"

float quat_norm(float q[4]){
  return sqrt(q[0]*q[0]+q[1]*q[1]+q[2]*q[2]+q[3]*q[3]);
}

void quat_normalization(float q[4]){
  float norm=quat_norm(q);
  q[0]/=norm;
  q[1]/=norm;
  q[2]/=norm;
  q[3]/=norm;
}

void quat_toeulerdeg(float q[4], float *v){ // W X Y Z -> roll pitch yaw
/*
  v[0]=atan2f((2*q[2]*q[3]-2*q[0]*q[1]),(2*q[0]*q[0]+2*q[3]*q[3]-1))*(180.0f/M_PI); // roll
  v[1]=-asinf(2*q[1]*q[3]+2*q[0]*q[2])*(180.0f/M_PI);                               // pitch
  v[2]=atan2f((2*q[1]*q[2]-2*q[0]*q[3]),(2*q[0]*q[0]+2*q[1]*q[1]-1))*(180.0f/M_PI); // yaw
*/
/*
  v[0]=atan2f(2*(q[0]*q[1]-q[2]*q[3]),1-2*(q[1]*q[1]+q[2]*q[2]))*(180.0f/M_PI); // roll
  v[1]=asin(2*(q[0]*q[2]-q[1]*q[3]))*(180.0f/M_PI);                              // pitch
  v[2]=atan2f(2*(q[0]*q[3]-q[1]*q[2]),1-2*(q[2]*q[2]+q[3]*q[3]))*(180.0f/M_PI); // yaw
*/
}

#endif // ahrs_common_h
