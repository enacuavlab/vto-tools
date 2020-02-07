#include "cv.h"
#include <opencv2/opencv.hpp>
#include <pthread.h>

#define SCALE 3/2
#define CAMOUTSTR "/tmp/camera3"

using namespace cv;
using namespace std;



/*****************************************************************************/
struct pthreadarg_t {
  int width;
  int height;
  int mbx;
  int mby;
  int tabsize;
} pthreadarg_t;

struct motion_elt_t {
 int8_t x;
 int8_t y;
 uint16_t sad;
};
motion_elt_t *motionTabIn;

static pthread_mutex_t imv_mutex;
bool imv_ready=false;

static pthread_t img_thread;
static pthread_mutex_t img_mutex;
static pthread_cond_t img_condv;
bool img_ready=false;

bool init_ready=false;

Mat imageIn;
VideoWriter streamOut;

static int8_t mline[8][8] = { \
  {1, 1, 1, 1, 1, 1, 1, 1 }, 
  {1, 1, 1, 1, 2, 2, 2, 2 }, 
  {1, 1, 2, 2, 2, 2, 3, 3 }, 
  {1, 1, 2, 2, 3, 3, 3, 4 }, 
  {1, 2, 2, 3, 3, 4, 4, 5 }, 
  {1, 2, 2, 3, 4, 5, 5, 6 }, 
  {1, 2, 3, 4, 5, 5, 6, 7 }, 
  {1, 2, 3, 4, 5, 6, 7, 8 } };

/*****************************************************************************/
static void *process_thread(void *ptr)
{
  struct pthreadarg_t args;
  memcpy(&args,ptr,sizeof(pthreadarg_t));

  unsigned int imageSize = ((args.width * args.height * sizeof(uint8_t))*SCALE);
  Mat imageOut(args.width, args.height, CV_8UC3,Scalar(0,0,0));

  unsigned int motionSize = (args.tabsize)*sizeof(motion_elt_t);
  motion_elt_t *motionTabOut = new motion_elt_t[args.tabsize];

  unsigned int uoffset=(args.width * args.height);
  unsigned int voffset=uoffset*5/4;

  unsigned int i,j,k,l,m,n,s;
  int8_t r;
  int x,y,p,q;

  while (true) {

    pthread_mutex_lock(&img_mutex);
    while (!img_ready) pthread_cond_wait(&img_condv, &img_mutex);
    memcpy(imageOut.data,imageIn.data,imageSize);		
    img_ready=false;
    pthread_mutex_unlock(&img_mutex);

    if(imv_ready) { 
      pthread_mutex_lock(&imv_mutex);
      memcpy(motionTabOut ,motionTabIn, motionSize);
      imv_ready=false;
      pthread_mutex_unlock(&imv_mutex);
    }

    for (j = 0; j < args.mby; j++) {
      for (i = 0; i < (args.mbx); i++) {

	x=((i-1)*8)+12;
        y=((j-1)*8)+12;
        k=(2*((y*(args.mbx)*16)+x));
        imageOut.data[k] = 0;

        l=(y*(args.mbx)*8)+x;
        m = (l & 1) ? 0xFF : 0x00;
        imageOut.data[uoffset+l] = imageOut.data[uoffset+l] & m;
        imageOut.data[voffset+l] = imageOut.data[voffset+l] & m;


        motion_elt_t *vec = motionTabOut + (i+(args.mbx+1)*j);
        if (vec->x == 0 && vec->y == 0) continue;
//      if (vec->sad > sad_limit) continue;

        p = ((vec->x)>>3);if(p>8)p=8;
        q = ((vec->y)>>3);if(q>8)q=8;
 
        p=8;q=8;

 	if((q!=0)||(p!=0)) {
	  if((q<9)&&(p<9)) {
            for (n = 0; n < p; n++) {
              r=mline[n][q]; 
              s=r;
cout << +(s) << endl;
              imageOut.data[k+(r*(n+1))+(r-1)*(args.width)]=0;
	    }
	  }
	}
      }
    }

    streamOut.write(imageOut);
  }
  return((void *)0);
}


/*****************************************************************************/
void cv_init(int width, int height, int fps, int fmt)
{
  streamOut = VideoWriter(
    "appsrc ! "
    "shmsink socket-path=" CAMOUTSTR
    " wait-for-connection=false async=false sync=false",
    0,fps/1,Size(width,height),true);

  imageIn.create(width*SCALE, height, CV_8UC1);

  int mbx = width/16;
  int mby = height/16;
  int motionTabSize = (mbx+1) * mby;
  motionTabIn = new motion_elt_t[motionTabSize];

  pthread_mutex_init(&imv_mutex, NULL);

  pthread_mutex_init(&img_mutex, NULL);
  pthread_cond_init(&img_condv, NULL);

  struct pthreadarg_t param = {width,height,mbx,mby,motionTabSize};
  pthread_create(&img_thread, NULL, process_thread, (void *)&param);

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
    memcpy(motionTabIn ,p_buffer, length);
    imv_ready=true;
    pthread_mutex_unlock(&imv_mutex);
  }
}


/*****************************************************************************/
void cv_close(void)
{
}
