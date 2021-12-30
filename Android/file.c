/*
gcc file.c -o file

*/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define STRSIZE 150

struct sample_t {
  float ugyr[3];
  float uacc[3];
  float umag[3];
};

#define MAXSAMPLES 5000
struct sample_t samples[MAXSAMPLES];

int main( int argc, char*argv[]) {
  struct sample_t bias;
  struct sample_t *ptr;
  int cpt=0;
  char buf[STRSIZE];
  FILE *in;

  in = fopen("5ms_sample.log","r");
  if(in!=NULL) {
    while(fgets(buf, STRSIZE, in) != NULL){
      ptr = &samples[cpt];
      bzero(ptr,sizeof(struct sample_t));
      sscanf(buf,"%f,%f,%f,%f,%f,%f,%f,%f,%f",&(ptr->ugyr[0]),&(ptr->ugyr[1]),&(ptr->ugyr[2]),\
        &(ptr->uacc[0]),&(ptr->uacc[1]),&(ptr->uacc[2]),&(ptr->umag[0]),&(ptr->umag[1]),&(ptr->umag[2]));
      printf("%f %f %f %f %f %f %f %f %f\n",ptr->ugyr[0],ptr->ugyr[1],ptr->ugyr[2],\
	ptr->uacc[0],ptr->uacc[1],ptr->uacc[2],ptr->umag[0],ptr->umag[1],ptr->umag[2]);
      cpt++;
    }
    for(int i=0;i<cpt;i++) {
      ptr = &samples[i];
      for(int j=0;j<3;j++) { 
        bias.ugyr[j]+=ptr->ugyr[j];bias.uacc[j]+=ptr->uacc[j];bias.umag[j]+=ptr->umag[j];
      }
    }
    cpt--;
    for(int j=0;j<3;j++) { 
      bias.ugyr[j]=bias.ugyr[j]/cpt;bias.uacc[j]=bias.uacc[j]/cpt;bias.umag[j]=bias.umag[j]/cpt;
    }
    printf("\n\n%f %f %f %f %f %f %f %f %f\n",bias.ugyr[0],bias.ugyr[1],bias.ugyr[2],\
      bias.uacc[0],bias.uacc[1],bias.uacc[2],bias.umag[0],bias.umag[1],bias.umag[2]);
  }
  printf("%d\n",cpt);
  return(0);
}
