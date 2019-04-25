Axis P1448-LE Camera

StreamProfile
VTO_Cast
resolution=1920x1080&videocodec=h264&h264profile=baseline
resolution=640x480&videocodec=h264&h264profile=baseline

#resolution=1920x1080&compression=30&mirror=0&fps=0&audio=0&h264profile=high&videobitrate=0&videocodec=h264

--------------------------------------------------------------------------------
http://192.168.1.232/axis-cgi/param.cgi?action=list&group=Properties.API.HTTP.Version
=> Properties.API.HTTP.Version=3

http://192.168.1.232/axis-cgi/param.cgi?action=list&group=Properties.Image.Resolution
=> Properties.Image.Resolution=3840x2160,3072x1728,2720x1536,2592x1944,2560x1920,2560x1600,2560x1440,2432x1824,2304x1728,2048x1536,1920x1200,1920x1080,1440x900,1280x800,1280x720,1024x768,1024x640,800x600,800x500,800x450,640x480,640x400,640x360,480x360,480x300,480x270,320x240,320x200,320x180,240x180,176x144,160x120,160x100,160x90

http://192.168.1.232/axis-cgi/param.cgi?action=list&group=Properties.Image.Format
=> Properties.Image.Format=jpeg,mjpeg,h264,bitmap

http://192.168.1.232/axis-cgi/param.cgi?action=list&group=StreamProfile.S0
=>
root.StreamProfile.S0.Description=
root.StreamProfile.S0.Name=VTO-Cast
root.StreamProfile.S0.Parameters=resolution=640x480&videocodec=h264&h264profile=baseline


---------------------
http://192.168.1.232/axis-cgi/imagesize.cgi?camera=1
=> 
image width = 1920
image height = 1080

---------------------
http://192.168.1.232/axis-cgi/imagesize.cgi?resolution=QCIF&rotation=180&squarepixel=1&camera=1
=>
image width = 176
image height = 144

http://192.168.1.232/axis-cgi/jpg/image.cgi?resolution=320x240&compression=25&camera=1
=> 

---------------------
http://192.168.1.232/axis-cgi/mjpg/video.cgi?streamprofile=toto
=>

http://192.168.1.232/axis-cgi/mjpg/video.cgi?resolution=320x240&compression=25&camera=1
=>

---------------------
ffprobe rtsp://pprz:vtoenac@192.168.1.232/axis-media/media.amp
=>
Stream #0:0: Video: h264 (Baseline), yuvj420p(pc, bt709, progressive), 1920x1080 [SAR 1:1 DAR 16:9], 25 fps, 25 tbr, 90k tbn, 180k tbc

ffprobe rtsp://pprz:vtoenac@192.168.1.232/axis-media/media.amp?videocodec=h264&resolution=640x480
=> ?

ffprobe rtsp://pprz:vtoenac@192.168.1.232/axis-media/media.amp/trackID=1?videocodec=h264&resolution=640x480
=> ?

ffprobe rtsp://pprz:vtoenac@192.168.1.232/axis-media/media.amp?streamprofile="VTO-Cast"
=> 
Stream #0:0: Video: h264 (Baseline), yuvj420p(pc, bt709, progressive), 640x480 [SAR 1:1 DAR 4:3], 25 fps, 25 tbr, 90k tbn, 180k tbc

ffprobe rtsp://pprz:vtoenac@192.168.1.232/axis-media/media.amp?resolution=1920x1080&videocodec=h264&h264profile=baseline
=>
Stream #0:0: Video: h264 (Baseline), yuvj420p(pc, bt709, progressive), 1920x1080 [SAR 1:1 DAR 4:3], 25 fps, 25 tbr, 90k tbn, 180k tbc

 
---------------------
ffprobe rtsp://pprz:vtoenac@192.168.1.232/axis-media/media.amp?resolution=1920x1080
=>
Stream #0:0: Video: h264 (Baseline), yuvj420p(pc, bt709, progressive), 1920x1080 [SAR 1:1 DAR 16:9], 25 fps, 25 tbr, 90k tbn, 180k tbc

ffplay -fflags nobuffer rtsp://pprz:vtoenac@192.168.1.232/axis-media/media.amp?resolution=1920x1080
