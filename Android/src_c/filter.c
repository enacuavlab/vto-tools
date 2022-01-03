/*
gcc filter.c -lm -o filter
*/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define MAGNOISEPERCENT 0.6 // Below 60%
#define MAGNOISEWINDOW	10

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
  int noisewindows=atoi(argv[1]);
  int  noisepercent=atoi(argv[2]);
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

    // Compute mean
    elt=first;
    float neutral=0.;
    cpt=0;
    while(elt!=NULL){
      neutral+=(elt->val);
      elt=elt->nxt;
      cpt++;
    }
    cpt--;
    neutral/=cpt;

    // Compute median L2 norm
    elt=first;
    while(elt!=NULL){
      elt->valmed=sqrt(((elt->val)-neutral)*((elt->val)-neutral));
      elt=elt->nxt;
    }
    elt=first;
    float tmp;
    cpt=0;
    while(elt!=NULL){
      elt_t *eltin=elt;
      while(eltin!=NULL){
        if((eltin->valmed)<(elt->valmed)) {
	  tmp=elt->valmed;
          elt->valmed=eltin->valmed;
	  eltin->valmed=tmp;
	}
        eltin=eltin->nxt;
      }
      elt=elt->nxt;
      cpt++;
    }
    elt=first;
    float median=0.;
    cpt=(cpt-1)/2;
    while((elt!=NULL)&&(0<cpt--)) elt=elt->nxt;
    median=elt->valmed;

    // Filter noisy within a sliding window
    float noise_threshold=median*noisepercent/100.;
    float noise;
    float sd;
    int nb=0;
    elt=first;
    elt_t *eltin;
    while((total-2*noisewindows)>nb++){
      eltin=elt;
      cpt=0;
      noise=0.;
      while((eltin!=NULL)&&((2*noisewindows)>cpt++)){
	noise+=eltin->val;
        eltin=eltin->nxt;
      }
      noise/=2*noisewindows;
      eltin=elt;
      cpt=0;
      sd=0.;
      while((eltin!=NULL)&&(2*noisewindows>cpt++)){
	sd+=(((eltin->val)-noise)*((eltin->val)-noise));
	eltin=eltin->nxt;
      }
      sd=sqrt(sd/(2*noisewindows));
      eltin=elt;
      cpt=0;
      while((eltin!=NULL)&&(2*noisewindows>cpt++)){
	if(sd>noise_threshold)elt->filtered=true;
	eltin=eltin->nxt;
      }
      elt=elt->nxt;
    }

    // Output non filtered
    elt=first;
    while(elt!=NULL){
      if((elt->filtered==false)&&(elt->val!=0.))printf("%d %f\n",elt->stamp,elt->val);
      elt=elt->nxt;
    }
  }
  return(0);
}
