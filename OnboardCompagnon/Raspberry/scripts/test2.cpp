#include <opencv2/opencv.hpp>
#include <iostream>
#include <mutex>
#include <thread>
#include <condition_variable>

#include <chrono>

using namespace cv;
using namespace std;

/*
G_DEBUG=3 gst-launch-1.0 -vvvv rpicamsrc bitrate=1000000 vflip=true ! video/x-h264,width=640,height=480,framerate=15/1 ! h264parse ! tee name=streams ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! omxh264dec ! shmsink wait-for-connection=1 socket-path=/tmp/camera2 streams. ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! shmsink wait-for-connection=1 socket-path=/tmp/camera1

G_DEBUG=3 gst-launch-1.0 -vvvv shmsrc socket-path=/tmp/camera1 ! video/x-h264,width=640,height=480,framerate=15/1,stream-format=byte-stream,alignment=au ! h264parse ! rtph264pay config-interval=1  pt=96 ! udpsink host=192.168.43.181 port=5000 sync=false
or
G_DEBUG=3 gst-launch-1.0 -vvvv shmsrc socket-path=/tmp/camera2 ! video/x-raw,format=I420,width=640,height=480,framerate=15/1 ! videoconvert ! omxh264enc ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.43.181 port=5000 sync=false


gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false
*/



string get_pipeline_in(void) 
{
  return ("shmsrc socket-path=/tmp/camera2 ! "
    "video/x-raw,width=640,height=480,framerate=15/1,format=I420 ! "
    "appsink sync=true");
}


string get_pipeline_out(void) 
{
  return("appsrc ! "
    "video/x-raw,width=640,height=480,framerate=15/1,format=BGR ! "
    "videoconvert ! "
    "video/x-raw,format=I420 ! "
    "omxh264enc ! "
    "rtph264pay config-interval=1 pt=96 ! "
    "udpsink host=192.168.43.181 port=5000");
}


struct shared_struct
{
  mutex mut;
  condition_variable cond;
  bool ready;
  Mat frame;
};


void data_acquisition(VideoCapture *in, shared_struct *param)
{
  unsigned int acquisition_cpt = 0;
  while (true) {
    in->read(param->frame);
    if (!param->frame.empty()) { 
      unique_lock<mutex> lock(param->mut);
      param->ready = true;
      acquisition_cpt += 1;
      cout << "acquisition_ctp " << acquisition_cpt << endl;
      param->cond.notify_one();
    }
  }
}


void data_processing(VideoWriter *out, shared_struct *param)
{
  unsigned int processing_cpt = 0;
  Mat img0,img1,img2;

  unique_lock<mutex> lock(param->mut);
  while (true) {
    while(!param->ready) param->cond.wait(lock);
    param->frame.copyTo(img0);
    cvtColor(img0,img1,COLOR_YUV2BGR_I420); 
    cvtColor(img1,img2,COLOR_BGR2YUV_I420); 
    out->write(img1);
    processing_cpt += 1;
    cout << "processing_ctp " << processing_cpt << endl;
    param->ready = false;
  }
}


int main(int, char**)
{
  shared_struct param;
  param.ready = false;

  VideoCapture in(get_pipeline_in(),CAP_GSTREAMER);
  if (in.isOpened()) {
    VideoWriter out(get_pipeline_out(),0,15.0,Size(640,480),true);
    if (out.isOpened()) {
      thread t1(data_acquisition,&in,&param);
      thread t2(data_processing,&out,&param);
      t1.join();
      t2.join();

      out.release();
    }
    in.release();
  }

  return 0;
}
