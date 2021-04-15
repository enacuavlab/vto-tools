#include "cv.h"
#include <opencv2/opencv.hpp>
#include <pthread.h>

#include <sys/socket.h>
#include <arpa/inet.h>

#include <opencv2/aruco.hpp>

using namespace cv::aruco;
using namespace cv;
using namespace std;

/*****************************************************************************/
#define SAD_LIMIT 2000
#define streamOutGstStr "appsrc ! shmsink socket-path=/tmp/camera3 wait-for-connection=false async=false sync=false"

/*****************************************************************************/
struct sockaddr_in addr;
unsigned int addrLen = sizeof(addr);
int fdgcs;

FileStorage fs;
Mat cameraMatrix, distCoeffs;

struct motion_elt_t {
  int8_t x;
  int8_t y;
  uint16_t sad;
};
static motion_elt_t *motionIn;
static Mat1b gray;
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
  Mat3b grayBGR;
  Mat colormap;
  int32_t sum_x,sum_y;

  int mbx = width/16;
  int mby = height/16;
  int mbxy = (8 * mbx * mby);
  unsigned int motionSize = ((mbx+1)*mby) * sizeof(struct motion_elt_t); 
  motion_elt_t *motionOut = new motion_elt_t[(mbx+1)*mby];

  Ptr<Dictionary> dictionary = getPredefinedDictionary(DICT_6X6_250);
//  Ptr<DetectorParameters> parameters = DetectorParameters::create();
  vector<vector<Point2f>> markerCorners;
//  vector<vector<Point2f>> rejectedCandidates;
  vector<int> markerIds;
  vector<vector<Point2f>> corners;
  char msgbuff[40];


  while (true) {
    pthread_mutex_lock(&img_mutex);
    while (!img_ready) pthread_cond_wait(&img_condv, &img_mutex);
    cvtColor(gray, grayBGR, COLOR_GRAY2BGR);
    applyColorMap(grayBGR, colormap, COLORMAP_JET); 

    img_ready=false;
    pthread_mutex_unlock(&img_mutex); 

    if(imv_ready) { 
      pthread_mutex_lock(&imv_mutex);
      memcpy(motionOut ,motionIn, motionSize);
      imv_ready=false;
      pthread_mutex_unlock(&imv_mutex);
    }  

    sum_x=0;sum_y=0;
    for (int j=0;j<mby;j++) {
      for (int i=0;i<mbx;i++) { 
        motion_elt_t *vec = motionOut + (i+(mbx+1)*j); 
        if (vec->x == 0 && vec->y == 0) continue;
        if (vec->sad > SAD_LIMIT) continue;
        int x = i*16 + 8;
        int y = j*16 + 8;
        float intensity = vec->sad;
        intensity = round(255 * intensity / SAD_LIMIT);
        if (intensity > 255) intensity = 255;
        uint8_t *ptr = colormap.ptr<uchar>(0);
        uint8_t idx = 3*(uint8_t)intensity;
//        arrowedLine(grayBGR, Point(x+vec->x, y+vec->y),
//                             Point(x, y),
//                             Scalar(ptr[idx], ptr[idx+1], ptr[idx+2])); 

        sum_x += (intensity * vec->x);
        sum_y += (intensity * vec->y);
      }
    } 

    sum_x = (sum_x/mbxy);
    sum_y = (sum_y/mbxy);
    arrowedLine(grayBGR, Point(320,240),Point(320+sum_x,240+sum_y),Scalar(0,255,0),5);

    /**********************************************************************/

//    detectMarkers(gray, dictionary, markerCorners, markerIds, parameters, rejectedCandidates);
    detectMarkers(gray, dictionary, markerCorners, markerIds);
    int n=markerIds.size(); 
    if(n>0) {
      Point2f center=(0.25*(markerCorners[0][0]+markerCorners[0][1]+markerCorners[0][2]+markerCorners[0][3]));
      sprintf(msgbuff,"%d %d\n",(int)center.x,(int)center.y);
      sendto(fdgcs,msgbuff,strlen(msgbuff),0,(struct sockaddr*)&addr,sizeof(addr));
      drawDetectedMarkers(grayBGR, markerCorners, markerIds);
//      vector<Vec3d> rvecs, tvecs;
//      estimatePoseSingleMarkers(markerCorners, 0.05, cameraMatrix, distCoeffs, rvecs, tvecs);
//      for(int i=0; i<markerIds.size(); i++)
//        drawAxis(grayBGR, cameraMatrix, distCoeffs, rvecs[i], tvecs[i], 0.1);
    }
    strOut.write(grayBGR);

    /**********************************************************************/

  }
  return((void *)0);
}

/*****************************************************************************/
void cv_init(int w, int h, int f, int fmt)
{
  addr.sin_family = AF_INET;
  addr.sin_port = htons(4200);
  addr.sin_addr.s_addr = inet_addr("127.0.0.1");
  fdgcs = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);

  fs.open("/home/pi/Projects/opencv_test/test.xml", FileStorage::READ);
  fs["matrix"] >> cameraMatrix;
  fs["dist"] >> distCoeffs;

  width=w;height=h;fps=f;

  gray = Mat(height, width, CV_8UC1);
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
    memcpy(gray.data, p_buffer, length);		
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
