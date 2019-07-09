#include <opencv2/opencv.hpp>
#include <iostream>
#include <mutex>
#include <thread>
#include <condition_variable>

#include <chrono>

using namespace cv;
using namespace std;

/*
rm /tmp/camera*
 
GST_DEBUG=3 gst-launch-1.0 -vvvv rpicamsrc bitrate=1000000 vflip=true ! video/x-h264,width=640,height=480,framerate=15/1 ! h264parse ! tee name=streams ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! omxh264dec ! shmsink wait-for-connection=1 socket-path=/tmp/camera2 streams. ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! shmsink wait-for-connection=1 socket-path=/tmp/camera1

GST_DEBUG=3 gst-launch-1.0 -vvvv shmsrc socket-path=/tmp/camera1 ! video/x-h264,width=640,height=480,framerate=15/1,stream-format=byte-stream,alignment=au ! h264parse ! rtph264pay config-interval=1  pt=96 ! udpsink host=192.168.43.181 port=5000 sync=false
or
GST_DEBUG=3 gst-launch-1.0 -vvvv shmsrc socket-path=/tmp/camera2 ! video/x-raw,format=I420,width=640,height=480,framerate=15/1 ! (videoconvert) ! omxh264enc ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.43.181 port=5000 sync=false

GST_DEBUG=3 gst-launch-1.0 -vvvv shmsrc socket-path=/tmp/camera3 ! video/x-raw,format=I420,width=640,height=480,framerate=15/1 ! omxh264enc target-bitrate=1000000 control-rate=variable ! video/x-h264,profile=high ! h264parse ! rtph264pay config-interval=1 name=pay0 pt=96 ! udpsink host=192.168.43.181 port=5000

gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false
*/


int main(int, char**)
{
  unsigned int cpt = 0;
  Mat frame,img0,img1,img2;

  VideoCapture in(
    "shmsrc socket-path=/tmp/camera2 ! "
    "video/x-raw,width=640,height=480,framerate=15/1,format=I420 ! "
    "appsink sync=true",
    CAP_GSTREAMER);

  VideoWriter out(
    "appsrc ! "
    "shmsink socket-path=/tmp/camera3 "
    "wait-for-connection=false async=false sync=false",
    CAP_GSTREAMER,0,15.0,Size(640,480),true);

  if (in.isOpened() && out.isOpened()) {
    while(true) {
      in.read(frame);
      if (!frame.empty()) { 
        frame.copyTo(img0);

        // Cam -> CSI-2 -> H264 Raw (YUV 4-4-4 (12bits) I420)
        // convert YUV nibbles (4-4-4) to OpenCV standard BGR bytes (8-8-8)
        cvtColor(img0,img1,COLOR_YUV2BGR_I420);  
	imwrite("img.jpg",img2);
//        cvtColor(img0,img2,COLOR_YUV2BGR);  

        out.write(img1);
        cpt += 1;
        cout << "processing " << cpt << endl;
      }
    }
  }

  return 0;
}
