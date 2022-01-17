#ifndef ahrs_4_h
#define ahrs_4_h

// Toulouse France Declination:+1.344° Inclination:59.128 
#define MagRadDeclination 0.017453

#include "ahrs_common.h"

void ahrs_filters_4(float c[3][3],float *r) {
  float g[4],a[4]={0.f,0.0f,0.0f,0.0f}; 
  float accX=c[ACCPOS][0]; 
  float accY=c[ACCPOS][1]; 
  float accZ=c[ACCPOS][2]; 
  float roll=-0.5f*atan2(accY,sqrt(accX*accX+accZ*accZ)); 
  float pitch=0.5f*atan2(accX,sqrt(accY*accY+accZ*accZ));
//  a[0]=roll;
//  a[2]=pitch;

  float magX=c[MAGPOS][1]; 
  float magY=c[MAGPOS][0]; 
  float magZ=c[MAGPOS][2]; 
  float xh=magX*cos(pitch)+magY*sin(roll)*sin(pitch)-magZ*cos(roll)*sin(pitch);
  float yh=magY*cos(roll)+magZ*sin(roll);
  float yaw=atan2(yh,xh)+MagRadDeclination;
  a[1]=yaw;
/*
  a[1]=c[ACCPOS][1];  // YAW
  a[2]=c[ACCPOS][2];  // PITCH
  a[3]=-c[ACCPOS][0];  // ROLL
  a[0]=0.f;
  g[3]=1.0f;          // GRAVITY

  quat_norm(a);
  quat_mult(a,g,r);   
*/
  for(int i=0;i<4;i++)r[i]=a[i];
  r[3]=1.0f;
  quat_norm(r);
}

#endif // ahrs_4_h
