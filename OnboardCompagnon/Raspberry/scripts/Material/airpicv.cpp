/*
                        | --> camera1 (x-h264) 
 rpicamsrc (x-h264) --> |   
                        | omxh264dec --> camera2 (x-raw,I420)

	                                  |
	                                  | --> VideoCapture (yuv) VideoWriter --> camera3 (x-raw,I420) 
*/

#include <opencv2/opencv.hpp>
#include <iostream>
#include <mutex>
#include <thread>
#include <condition_variable>
#include <chrono>

//#include <sys/types.h> 
#include <sys/socket.h> 
//#include <arpa/inet.h> 
#include <netinet/in.h> 

/*
g++ -g airpicv.cpp -o airpicv `pkg-config --cflags --libs opencv4` -lpthread 

or
g++ -g airpicv.cpp -o airpicv -I/usr/local/include/opencv4 -lopencv_core -lopencv_objdetect -lopencv_videoio -lopencv_imgproc -lpthread
*/

#define WIDTH 1280
#define HEIGHT 720
#define FPS 30
#define SCALE 3/2

#define WIDTHSTR "1280"
#define HEIGHTSTR "720"
#define FPSSTR "30"

#define CAMINSTR "/tmp/camera2"
#define CAMOUTSTR "/tmp/camera3"

using namespace cv;
using namespace std;


/*****************************************************************************/
std::mutex mtx;
std::condition_variable cond;
Mat dataIn = Mat(HEIGHT*SCALE,WIDTH,CV_8UC1); 
bool ready = false;
bool readyDetect = false;

struct sockaddr_in UdpOut;
int UdpOutSocket;

Rect detect;
unsigned int fpsIn = 0;
unsigned int fpsProc = 0;

/*****************************************************************************/
void image_processing(void)
{
  double scale=1;
  CascadeClassifier cascade("/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml");
  vector<Rect> faces;
  Mat gray;
  Mat img1(HEIGHT,WIDTH,CV_8UC3,Scalar(0,0,0));

  char buff[50];

  while (true) {
    std::unique_lock<std::mutex> lck(mtx);
    cond.wait(lck, []{return ready;});

    cvtColor(dataIn,img1,COLOR_YUV2BGR_I420);
    cvtColor(img1,gray,COLOR_BGR2GRAY);

    cascade.detectMultiScale(gray, faces, 2.0, 1, 0|CASCADE_SCALE_IMAGE, Size(80, 80) );
    if(faces.size()>0) {
      detect = faces[0];
      readyDetect = true;

      sprintf(buff, "%d,%d,%d,%d\n",detect.x,detect.y,detect.height,detect.width);
      sendto(UdpOutSocket, buff, strlen(buff), 0, (const struct sockaddr *) &UdpOut, sizeof(UdpOut));

    } else {
      readyDetect = false;
    }

    fpsProc++;
    ready = false;
  }
}

/*****************************************************************************/
unsigned int width=WIDTH,height=HEIGHT;
void y_overlay(Mat *param)
{
  unsigned int ax=detect.x,bx=ax+detect.width;
  unsigned int ay=detect.y,by=ay+detect.height;
  unsigned int ayl=ay*width,byl=by*width;
  unsigned int offset=0;

  for(int i=ax;i<bx;i++) {
    param->data[i+ayl] = 0;
    param->data[i+byl] = 0;
  }
  for(int i=ay;i<by;i++) {
    offset=i*WIDTH;
    param->data[offset+ax] = 0;
    param->data[offset+bx] = 0;
  }
}

/*****************************************************************************/
void fps_processing(void) 
{
  while(true) {
    std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    cout << fpsIn << " " << fpsProc << endl;
    fpsIn=0;
    fpsProc=0;
  }
}

/*****************************************************************************/
void stream_processing(void) 
{
  unsigned int dataSize = sizeof(unsigned char)*WIDTH*HEIGHT*SCALE;
  Mat dataOut(WIDTH,HEIGHT,CV_8UC3,Scalar(0,0,0));

  VideoCapture in(
    "shmsrc socket-path=" CAMINSTR
    " ! video/x-raw,width=" WIDTHSTR
    ",height=" HEIGHTSTR
    ",framerate=" FPSSTR
    "/1,format=I420 ! "
    "appsink sync=true",
    CAP_GSTREAMER);

  VideoWriter out(
    "appsrc ! "
    "shmsink socket-path=" CAMOUTSTR
    " wait-for-connection=false async=false sync=false",
    0,FPS/1,Size(WIDTH,HEIGHT),true);

  memset(&UdpOut, 0, sizeof(UdpOut));
//  to.sin_addr.s_addr = inet_addr("127.0.0.1");
  UdpOut.sin_addr.s_addr = INADDR_ANY;
  UdpOut.sin_family = AF_INET;
  UdpOut.sin_port = htons(4244);
  UdpOutSocket = socket(AF_INET, SOCK_DGRAM, 0);

  if (in.isOpened() && out.isOpened()) {
    while(true) {
      in.read(dataIn);
      if (!dataIn.empty()) {
        memcpy(dataOut.data, dataIn.data, dataSize);

        if(!ready) {
           ready=true;
           cond.notify_one();
	}

        if(readyDetect) y_overlay(&dataOut);
        out.write(dataOut);
        fpsIn++;
      }
    }
  }
  in.release();
  out.release();
}


/*****************************************************************************/
int main(int, char**)
{
  thread t0(fps_processing);
  thread t1(stream_processing);
  thread t2(image_processing);

  t0.join();
  t1.join();
  t2.join();

  return 0;
}
