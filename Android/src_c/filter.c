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
  int noisewindows=atoi(argv[1]);
  int  noisepercent=atoi(argv[2]);
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

    // Compute mean
    elt=first;
    float neutral[3]={0.,0.,0.};
    cpt=0;
    while(elt!=NULL){
      for(i=0;i<3;i++)neutral[i]+=(elt->data[i].val);
      elt=elt->nxt;
      cpt++;
    }
    cpt--;
    for(i=0;i<3;i++)neutral[i]/=cpt;

    // Compute median L2 norm
    elt=first;
    while(elt!=NULL){
      for(i=0;i<3;i++)
        elt->data[i].valmed=sqrt(((elt->data[i].val)-neutral[i])*((elt->data[i].val)-neutral[i]));
      elt=elt->nxt;
    }
    elt=first;
    float tmp;
    cpt=0;
    while(elt!=NULL){ // Sorting
      for(i=0;i<3;i++){
        elt_t *eltin=elt;
        while(eltin!=NULL){
          if((eltin->data[i].valmed)<(elt->data[i].valmed)){
  	    tmp=elt->data[i].valmed;
            elt->data[i].valmed=eltin->data[i].valmed;
  	    eltin->data[i].valmed=tmp;
  	  }
          eltin=eltin->nxt;
        }
      }
      elt=elt->nxt;
      cpt++;
    }
    elt=first;
    float median[3]={0.,0.,0.};
    cpt=(cpt-1)/2;  
    while((elt!=NULL)&&(0<cpt--))elt=elt->nxt;
    for(i=0;i<3;i++)median[i]=elt->data[i].valmed; // Get value at the middle of sorted measurements

    // Filter noisy within a sliding window
    float noise_threshold[3];
    for(i=0;i<3;i++)noise_threshold[i]=median[i]*noisepercent/100.;
    float noise;
    float sd;
    int nb=0;
    elt=first;
    elt_t *eltin;
    while((total-2*noisewindows)>nb++){
      for(i=0;i<3;i++){
        eltin=elt;
        cpt=0;
        noise=0.;
        while((eltin!=NULL)&&((2*noisewindows)>cpt++)){
  	  noise+=eltin->data[i].val;
          eltin=eltin->nxt;
        }
        noise/=2*noisewindows;
        eltin=elt;
        cpt=0;
        sd=0.;
        while((eltin!=NULL)&&(2*noisewindows>cpt++)){
  	  sd+=(((eltin->data[i].val)-noise)*((eltin->data[i].val)-noise));
  	  eltin=eltin->nxt;
        }
        sd=sqrt(sd/(2*noisewindows)); //Standard deviation
        eltin=elt;
        cpt=0;
        while((eltin!=NULL)&&(2*noisewindows>cpt++)){
  	  if(sd>noise_threshold[i])elt->data[i].filtered=true;
  	  eltin=eltin->nxt;
        }
      }
      elt=elt->nxt;
    }

    // Output non filtered
    elt=first;
    while(elt!=NULL){
      if((elt->data[0].filtered==false)&&(elt->data[1].filtered==false)&&(elt->data[2].filtered==false)
        &&(elt->data[0].val!=0.)&&(elt->data[1].val!=0.)&&(elt->data[2].val!=0.))
          printf("%d %f %f %f\n",elt->stamp,elt->data[0].val,elt->data[1].val,elt->data[2].val);
      elt=elt->nxt;
    }
  }
  return(0);
}
