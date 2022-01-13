#ifndef ahrs_1_h
#define ahrs_1_h

/*
https://blog.endaq.com/quaternions-for-orientation
*/

#include "ahrs_common.h"

void ahrs_filters_1(float c[3][3],float *q_a) {
  q_a[0]=c[ACCPOS][0]*.10f;  // 
  q_a[1]=-c[ACCPOS][2]*.10f; // ROLL
  q_a[2]=c[ACCPOS][1]*.10f;  // PITCH
  q_a[3]=0;//c[ACCPOS][3]; 
/*
  q_a[0]=-c[ACCPOS][0]; // projection du vecteur ay, vers la droite
  q_a[2]=c[ACCPOS][1]; // projection de vecteur ax, vers l'avant // PITCH
  q_a[1]=c[ACCPOS][2]; // projection du vecteur az, vers le bas  // ROLL
  q_a[3]=0;
  quat_normalization(q_a);
  q_a[3]=sqrt(1-(q_a[0]*q_a[0])-(q_a[1]*q_a[1])-(q_a[2]*q_a[2]));
*/
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
