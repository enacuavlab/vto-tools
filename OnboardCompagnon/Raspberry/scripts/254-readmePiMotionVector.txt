raspivid patch and compile to raspicv
to run a thread to provide /tmp/camera3 with motion vector display
 
------------------------------------------------------------------------------------------------------
Adam Heinrich thesis
An Optical Flow Odometry Sensor Based
on the Raspberry Pi Computer


The VideoCore uses two hardware motion estimation blocks for video
encoding. A coarse motion estimation (CME) block estimates displacement
in pixel resolution and a subsequent fine motion estimation (FME) block is
able to estimate the displacement in a sub-pixel resolution

The motion estimation block uses a block matching method to estimate the displacement (∆u, ∆v). For each macroblock in the current frame, the closest match is found in the previous frame within a given range. Vectors from the CME block can be obtained directly from the encoder while vectors from the FME block are encoded in the final H.264 bitstream

For each P-frame, the encoder provides a buffer which contains a single 32-
bit value for each 16 × 16 px macroblock [Upt14, Hol14]. The most significant
16 bits represent a Sum of Absolute Differences (SAD) value. The SAD value
is a measure of the estimated motion’s quality: the lower the SAD, the better
match has been found. The other 16 bits represent motion in horizontal and
vertical directions (8-bit signed integer per direction)

The number of macroblocks provided by the CME is constant for each
frame

Moreover, the analysis shows that the CME, in fact, estimates motion in
two-pixel resolution (i.e. only even values are present).


a video_splitter component which has the ability to split video streams to multiple outputs. The video_splitter performs format conversion to grayscale so it is not necessary to configure the format at the camera’s output (the camera’s output format is optimized for the most efficient encoding)

both encoder_buffer_callback() and splitter_buffer_callback() contain a single line code which passes buffers to the main application for further processing.


Currently the cv.cpp is limited to 640x480 grayscale image. This can be easily modified (see function cv_init()).

------------------------------------------------------------------------------------------------------
cd
git clone https://github.com/raspberrypi/userland.git
git clone https://github.com/adamheinrich/RaspiCV.git

--------------
mv ~/RaspiCV/src/cv.cpp ~/RaspiCV/src/cv.cpp.old
get cv.cpp from Material/

-------------- 
cp ~/RaspiCV/src/Makefile ~/RaspiCV/src/Makefile.old
vi RaspiCV/src/Makefile
and PATCH
...
USERLAND_DIR = $(HOME)/userland
...
        $(USERLAND_DIR)/host_applications/linux/apps/raspicam/RaspiHelpers.c \
        $(USERLAND_DIR)/host_applications/linux/apps/raspicam/RaspiCommonSettings.c \
        $(USERLAND_DIR)/host_applications/linux/apps/raspicam/RaspiGPS.c \
        $(USERLAND_DIR)/host_applications/linux/apps/raspicam/libgps_loader.c
...
CXXFLAGS = $(ARCHFLAGS) $(DBGFLAGS) $(OPTFLAGS) `pkg-config --cflags opencv` \
CXXFLAGS = $(ARCHFLAGS) $(DBGFLAGS) $(OPTFLAGS) `pkg-config --cflags opencv4` \
...
LDFLAGS += `pkg-config --libs opencv`
LDFLAGS += `pkg-config --libs opencv4`
...
LDLIBFLAGS = -Wl,-
LDLIBFLAGS = -ldl -Wl,-

--------------
mv ~/RaspiCV/src/RaspiCV.c ~/RaspiCV/src/RaspiCV.c.old
cp ~/userland/host_applications/linux/apps/raspicam/RaspiVid.c ~/RaspiCV/src/RaspiCV.c
and PATCH
...
#include "cv.h"
#include <semaphore.h>
...
               if(pData->pstate->inlineMotionVectors)
               {
		  cv_process_imv(buffer->data, buffer->length, buffer->pts);
                  bytes_written = fwrite(buffer->data, 1, buffer->length, pData->imv_file_handle);
...
      if (bytes_to_write)
      {
         mmal_buffer_header_mem_lock(buffer);
	 cv_process_img(buffer->data, bytes_to_write, buffer->pts);
         bytes_written = fwrite(buffer->data, 1, bytes_to_write, pData->raw_file_handle);
...
	       cv_init(state.common_settings.width, state.common_settings.height, state.framerate, state.raw_output_fmt);
               int initialCapturing=state.bCapturing;
               while (running)
               {
...
      destroy_splitter_component(&state);
      destroy_camera_component(&state);

      cv_close();

--------------
cd ~/RaspiCV/src/
make

------------------------------------------------------------------------------------------------------
/home/pi/RaspiCV/build/raspicv -v -w 640 -h 480 -fps 30 -t 0 -o /dev/null -x /dev/null -r /dev/null -rf gray
