
void ahrs_fc_init(void){
}

bool ahrs_fc_align(struct FloatRates *lp_gyro, struct FloatVect3 *lp_accel,
                   struct FloatVect3 *lp_mag __attribute__((unused))){
}

void ahrs_fc_propagate(struct FloatRates *gyro, float dt){
}

void ahrs_fc_update_accel(struct FloatVect3 *accel, float dt){
}


void ahrs_fc_update_mag(struct FloatVect3 *mag __attribute__((unused)), float dt __attribute__((unused))){
}


void ahrs_fc_update_gps(struct GpsState *gps_s __attribute__((unused))){
}

void ahrs_fc_update_heading(float heading){
}

void ahrs_fc_realign_heading(float heading){
}

void main(int argc, char **argv){
  return(1);
}
