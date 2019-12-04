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
////#include <arpa/inet.h> 
#include <netinet/in.h> 


/*
g++ -g test6.cpp -o test6 `pkg-config --cflags --libs opencv` -D_GLIBCXX_USE_CXX11_ABI=0 -lpthread 
or
g++ -g groundpicv.cpp -o groundpicv -I/usr/local/include/opencv4 -lopencv_core -lopencv_objdetect -lopencv_videoio -lopencv_imgproc -lpthread
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

struct sockaddr_in UdpIn;
int UdpInSocket;

Rect detect;
unsigned int fpsIn = 0;
unsigned int fpsProc = 0;

/*****************************************************************************/
void image_processing(void)
{
//  double scale=1;
//  CascadeClassifier cascade("/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml");
//  vector<Rect> faces;
//  Mat gray;
//  Mat img1(HEIGHT,WIDTH,CV_8UC3,Scalar(0,0,0));

  char buff[50];
  socklen_t addrlen = sizeof(UdpIn);
  int len;

  while (true) {

//    std::unique_lock<std::mutex> lck(mtx);
//    cond.wait(lck, []{return ready;});
//
//    cvtColor(dataIn,img1,COLOR_YUV2BGR_I420);
//    cvtColor(img1,gray,COLOR_BGR2GRAY);
//
//    cascade.detectMultiScale(gray, faces, 2.0, 1, 0|CASCADE_SCALE_IMAGE, Size(80, 80) );
//    if(faces.size()>0) {
//      detect = faces[0];
//      readyDetect = true;
//    } else {
//      readyDetect = false;
//    }


    len = recvfrom(UdpInSocket, buff, sizeof(buff), 0, (sockaddr *) &UdpIn, &addrlen);
    if(len > 0) {
      buff[len+1]='\n';
      sscanf(buff, "%d,%d,%d,%d",&detect.x,&detect.y,&detect.height,&detect.width);
      readyDetect =true;
    }
		  
    fpsProc++;

//    ready = false;
  }
}

/*****************************************************************************/
void overlay(Mat *param)
{
  unsigned int ax=detect.x,bx=ax+detect.width;
  unsigned int ay=detect.y,by=ay+detect.height;

  // YUV420P 

  // Y
  unsigned int ayl_y=ay*WIDTH,byl_y=by*WIDTH;
  for(int i=ax;i<bx;i++) {
    param->data[i+ayl_y] = 0;
    param->data[i+byl_y] = 0;
  }
  unsigned int offset_y=0;
  for(int i=ay;i<by;i++) {
    offset_y=i*WIDTH;
    param->data[offset_y+ax] = 0;
    param->data[offset_y+bx] = 0;
  }

  // U & V
  unsigned int ayl_u = int(rint(ay*0.5))*int(rint(WIDTH*0.5))+(WIDTH*HEIGHT);
  unsigned int ayl_v = ayl_u + int(rint(WIDTH*HEIGHT*0.25));
  unsigned int byl_u = int(rint(by*0.5))*int(rint(WIDTH*0.5))+(WIDTH*HEIGHT);
  unsigned int byl_v = byl_u + int(rint(WIDTH*HEIGHT*0.25));
  for(int i=(ax*0.5);i<(bx*0.5);i++) {
    param->data[i+ayl_u] = 0;
    param->data[i+ayl_v] = 0;
    param->data[i+byl_u] = 0;
    param->data[i+byl_v] = 0;
  }
  unsigned int offset_u=0;
  unsigned int offset_v=0;
  for(int i=(ay*0.5);i<(by*0.5);i++) {
    offset_u = int(rint(i*WIDTH*0.5))+(WIDTH*HEIGHT);
    param->data[offset_u+int(rint(ax*0.5))] = 0;
    param->data[offset_u+int(rint(bx*0.5))] = 0;
    offset_v = offset_u + int(rint(WIDTH*HEIGHT*0.25));
    param->data[offset_v+int(rint(ax*0.5))] = 0;
    param->data[offset_v+int(rint(bx*0.5))] = 0;
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
  struct sockaddr_in myaddr;

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

  UdpInSocket = socket(AF_INET, SOCK_DGRAM, 0);
  memset((char *)&myaddr, 0, sizeof(myaddr));
  myaddr.sin_family = AF_INET;
  myaddr.sin_addr.s_addr = htonl(INADDR_ANY);
  myaddr.sin_port = htons(4244);
  bind(UdpInSocket, (struct sockaddr *)&myaddr, sizeof(myaddr));

  if (in.isOpened() && out.isOpened()) {
    while(true) {
      in.read(dataIn);
      if (!dataIn.empty()) {
        memcpy(dataOut.data, dataIn.data, dataSize);

//        if(!ready) {
//           ready=true;
//           cond.notify_one();
//	}

        if(readyDetect) overlay(&dataOut);
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
