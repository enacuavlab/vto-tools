#ifndef ahrs_2_h
#define ahrs_2_h

/*
https://ahrs.readthedocs.io/en/latest/filters/aqua.html

- Pitch and roll not limited but not continuous
- No Yaw

*/

#include "ahrs_common.h"

void ahrs_filters_2(float c[3][3],float *r) {
  float den;
  float a[4];
  a[0]=c[ACCPOS][0]; 
  a[1]=c[ACCPOS][1]; 
  a[2]=c[ACCPOS][2];  
  a[3]=0.0f;
  quat_norm(a);
  float accX=a[0];
  float accY=a[1];
  float accZ=a[2];
  if(accZ>=0){
    den=1.0f/sqrt(2*(1+accZ));
    r[2]=sqrt((1+accZ)/2.0f);  // Pitch
    r[1]=-accY*den;
    r[3]=-accX*den;
    r[0]=0;
  } else {
    den=1.0f*sqrt(2*(1-accZ));
    r[2]=-accY*den;
    r[1]=sqrt((1-accZ)/2.0f);
    r[3]=0;
    r[0]=accX*den;
  }
  quat_norm(r);
}

#endif // ahrs_2_h
