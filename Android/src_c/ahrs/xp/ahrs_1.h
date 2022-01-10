#ifndef ahrs_1_h
#define ahrs_1_h

/*
https://blog.endaq.com/quaternions-for-orientation
*/

#include "ahrs_common.h"

void ahrs_filters_1(float c[3][3],float *q_a) {
  q_a[0]=0;
  q_a[1]=c[ACCPOS][0];
  q_a[2]=c[ACCPOS][1];
  q_a[3]=c[ACCPOS][2];
  quat_normalization(q_a);
/*
  cos(bx)*cos(bx)+cos(by)*cos(by)+cos(bz)*cos(bz)=1
  cos(a2)*cos(a2)+sin(a2)*sin(a2)+(cos(bx)*cos(bx)+cos(by)*cos(by)+sin(bz)*sin(bz))=1

  q[0]=cos(a2);
  q[1]=sin(a2)cos(bx);
  q[2]=sin(a2)cos(by);
  q[3]=sin(a2)cos(bz);
*/

}


#endif // ahrs_1_h
