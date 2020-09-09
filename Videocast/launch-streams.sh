ffmpeg -f x11grab -s 1920x1080 -framerate 25 -i :0.0+0,0 -r 25 -g 50 -c:v h264_nvenc -pix_fmt yuv420p -preset fast -profile:v main -b:v 2000K -maxrate 24000k -bufsize 6000k -f rtp rtp://192.168.1.237:35010

