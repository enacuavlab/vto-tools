/*
gcc calib.c -o calib

*/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define STRSIZE 500

typedef struct elt_t elt_t;
typedef struct elt_t {
  int val;
  struct elt_t *nxt;
} *llist;


int main( int argc, char*argv[]){
  char buf[STRSIZE];

  if(argc<=1) exit(-1);
  FILE *in=fopen(argv[1],"r");
  if(in!=NULL){
    while(fgets(buf, STRSIZE, in) != NULL){
      elt_t* elt = malloc(sizeof(elt_t));
     
/*
      ptr = malloc &samples[cpt];
      bzero(ptr,sizeof(struct sample_t));
      sscanf(buf,"%f,%f,%f,%f,%f,%f,%f,%f,%f",&(ptr->ugyr[0]),&(ptr->ugyr[1]),&(ptr->ugyr[2]),\
        &(ptr->uacc[0]),&(ptr->uacc[1]),&(ptr->uacc[2]),&(ptr->umag[0]),&(ptr->umag[1]),&(ptr->umag[2]));
      printf("%f %f %f %f %f %f %f %f %f\n",ptr->ugyr[0],ptr->ugyr[1],ptr->ugyr[2],\
	ptr->uacc[0],ptr->uacc[1],ptr->uacc[2],ptr->umag[0],ptr->umag[1],ptr->umag[2]);
      cpt++;
*/
    }
/*
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
*/
  }
  return(0);
}