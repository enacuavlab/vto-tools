/*
gcc -g calib.c -lm -o calib
*/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define ACCNOISEPERCENT 0.1 // Below 10%
#define MAGNOISEPERCENT 0.6 // Below 60%
#define ACCNOISEWINDOW	20
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

  if(argc<=1) exit(-1);
  FILE *in=fopen(argv[1],"r");
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
    printf("neutral:%f\n",neutral);

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
    printf("median:%f\n",median);

    // Filter noisy within a sliding window
    float noise_threshold=median*ACCNOISEPERCENT;
    float noise;
    elt=first;
    elt_t *eltin,*eltout;
    while(elt!=NULL){
      eltin=elt;
      cpt=0;
      noise=0.;
      while((eltin!=NULL)&&(ACCNOISEWINDOW>cpt++)){
        eltin->valmed=sqrt(((eltin->val)*(eltin->val)));
	noise+=eltin->valmed;
        eltin=eltin->nxt;
      }
      noise/=ACCNOISEWINDOW;
      eltout=elt;
      elt=eltin;
      cpt=0;
      noise/=ACCNOISEPERCENT*10;
      while((eltout!=NULL)&&(ACCNOISEWINDOW>cpt++)){
        if(eltout->valmed > noise) eltout->filtered=true;
	printf("%f %f %d\n",noise,eltout->valmed,eltout->filtered);
	eltout=eltout->nxt;
      }
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
