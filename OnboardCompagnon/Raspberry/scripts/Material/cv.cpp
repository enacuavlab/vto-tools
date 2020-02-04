#include "cv.h"
#include <opencv2/opencv.hpp>
#include <pthread.h>

#define SCALE 3/2
#define CAMOUTSTR "/tmp/camera3"

using namespace cv;
using namespace std;

/*****************************************************************************/
static pthread_mutex_t imv_mutex;
static pthread_cond_t imv_condv;
bool imv_ready=false;

static pthread_t img_thread;
static pthread_mutex_t img_mutex;
static pthread_cond_t img_condv;
bool img_ready=false;

/*****************************************************************************/
VideoWriter streamOut;
Mat imageIn;

typedef struct {
  int width;
  int height;
  int tabsize;
} pthreadarg_t;

typedef struct {
	int8_t x;
	int8_t y;
	uint16_t sad;
} motion_elt_t;
motion_elt_t *motionTabIn;

/*****************************************************************************/
static void *process_thread(void *ptr)
{
  pthreadarg_t *args = (pthreadarg_t *)ptr;

  unsigned int imageSize = ((args->width * args->height * sizeof(uint8_t))*SCALE);
  Mat imageOut(args->width, args->height, CV_8UC3,Scalar(0,0,0));

  unsigned int motionSize = (args->tabsize)*sizeof(motion_elt_t);
  motion_elt_t *motionTabOut = new motion_elt_t[args->tabsize];

  while (true) {

    pthread_mutex_lock(&img_mutex);
    while (!img_ready) pthread_cond_wait(&img_condv, &img_mutex);
    memcpy(imageOut.data,imageIn.data,imageSize);		
    img_ready=false;
    pthread_mutex_unlock(&img_mutex);

    pthread_mutex_lock(&imv_mutex);
    while (!imv_ready) pthread_cond_wait(&imv_condv, &imv_mutex);
    memcpy(motionTabOut ,motionTabIn, motionSize);
    imv_ready=false;
    pthread_mutex_unlock(&imv_mutex);

    cout << "Thread " << motionSize << endl;

    streamOut.write(imageOut);
  }
  return((void *)0);
}


void cv_init(int width, int height, int fps, int fmt)
{
  streamOut = VideoWriter(
    "appsrc ! "
    "shmsink socket-path=" CAMOUTSTR
    " wait-for-connection=false async=false sync=false",
    0,fps/1,Size(width,height),true);

  imageIn.create(width*SCALE, height, CV_8UC1);

  int motionTabSize = ((width/16)+1) * (height/16);
  motionTabIn = new motion_elt_t[motionTabSize];

  pthread_mutex_init(&imv_mutex, NULL);
  pthread_cond_init(&imv_condv, NULL);

  pthread_mutex_init(&img_mutex, NULL);
  pthread_cond_init(&img_condv, NULL);

  pthreadarg_t param = {width,height,motionTabSize};
  pthread_create(&img_thread, NULL, process_thread, (void *)&param);
}


void cv_process_img(uint8_t *p_buffer, int length, int64_t timestamp)
{
  cout << "imG " << length << endl;

  pthread_mutex_lock(&img_mutex);
  memcpy(imageIn.data, p_buffer, length);		
  img_ready=true;
  pthread_cond_signal(&img_condv);
  pthread_mutex_unlock(&img_mutex);
}


void cv_process_imv(uint8_t *p_buffer, int length, int64_t timestamp)
{
  cout << "imV " << length << endl;

  pthread_mutex_lock(&imv_mutex);
  memcpy(motionTabIn, p_buffer, length);
  imv_ready=true;
  pthread_cond_signal(&imv_condv);
  pthread_mutex_unlock(&imv_mutex);
}


void cv_close(void)
{
}
