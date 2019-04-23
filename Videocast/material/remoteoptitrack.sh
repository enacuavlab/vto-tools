
-------------------------------------------------------------------------
using System.Diagnostics;
using System.ServiceProcess;

namespace DotNetService
{
	public class Service:ServiceBase
	{
		protected override void OnStart(string[] args)
		{
			Process.Start(@"C:\usr\bin\ffmpeg.exe", @"-f gdigrab -framerate 24 -offset_x 3840 -offset_y 0 
				-video_size 1920x1080 -i desktop -vcodec h264_nvenc -f mpegts udp://192.168.1.237:2202");
		}
	}
	
	static class Program { static void Main() { ServiceBase.Run(new ServiceBase[] { new Service() } ); }}
}

-------------------------------------------------------------------------
using System.Diagnostics;
  
namespace CProcessStart
{
    class Program
    {
        static void Main(string[] args)
        {
            ProcessStartInfo startInfo = new ProcessStartInfo(@"C:\Program Files (x86)\bin\fffmpeg.exe");
            startInfo.WindowStyle = ProcessWindowStyle.Normal;
        
            startInfo.Arguments = @"-f gdigrab -framerate 24 -offset_x 3840 -offset_y 0 -video_size 1920x1080 -i desktop -vcodec h264_nvenc -f mpegts udp://192.168.1.237:2202";
            Process.Start(startInfo);  
        }
    }
}

-------------------------------------------------------------------------
https://vnbskm.nl/2017/01/14/tutorial-building-a-windows-service-application/

-------------------------------------------------------------------------





sudo apt-get install samba-common

net rpc service list -I IPADDRESS -U USERNAME%PASSWORD

net rpc service stop SERVICENAME -I IPADDRESS -U USERNAME%PASSWORD

net rpc service start SERVICENAME -I IPADDRESS -U USERNAME%PASSWORD


-------------------------------------------------------------------------
C#.NET

using (System.Diagnostics.Process p = new System.Diagnostics.Process()) 
{
  p.StartInfo.RedirectStandardOutput = true;
  p.StartInfo.UseShellExecute = false;
  p.StartInfo.CreateNoWindow = true;

  p.StartInfo.FileName = @"C:\\usr\\bin\\ffmpeg.exe"
  p.StartInfo.Arguments = "-f gdigrab -framerate 24 -offset_x 3840 -offset_y 0 -video_size 1920x1080 -i desktop -vcodec h264_nvenc -f mpegts udp://192.168.1.237:2202";
  p.Start();
  p.WaitForExit();
}



-------------------------------------------------------------------------
Service1.cs class 

using System;  
using System.Collections.Generic;  
using System.ComponentModel;  
using System.Data;  
using System.Diagnostics;  
using System.IO;  
using System.Linq;
using System.ServiceProcess;  
using System.Text;  
using System.Threading.Tasks;  
using System.Timers;  

namespace MyFirstService {  

    public partial class Service1: ServiceBase {  

        Timer timer = new Timer(); // name space(using System.Timers;)  

        public Service1() {  

            InitializeComponent();  

        }  

        protected override void OnStart(string[] args) {  

            WriteToFile("Service is started at " + DateTime.Now);  

            timer.Elapsed += new ElapsedEventHandler(OnElapsedTime);  

            timer.Interval = 5000; //number in milisecinds  

            timer.Enabled = true;  

        }  

        protected override void OnStop() {  

            WriteToFile("Service is stopped at " + DateTime.Now);  

        }  

        private void OnElapsedTime(object source, ElapsedEventArgs e) {  

            WriteToFile("Service is recall at " + DateTime.Now);  

        }  

        public void WriteToFile(string Message) {  

            string path = AppDomain.CurrentDomain.BaseDirectory + "\\Logs";  

            if (!Directory.Exists(path)) {  

                Directory.CreateDirectory(path);  

            }  

            string filepath = AppDomain.CurrentDomain.BaseDirectory + "\\Logs\\ServiceLog_" + DateTime.Now.Date.ToShortDateString().Replace('/', '_') + ".txt";  

            if (!File.Exists(filepath)) {  

                // Create a file to write to.   

                using(StreamWriter sw = File.CreateText(filepath)) {  

                    sw.WriteLine(Message);  

                }  

            } else {  

                using(StreamWriter sw = File.AppendText(filepath)) {  

                    sw.WriteLine(Message);  

                }  
            }  
        }  
    }  
}