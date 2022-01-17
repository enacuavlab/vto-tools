#ifndef ahrs_common_h
#define ahrs_common_h

#include "math.h"

void quat_norm(float q[4]){
  float norm=sqrt(q[0]*q[0]+q[1]*q[1]+q[2]*q[2]+q[3]*q[3]);
  q[0]/=norm;
  q[1]/=norm;
  q[2]/=norm;
  q[3]/=norm;
}

void quat_mult(float q[4], float p[4], float *m){
  m[0]=q[0]*p[0]-q[1]*p[1]-q[2]*p[2]-q[3]*p[3];
  m[1]=q[1]*p[0]+q[0]*p[1]-q[3]*p[2]+q[2]*p[3];
  m[2]=q[2]*p[0]+q[3]*p[1]+q[0]*p[2]-q[1]*p[3];
  m[3]=q[3]*p[0]-q[2]*p[1]+q[1]*p[2]+q[0]*p[3];
}

#endif // ahrs_common_h
