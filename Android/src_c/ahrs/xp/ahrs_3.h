#ifndef ahrs_3_h
#define ahrs_3_h

/*

Non constant rotation

stdbuf -oL -eL ./test_ahrs 3 | tee >(socat - udp-sendto:127.0.0.1:5554) | awk -F "[ ,]" -W interactive -v start="$(date +%s%3N)" '{cmd="(date +'%s%3N')";cmd | getline d;print d-start,$5,$6,$7;close(cmd)}' | feedgnuplot --stream 0.01 --exit --domain --lines --xlen 10000
*/

#include "ahrs_common.h"

float r_pitch=0.0f;
float r_yaw=0.0f;
float r_roll=0.0f;

void ahrs_filters_3(float c[3][3],float *r) {
  float a[4];
  a[0]=-c[ACCPOS][0]; // AccY
  a[1]=-c[ACCPOS][1]; // AccX  
  a[2]=c[ACCPOS][2];  // AccZ 
  a[3]=0.0f;
  quat_norm(a);
  if(a[2]>0)r[0]=-asin(a[1]/(2+a[2])); // Pitch
  else r[0]=asin(a[1]/(2-a[2]));
  r[1]=0;//sin(r_yaw);
  if(a[2]>0)r[2]=-asin(a[0]/(2+a[2])); // Roll
  else r[2]=asin(a[0]/(2-a[2]));
  r[3]=1.0f-sqrt(r[0]*r[0]+r[1]*r[1]+r[2]*r[2]);

  quat_norm(r);
}

#endif // ahrs_3_h
