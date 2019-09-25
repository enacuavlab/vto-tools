#include <opencv2/opencv.hpp>
#include <iostream>
#include <mutex>
#include <thread>
#include <condition_variable>

using namespace cv;
using namespace std;

/*
g++ test10.cpp -o test10 `pkg-config --cflags --libs opencv` -D_GLIBCXX_USE_CXX11_ABI=0 -lpthread
*/

/*

gst-launch-1.0 rpicamsrc bitrate=1000000 vflip=true ! video/x-h264,width=640,height=480,framerate=15/1 ! h264parse config-interval=1 ! tee name=streams ! queue ! shmsink socket-path=/tmp/camera1 wait-for-connection=false sync=false streams. ! queue ! omxh264dec ! shmsink socket-path=/tmp/camera2 wait-for-connection=false sync=false

~/gst-rtsp-server-1.10.4/examples/test-launch "( shmsrc socket-path=/tmp/camera1 do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay config-interval=1 name=pay0 pt=96 )"

gst-launch-1.0 rtspsrc location=rtsp://192.168.1.80:8554/test ! rtph264depay ! avdec_h264 ! xvimagesink sync=false

*/

unsigned int acquisition_cpt = 0;
unsigned int processing_cpt = 0;
Mat globalframe(Size(640,480), CV_8UC3);


string get_pipeline_in(void) 
{
  return ("shmsrc socket-path=/tmp/camera2 ! "
    "video/x-raw,width=640,height=480,framerate=15/1,format=RGB ! "
    "videoconvert ! "
    "appsink sync=false");
}


string get_pipeline_out(void) 
{
  return ("appsrc ! queue ! "
    "shmsink socket-path=/tmp/camera3 "
    "wait-for-connection=false async=false sync=false");
}


void data_acquisition(VideoCapture *cap,condition_variable *cond,mutex *mut, bool *ready)
{
  Mat frame(Size(640,480), CV_8UC3);
  while (cap->read(frame)) {
    if (!frame.empty()) {
      unique_lock<mutex> lock(*mut);
      globalframe = frame.clone();
//      acquisition_cpt += 1;
//      cout << "acquisition_ctp " << acquisition_cpt << endl;
      *ready=true;
      cond->notify_one();
    }
  }
}


void data_processing(VideoWriter *snd, condition_variable *condition, mutex *mut, bool ready)
{
  double scale=1;
  CascadeClassifier cascade("haarcascade_frontalcatface.xml");

  while (true) {
    unique_lock<mutex> lock(*mut);
    while(!ready) condition->wait(lock);
//    processing_cpt += 1;
//    cout << "processing_ctp " << processing_cpt << endl;
    Mat img = globalframe.clone();

    vector<Rect> faces;
    Mat gray;
    cvtColor( img, gray, COLOR_BGR2GRAY );

    cascade.detectMultiScale( 
      gray, faces, 1.1, 2, 0|CASCADE_SCALE_IMAGE, Size(30, 30) );

    for ( size_t i = 0; i < faces.size(); i++ ) {
      Rect r = faces[i];
      Scalar color = Scalar(255, 0, 0);
      rectangle( img,
        Point(round(r.x*scale),round(r.y*scale)),
	Point(round((r.x + r.width-1)*scale),round((r.y + r.height-1)*scale)),
        color, 3, 8, 0);
    }

    snd->write(img);
    processing_cpt += 1;
    cout << "processing_ctp " << processing_cpt << endl;
  }
}


int main(int, char**)
{
  bool ready=false;
  mutex mut;
  condition_variable cond;

  VideoCapture in(get_pipeline_in(),CAP_GSTREAMER);
  if (in.isOpened()) {
    VideoWriter out(get_pipeline_out(),0,15.0, Size(640,480),true);
    if (out.isOpened()) {
      thread t1(data_acquisition,&in,&cond,&mut,&ready);
      thread t2(data_processing,&out,&cond,&mut,ready);
      t2.join();
      t1.join();
    }
    in.release();
  }

  return 0;
}
