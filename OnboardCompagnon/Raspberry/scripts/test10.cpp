#include <opencv2/opencv.hpp>
#include <iostream>
#include <mutex>
#include <thread>
#include <condition_variable>

#include <chrono>

using namespace cv;
using namespace std;

/*
g++ test10.cpp -o test10 `pkg-config --cflags --libs opencv` -D_GLIBCXX_USE_CXX11_ABI=0 -lpthread
*/

/*

gst-launch-1.0 rpicamsrc bitrate=1000000 vflip=true ! video/x-h264,width=640,height=480,framerate=15/1 ! h264parse config-interval=1 ! tee name=streams ! queue max-size-bytes=0 max-size-buffers=0 ! shmsink socket-path=/tmp/camera1 wait-for-connection=false sync=false streams. ! queue max-size-bytes=0 max-size-buffers=0 ! omxh264dec ! shmsink socket-path=/tmp/camera2 wait-for-connection=false sync=false

gst-gateworks-apps/bin/gst-variable-rtsp-server -p 8554 -m /test -u "( shmsrc socket-path=/tmp/camera1 do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay config-interval=1 name=pay0 pt=96 )"

or

gst-gateworks-apps/bin/gst-variable-rtsp-server -p 8554 -m /test -u "( shmsrc socket-path=/tmp/camera3 ! video/x-raw,format=BGR,width=640,height=480,framerate=15/1 ! queue ! videoconvert ! queue ! video/x-raw,format=I420 ! omxh264enc target-bitrate=1000000 control-rate=variable ! video/x-h264,profile=high ! h264parse ! rtph264pay config-interval=1 name=pay0 pt=96 )"


gst-launch-1.0 rtspsrc location=rtsp://192.168.43.73:8554/test ! rtph264depay ! avdec_h264 ! xvimagesink sync=false

*/

/*
gst-launch-1.0 rpicamsrc preview=0 fullscreen=0  ! video/x-raw,format=RGB,width=640,height=480,framerate=15/1 ! shmsink socket-path=/tmp/camera3 wait-for-connection=false

*/

unsigned int acquisition_cpt = 0;
unsigned int processing_cpt = 0;

Mat Frame(Size(640,480), CV_8UC3);
bool Ready = false;

string get_pipeline_in(void) 
{
  return ("shmsrc socket-path=/tmp/camera2 ! "
    "video/x-raw,width=640,height=480,framerate=15/1,format=RGB ! "
    "videoconvert ! "
    "appsink sync=false");
}


string get_pipeline_out(void) 
{
  return ("appsrc ! "
    "shmsink socket-path=/tmp/camera3 "
    "wait-for-connection=false async=false sync=false");
}


void data_acquisition(VideoCapture *cap,VideoWriter *snd,condition_variable *cond,mutex *mut)
{
  while (true) {
    *cap >> Frame;
    if (Frame.empty()) continue;
    {
      lock_guard<mutex> lk(*mut);
      Ready = true;
    }
    *snd << Frame;
    cond->notify_one();

    acquisition_cpt += 1;
    cout << "acquisition_ctp " << acquisition_cpt << endl;
  }
}


void data_processing(VideoWriter *snd, condition_variable *cond, mutex *mut)
{
  double scale=1;
  CascadeClassifier cascade("haarcascade_frontalcatface.xml");
  Mat img(Size(640,480), CV_8UC3);

  while (true) {

    unique_lock<mutex> lock(*mut);
    while(!Ready)cond->wait(lock);
    Frame.copyTo(img);
    Ready = false;
    lock.unlock();

    processing_cpt += 1;
    cout << "processing_ctp " << processing_cpt << endl;

    vector<Rect> faces;
    Mat gray;
    cvtColor( img, gray, COLOR_BGR2GRAY );

//    cascade.detectMultiScale( 
//      gray, faces, 1.1, 2, 0|CASCADE_SCALE_IMAGE, Size(30, 30) );
//
//    for ( size_t i = 0; i < faces.size(); i++ ) {
//      Rect r = faces[i];
//      Scalar color = Scalar(255, 0, 0);
//      rectangle( img,
//        Point(round(r.x*scale),round(r.y*scale)),
//	Point(round((r.x + r.width-1)*scale),round((r.y + r.height-1)*scale)),
//        color, 3, 8, 0);
//    }

//    snd->write(img);
  }
}


int main(int, char**)
{
  mutex mut;
  condition_variable cond;

  VideoCapture in(get_pipeline_in(),CAP_GSTREAMER);
  if (in.isOpened()) {
    VideoWriter out(get_pipeline_out(),0,15.0, Size(640,480),true);
    if (out.isOpened()) {
      thread t1(data_acquisition,&in,&out,&cond,&mut);
//      thread t2(data_processing,&out,&cond,&mut);
//      t2.join();
      t1.join();
    }
    in.release();
  }

  return 0;
}
