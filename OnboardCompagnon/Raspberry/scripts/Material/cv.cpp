#include "cv.h"
#include <opencv2/opencv.hpp>
#include <pthread.h>

using namespace cv;
using namespace std;

/*****************************************************************************/
#define SAD_LIMIT 150
#define SCALE 3/2
#define streamOutGstStr "appsrc ! shmsink socket-path=/tmp/camera3 wait-for-connection=false async=false sync=false"

/*****************************************************************************/
struct motion_elt_t {
 int8_t x;
 int8_t y;
 uint16_t sad;
};
static motion_elt_t *motionIn;
static Mat imageIn;
static int width,height,fps;

static pthread_mutex_t imv_mutex;
static bool imv_ready=false;

static pthread_t img_thread;
static pthread_mutex_t img_mutex;
static pthread_cond_t img_condv;
static bool img_ready=false;

static bool init_ready=false;

/*****************************************************************************/
static void *process_thread(void *ptr)
{
  VideoWriter strOut = VideoWriter(streamOutGstStr,0,fps/1,Size(width,height),true);

  unsigned int imageSize = ((width * height * sizeof(uint8_t))*SCALE);
  Mat imageOut(width, height, CV_8UC3,Scalar(0,0,0));
  char* imgptr = imageOut.ptr<char>(0);

  int mbx = width/16;
  int mby = height/16;
  unsigned int motionSize = ((mbx+1)*mby) * sizeof(struct motion_elt_t); 
  motion_elt_t *motionOut = new motion_elt_t[(mbx+1)*mby];

  unsigned int uoffset=(width * height);
  unsigned int voffset=uoffset*5/4;

  unsigned int k,l,m,s;
  int x,y,p,q,a,b;
  int8_t r;

  int8_t mline[17][17];
  for(int y=0;y<=16;y++) {
    for(int x=0;x<=16;x++) {
      mline[x][y]=floor((x*y/16.0)+0.5);
    }
  }

  while (true) {

    pthread_mutex_lock(&img_mutex);
    while (!img_ready) pthread_cond_wait(&img_condv, &img_mutex);
    memcpy(imageOut.data,imageIn.data,imageSize);		
    img_ready=false;
    pthread_mutex_unlock(&img_mutex);

    if(imv_ready) { 
      pthread_mutex_lock(&imv_mutex);
      memcpy(motionOut ,motionIn, motionSize);
      imv_ready=false;
      pthread_mutex_unlock(&imv_mutex);
    }

    for (int j=1;j<(mby-1);j++) {
      for (int i=1;i< (mbx-1);i++) {

	x=((i-1)*8)+12;
        y=((j-1)*8)+12;
        k=(2*((y*(mbx)*16)+x));
	imgptr[k]=0;

        l=(y*(mbx)*8)+x;
        m = (l & 1) ? 0xFF : 0x00;
        imgptr[uoffset+l] = imgptr[uoffset+l] & m;
        imgptr[voffset+l] = imgptr[voffset+l] & m;

        motion_elt_t *vec = motionOut + (i+(mbx+1)*j);

        if (vec->x == 0 && vec->y == 0) continue;
        if (vec->sad > SAD_LIMIT) continue;

        p = ((vec->x)>>2);
	if(p<0) {a=-1;p=-p;} else a=1;
	if(p>15) p=15;
        q = ((vec->y)>>2);
	if(q<0) {b=-1;q=-q;} else b=1;
	if(q>15) q=15;

        if(p<q) {
          for (int n=0;n<=q;n++) {
            r=mline[n][p]; 
	    s=(b*n*width)-(a*r);
            imgptr[k+s]=0;
	  }
	} else {
          for (int n=0;n<=p;n++) {
            r=mline[n][q];
	    s=(b*r*width)-(a*n);
            imgptr[k+s]=0;
	  }
	}
      }
    }
    strOut.write(imageOut);
  }
  return((void *)0);
}


/*****************************************************************************/
void cv_init(int w, int h, int f, int fmt)
{
  width=w;height=h;fps=f;

  imageIn.create(width*SCALE, height, CV_8UC1);
  motionIn = new motion_elt_t[((width/16)+1) * (height/16)];

  pthread_mutex_init(&imv_mutex, NULL);

  pthread_mutex_init(&img_mutex, NULL);
  pthread_cond_init(&img_condv, NULL);

  pthread_create(&img_thread, NULL, process_thread, (void *)0);

  init_ready=true;
}


/*****************************************************************************/
void cv_process_img(uint8_t *p_buffer, int length, int64_t timestamp)
{
  if (init_ready) {
    pthread_mutex_lock(&img_mutex);
    memcpy(imageIn.data, p_buffer, length);		
    img_ready=true;
    pthread_cond_signal(&img_condv);
    pthread_mutex_unlock(&img_mutex);
  }
}


/*****************************************************************************/
void cv_process_imv(uint8_t *p_buffer, int length, int64_t timestamp)
{
  if (init_ready) {
    pthread_mutex_lock(&imv_mutex);
    memcpy(motionIn ,p_buffer, length);
    imv_ready=true;
    pthread_mutex_unlock(&imv_mutex);
  }
}


/*****************************************************************************/
void cv_close(void)
{
}
