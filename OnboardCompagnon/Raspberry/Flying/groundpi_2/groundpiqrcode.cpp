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

std::array<cv::Point,4> points;
std::string data;
//Rect detect;
unsigned int fpsIn = 0;
unsigned int fpsProc = 0;

cv::Mat overlays[5];

/*****************************************************************************/
void image_processing(void)
{
//  double scale=1;
//  CascadeClassifier cascade("/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml");
//  vector<Rect> faces;
//  Mat gray;
//  Mat img1(HEIGHT,WIDTH,CV_8UC3,Scalar(0,0,0));

  char buff[128];
  socklen_t addrlen = sizeof(UdpIn);
  int len;

  /**************************************************************/
/*
  FILE* f = fopen("/home/pi/opencv_trials/cpp/licorne.bmp", "rb");
  unsigned char info[54];
  fread(info, sizeof(unsigned char), 54, f);

  int w = *(int*)&info[18];
  int h = *(int*)&info[22];
  int s = w * h;
  std::cout << "w " << w << " h:" << h << " s:" << std::endl;

  unsigned char* dt = new unsigned char[s]; 
  fread(dt, sizeof(unsigned char), s, f);
  fclose(f);

  for(int i = 0; i < s; i ++)
  {
    unsigned char tmp = dt[i];
    dt[i] = dt[i+2];
    dt[i+2] = tmp;
  }
*/


  /**************************************************************/
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
      buff[len+1]='\0';
      char c;
      std::stringstream sstr(buff);
      sstr >> points[0].x >> c >> points[0].y ;
      sstr >> points[1].x >> c >> points[1].y ;
      sstr >> points[2].x >> c >> points[2].y ;
      sstr >> points[3].x >> c >> points[3].y ;
      std::getline(sstr,data);
      //sscanf(buff, "%d,%d %d,%d %d,%d %d,%d \"%s\"",);
      //std::cout << "Got " << buff << std::endl;
      readyDetect =true;
    }
		  
    fpsProc++;

//    ready = false;
  }
}

/*****************************************************************************/
void overlay(Mat *param)
{
  int min_x=points[0].x;
  int min_y=points[0].y;
  int max_x=points[0].x;
  int max_y=points[0].y;
  for (int j = 1; j < 4; j++)
  {
	if (min_x>points[j].x)
		min_x=points[j].x;
	if (min_y>points[j].y)
		min_y=points[j].y;
	if (max_x<points[j].x)
		max_x=points[j].x;
	if (max_y<points[j].y)
		max_y=points[j].y;
  }
  unsigned int ax=min_x,bx=max_x;
  unsigned int ay=min_y,by=max_y;
  unsigned int width=bx-ax;
  unsigned int height=by-ay;

  // TODO Choose the image to overlay 
  cv::Mat imgOverlay = overlays[0];
  
  // YUV420P 
 
  unsigned int iow = imgOverlay.size().width;
  unsigned int ioh = imgOverlay.size().height;
  float factor_x = width/(float)iow;
  float factor_y = height/(float)ioh;
  float factor = MIN(1,MIN(factor_x,factor_y)); 
  
  // Y , U & V
  const static unsigned int offset_u = (WIDTH*HEIGHT);
  const static unsigned int offset_v = offset_u+ ((int)rint(WIDTH*0.5)*(int)rint(HEIGHT*0.5));
  max_x = MIN(WIDTH,bx);
  max_y = MIN(HEIGHT,by);
  for(int i=0;i<width;i++) {
    for(int j=0;j<height;j++) {
	  int x = ax + i*factor;
	  int y = ay + j*factor;
	  if (x<max_x && y <max_y) {  
	    // Y
            param->data[x+y*WIDTH] = imgOverlay.at<unsigned char>(i,j);
	    // U
            param->data[x+y*(int)rint(WIDTH*0.5)+offset_u] = 128;
	    // V
            param->data[x+y*(int)rint(WIDTH*0.5)+offset_v] = 128;
	  }
    }
  }

  /*
  static Mat img(HEIGHT,WIDTH,CV_8UC3,Scalar(0,0,0));

  //cvtColor(dataIn,img,COLOR_YUV2BGR_I420);

  std::cout << data << " : ";
  cv::Point mid(0, 0);
  for (int j = 0; j < 4; j++)
  {
       mid += points[j];
       std::cout << "(" << points[j].x << "," << points[j].y << ")";
       cv::line(dataIn, points[j], points[(j + 1) % 4], cv::Scalar(0, 255, 0), 3);
   }
   std::cout << std::endl;
   mid /= 4;

  cv::putText(dataIn, data, mid, cv::FONT_HERSHEY_PLAIN, 2.0, cv::Scalar(0, 255, 0), 4);

  //cvtColor(img,dataIn,COLOR_BGR2YUV_I420);

  const static unsigned int dataSize = sizeof(unsigned char)*WIDTH*HEIGHT*SCALE;
  memcpy(param->data, dataIn.data, dataSize);
  */

  readyDetect=false;
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

//        if(!ready) {
//           ready=true;
//           cond.notify_one();
//	}
//
	memcpy(dataOut.data, dataIn.data, dataSize);
        if(readyDetect) 
		overlay(&dataOut);

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
  // TODO add other images to overlay
  overlays[0]=imread("/home/pi/opencv_trials/cpp/licorne.bmp",cv::IMREAD_GRAYSCALE);

  thread t0(fps_processing);
  thread t1(stream_processing);
  thread t2(image_processing);

  t0.join();
  t1.join();
  t2.join();

  return 0;
}
