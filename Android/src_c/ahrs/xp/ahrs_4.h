#ifndef ahrs_4_h
#define ahrs_4_h

// https://ahrs.readthedocs.io/en/latest/filters/aqua.html

/*
  No full Pitch
*/

// Toulouse France Declination:+1.344° Inclination:59.128 
//#define MagRadDec 0.017453
//#define MagRadInc 1.029744

#include "ahrs_common.h"

void ahrs_filters_4(float c[3][3],float *r) {
  float a[4];
  a[0]=-c[ACCPOS][1]; // accX
  a[1]=-c[ACCPOS][0]; // accY
  a[2]=c[ACCPOS][2];  // accZ
  a[3]=0.f;
  quat_norm(a);

  float qacc[4]; // scalar,x,y,z
  if(a[2]>=0.f){
    float d=1.0f/sqrt(2.0f*(1+a[2]));
    qacc[3]=sqrt((1.0f+a[2])/2.0f);
    qacc[2]=a[1]*d; // Roll
    qacc[0]=-a[0]*d; // Pitch
    qacc[1]=0.f;
  } else {
    float d=1.0f/sqrt(2.0f*(1-a[2]));
    qacc[3]=-a[1]*d;
    qacc[2]=-sqrt((1.0f-a[2])/2.0f);
    qacc[0]=0.f;
    qacc[1]=a[0]*d;
  }
  quat_norm(qacc);

  float m[4];
  m[0]=c[MAGPOS][1];  // magX
  m[1]=c[MAGPOS][0];  // mag Y
  m[2]=0.f;           // magZ not needed
  m[3]=0.f;
  quat_norm(m);
  float t2=(m[0]*m[0]+m[1]*m[1]);
  float t=sqrt(t2);
  float qmag[4];
  if(m[0]>=0) {
    qmag[3]=sqrt(t2+t*m[0])/t;
    qmag[2]=0.f;
    qmag[0]=0.f;
    qmag[1]=m[1]/(sqrt(2.0f)*sqrt(t2+t*m[0]));
  } else {
    qmag[3]=m[1]/(sqrt(2.0f)*sqrt(t2-t*m[0]));
    qmag[2]=0.f;
    qmag[0]=0.f;
    qmag[1]=sqrt(t2-t*m[0])/t;
  }
  quat_norm(qmag);

  quat_mult(qacc,qmag,r);
  quat_norm(r);
}

#endif // ahrs_4_h
