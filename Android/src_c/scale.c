/*
gcc scale.c -lm -o scale
*/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define STRSIZE 500

typedef struct elt_t elt_t;
struct elt_t {
  unsigned int stamp;
  float val;
  float valmed;
  bool filtered;
  struct elt_t *nxt;
};


int main( int argc, char*argv[]){
  char buf[STRSIZE];
  int cpt=0;
  int total=0;

  if(argc<=3) exit(-1);
  float scale=atof(argv[1]);
  float resolution=atoi(argv[2]);
  FILE *in=fopen(argv[3],"r");
  if(in!=NULL){
    elt_t* elt=malloc(sizeof(elt_t));
    elt->nxt=(struct elt_t*)0;
    elt_t* first=elt;
    while(fgets(buf, STRSIZE, in) != NULL){
      sscanf(buf,"%d %f",&(elt->stamp),&(elt->val));
      elt->filtered=false;
      (elt->nxt)=malloc(sizeof(elt_t));
      (elt->nxt->nxt)=(struct elt_t*)0;
      elt=elt->nxt;
      total++;
    }

    // Compute max mean
    elt=first;
    float max=elt->val;
    float min=max;
    elt=elt->nxt;
    while(elt->nxt!=NULL){
      if((elt->val)>max)max=(elt->val);
      if((elt->val)<min)min=(elt->val);
      elt=elt->nxt;
    }

    if(max==min)exit(-1);
    float range=max-min;
    float n=(max+min)/2;
    float sf=2*scale/range;

    elt=first;
    while(elt->nxt!=NULL){
      elt->valmed=((elt->val)-n)*sf;
      printf("%d %f\n",elt->stamp,elt->valmed);
      elt=elt->nxt;
    }

    // Neutral: n
    // Sensivity: resolution * sf
    
  }
  return(0);
}
