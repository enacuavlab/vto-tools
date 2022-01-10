#ifndef ahrs_2_h
#define ahrs_2_h


void ahrs_filters_2float c[3][3],float *q_out) {
  quat_from_acc(v,q_out);
}


#endif // ahrs_2_h
