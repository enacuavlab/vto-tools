#include <opencv2/opencv.hpp>
#include <iostream>
#include <mutex>
#include <thread>
#include <condition_variable>

#include <chrono>

/*
g++ -g test6.cpp -o test6 `pkg-config --cflags --libs opencv` -D_GLIBCXX_USE_CXX11_ABI=0 -lpthread 
*/

using namespace cv;
using namespace std;

/*****************************************************************************/
std::mutex mtx;
std::condition_variable cond;
Mat frameIn = Mat(720,640,CV_8UC1); 
bool ready = false;
bool readyDetect = false;

Rect detect;

/*****************************************************************************/
void image_processing(void)
{
  double scale=1;
  CascadeClassifier cascade("/opt/opencv-4.1.0/share/opencv4/haarcascades/haarcascade_frontalcatface.xml");
  vector<Rect> faces;
  Mat gray;
  Mat img1(480,640,CV_8UC3,Scalar(0,0,0));

  while (true) {
    std::unique_lock<std::mutex> lck(mtx);
    cond.wait(lck, []{return ready;});

    cvtColor(frameIn,img1,COLOR_YUV2BGR_I420);
    cvtColor(img1,gray,COLOR_BGR2GRAY);
    imwrite("img.jpg",gray);

    cascade.detectMultiScale(gray, faces, 1.1, 2, 0|CASCADE_SCALE_IMAGE, Size(30, 30) );
    cout << "faces.size() " << faces.size() << endl;

    if(faces.size()==1) {
      detect = faces[0];
      readyDetect = true;
    }

    ready = false;
    lck.unlock();
  }
}

/*****************************************************************************/
unsigned int width=640,height=480;
//unsigned int ax=220,bx=320;
//unsigned int ay=210,by=300;
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
    offset=i*640;
    param->data[offset+ax] = 0;
    param->data[offset+bx] = 0;
  }
}

/*****************************************************************************/
void stream_processing(void) 
{
  unsigned int cpt = 0;

  Mat dataIn(480*3/2,640,CV_8UC1);
  Mat dataOut(480,640,CV_8UC3,Scalar(0,0,0));

  VideoCapture in(
    "shmsrc socket-path=/tmp/camera2 ! "
    "video/x-raw,width=640,height=480,framerate=15/1,format=I420 ! "
    "appsink sync=true",
    CAP_GSTREAMER);

  VideoWriter out(
    "appsrc ! "
    "shmsink socket-path=/tmp/camera3 "
    "wait-for-connection=false async=false sync=false",
    0,15.0,Size(640,480),true);

  if (in.isOpened() && out.isOpened()) {
    while(true) {
      in.read(dataIn);
      if (!dataIn.empty()) { 

        if(!ready) {
          std::unique_lock<std::mutex> lck(mtx);
          memcpy(frameIn.data, dataIn.data, sizeof(unsigned char)*640*480*3/2);  
          ready=true;
          lck.unlock();
          cond.notify_one();
	}

        memcpy(dataOut.data, dataIn.data, sizeof(unsigned char)*640*480*3/2);  
        if(readyDetect) y_overlay(&dataOut);
        out.write(dataOut);

        cpt += 1;
        cout << "processing " << cpt << endl;

      }
    }
  }
  in.release();
  out.release();
}


/*****************************************************************************/
int main(int, char**)
{
  thread t1(stream_processing);
  thread t2(image_processing);
  t1.join();
  t2.join();

  return 0;
}
