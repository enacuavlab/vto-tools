using System.ServiceProcess;
using System.Diagnostics;
using murrayju.ProcessExtensions;

namespace castscreen_prj
{
    public partial class castscreen_srv : ServiceBase
    {
        System.Diagnostics.EventLog eventLog1;

        public castscreen_srv()
        {
            InitializeComponent();
            eventLog1 = new System.Diagnostics.EventLog();
            if (!System.Diagnostics.EventLog.SourceExists("MySource"))
            {
                System.Diagnostics.EventLog.CreateEventSource(
                    "MySource", "MyNewLog");
            }
            eventLog1.Source = "MySource";
            eventLog1.Log = "MyNewLog";
        }

        protected override void OnStart(string[] args)
        {
            eventLog1.WriteEntry("In OnStart.");
            ProcessExtensions.StartProcessAsCurrentUser(null, @"C:\Users\pprz\Projects\ffmpeg\bin\ffmpeg.exe -f gdigrab -r 15 -s 1920x1080 -offset_x 3840 -i desktop -c:v h264_nvenc -maxrate:v 200k -f rtp rtp://192.168.1.237:2202");

            //ProcessExtensions.StartProcessAsCurrentUser(null, @"C:\Users\pprz\Projects\ffmpeg\bin\ffmpeg.exe -f gdigrab -r 15 -s 1920x1080 -offset_x 3840 -i desktop -c:v h264_nvenc -maxrate:v 200k -f mpegts udp://192.168.1.237:2202");
        }

        protected override void OnStop()
        {
            eventLog1.WriteEntry("In OnStop.");

            foreach (var proc in Process.GetProcessesByName("ffmpeg"))
            {
                eventLog1.WriteEntry("KILL:"+proc.ProcessName);
                proc.Kill();
            }
        }


        public void StartService()
        {
            OnStart(null);
        }

        public void StopService()
        {
            OnStop();
        }
    }
}
