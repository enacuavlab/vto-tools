sudo raspi-config
=> enable camera


sudo apt-get install crtmpserver

-------------------------------------------------------------------------------
/etc/crtmpserver/enabled_applications.conf
=> 
appselector
flvplaybac

/etc/crtmpserver/applications/appselector.lua
=> 
application =
{
  name = "appselector",
  description = "Application for selecting the rest of the applications",
  protocol = "dynamiclinklibrary",
  validateHandshake = true,
  default = true,
  acceptors =
  {
    {
      ip = "0.0.0.0",
      port = 1935,
      protocol = "inboundRtmp"
    },
  }
}

-------------------------------------------------------------------------------
/etc/crtmpserver/applications/flvplayback.lua
=> 
application=
{
  description="FLV Playback Sample",
  name="flvplayback",
  protocol="dynamiclinklibrary",
  mediaFolder="/var/lib/crtmpserver/mediaFolder",
  aliases=
  {
    "live",
  },
  acceptors =
  {
    {
      ip="0.0.0.0",
      port=6666,
      protocol="inboundLiveFlv",
      waitForMetadata=true,
    },
    {
      ip="0.0.0.0",
      port=554,
      protocol="inboundRtsp"
    },
  },
  validateHandshake=false,
  keyframeSeek=false,
  seekGranularity=0.1, --in seconds, between 0.1 and 600
  clientSideBuffer=30, --in seconds, between 5 and 30
}

-------------------------------------------------------------------------------
sudo /etc/init.d/crtmpserver restart


raspivid -n -t 0 -w 1920 -h 1080 -fps 25 -b 2000000 -o - | ffmpeg -i - -vcodec copy -an -f flv -metadata streamName=livestream tcp://0.0.0.0:6666

-------------------------------------------------------------------------------
ffplay -fflags nobuffer -i rtsp://192.168.43.66/live/livestream




ffmpeg -f v4l2 -s hd720 -pix_fmt nv12 -i /dev/video0 -f alsa -i sysdefault:CARD=sunxicodec -pix_fmt nv12 -qp 20 -c:v cedrus264 -b:v 300k -r 30 -vewait 3600 -ar 44.1k -b:a 128k -c:a aac -strict -2 -f matroska - | ffmpeg -i - -c:a copy -c:v copy -f flv -metadata streamName=livestream tcp://0.0.0.0:6666
