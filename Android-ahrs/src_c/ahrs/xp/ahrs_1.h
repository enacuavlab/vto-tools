#ifndef ahrs_1_h
#define ahrs_1_h

/*

- Pitch and roll limited to [-180,+180]
- No Yaw

*/

#include "ahrs_common.h"

void ahrs_filters_1(float c[3][3],float *r) {
  float accX=c[ACCPOS][0]; 
  float accY=c[ACCPOS][1]; 
  float accZ=c[ACCPOS][2]; 
  r[0]=0.5f*atan2(accY,sqrt(accX*accX+accZ*accZ)); // Pitch
  r[1]=0.f; // yaw
  r[2]=0.5f*atan2(accX,sqrt(accY*accY+accZ*accZ)); // Roll
  r[3]=1.0f;
  quat_norm(r);
}

#endif // ahrs_1_h
