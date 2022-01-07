/*
gcc scale.c -lm -o scale
*/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define STRSIZE 500

struct data_t {
  float val;
  float valmed;
  bool filtered;
};
typedef struct elt_t elt_t;
struct elt_t {
  unsigned int stamp;
  struct data_t data[3];
  struct elt_t *nxt;
};


int main( int argc, char*argv[]){
  char buf[STRSIZE];
  int cpt=0;
  int total=0;
  int i;

  if(argc<=3) exit(-1);
  float scale=atof(argv[1]);
  float resolution=atoi(argv[2]);
  FILE *in=fopen(argv[3],"r");
  if(in!=NULL){
    elt_t* elt=malloc(sizeof(elt_t));
    elt->nxt=(struct elt_t*)0;
    elt_t* first=elt;
    while(fgets(buf, STRSIZE, in) != NULL){
      sscanf(buf,"%d %f %f %f",&(elt->stamp),
        &(elt->data[0].val),&(elt->data[1].val),&(elt->data[2].val));
      for(i=0;i<3;i++)elt->data[i].filtered=false;
      (elt->nxt)=malloc(sizeof(elt_t));
      (elt->nxt->nxt)=(struct elt_t*)0;
      elt=elt->nxt;
      total++;
    }

    // Compute max min
    elt=first;
    float max[3],min[3];
    for(i=0;i<3;i++){max[i]=elt->data[i].val;min[i]=max[i];}
    elt=elt->nxt;
    while(elt->nxt!=NULL){
      for(i=0;i<3;i++){
        if((elt->data[i].val)>max[i])max[i]=(elt->data[i].val);
        if((elt->data[i].val)<min[i])min[i]=(elt->data[i].val);
      }
      elt=elt->nxt;
    }

    if((max[0]==min[0])||(max[1]==min[1])||(max[2]==min[2]))exit(-1);
    float range[3],n[3],sf[3];
    for(i=0;i<3;i++){
      range[i]=max[i]-min[i];
      n[i]=(max[i]+min[i])/2;
      sf[i]=2*scale/range[i];
    }

    elt=first;
    while(elt->nxt!=NULL){
      for(i=0;i<3;i++)elt->data[i].valmed=((elt->data[i].val)-n[i])*sf[i];
      elt=elt->nxt;
    }

    elt=first;
    while(elt->nxt!=NULL){
      printf("%d %f %f %f\n",elt->stamp,elt->data[0].valmed,elt->data[1].valmed,elt->data[2].valmed);
      elt=elt->nxt;
    }

    for(i=0;i<3;i++)printf("neutral=%f Sensitivity=%f\n",n[i],sf[i]*resolution);
    
  }
  return(0);
}
