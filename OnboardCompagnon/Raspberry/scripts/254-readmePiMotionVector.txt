


cd
git clone https://github.com/raspberrypi/userland.git
git clone https://github.com/adamheinrich/RaspiCV.git
 
vi RaspiCV/src/Makefile
USERLAND_DIR = $(HOME)/userland
....
        $(USERLAND_DIR)/host_applications/linux/apps/raspicam/RaspiHelpers.c \
        $(USERLAND_DIR)/host_applications/linux/apps/raspicam/RaspiCommonSettings.c \
        $(USERLAND_DIR)/host_applications/linux/apps/raspicam/RaspiGPS.c \
        $(USERLAND_DIR)/host_applications/linux/apps/raspicam/libgps_loader.c
...
LDLIBFLAGS = -Wl,-
LDLIBFLAGS = -ldl -Wl,-


cp ./userland/host_applications/linux/apps/raspicam/RaspiVid.c ~/RaspiCV/src/RaspiCV.c

-----------------
PATCH
-----------------
#include "RaspiCLI.h"

#include "cv.h"

#include <semaphore.h>
#
-----------------
               if(pData->pstate->inlineMotionVectors)
               {
		  cv_process_imv(buffer->data, buffer->length, buffer->pts);
                  bytes_written = fwrite(buffer->data, 1, buffer->length, pData->imv_file_handle);

-----------------
      if (bytes_to_write)
      {
         mmal_buffer_header_mem_lock(buffer);
	 cv_process_img(buffer->data, bytes_to_write, buffer->pts);
         bytes_written = fwrite(buffer->data, 1, bytes_to_write, pData->raw_file_handle);

-----------------
	       cv_init(state.common_settings.width, state.common_settings.height, state.framerate, state.raw_output_fmt);
               int initialCapturing=state.bCapturing;
               while (running)
               {

-----------------
      destroy_splitter_component(&state);
      destroy_camera_component(&state);

      cv_close();


-----------------
-----------------

raspicv -v -w 640 -h 480 -fps 30 -t 0 -o /dev/null -x /dev/null -r /dev/null -rf gray

raspicv -v -w 640 -h 480 -fps 30 -t 0 -o /dev/null -x /dev/null -r /dev/null -rf gray
