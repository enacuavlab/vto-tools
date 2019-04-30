Visual Studio 2019
------------------

Creer un projet
filter template C#
Service Windows (.NET Framework)
=> castscreen_prj

Explorateur de solution
selectionner Service1.cs + double click 
Propriétés: 
(Name) castscreen_srv 
ServiceName castscreen_srv 
Renommer Services1.cs en castscreen_srv.cs

Vue Design + Click droit
Ajouter le programme d'installation

Vue Design + Selectionner ServiceProcessInstaller1
Account = LocalSystem


-----------------------------------------------
Program.cs

        static void Main(String[] args)
        {
            if (args.Length == 0)
            {
                ServiceBase[] ServicesToRun;
                ServicesToRun = new ServiceBase[]
                { new castscreen_srv() };
                ServiceBase.Run(ServicesToRun);
            }
            else if (args[0].Equals("/console", StringComparison.OrdinalIgnoreCase))
            {
                using (castscreen_srv service = new castscreen_srv())
                {
                    service.StartService();
                    Thread.Sleep(10000);
                    service.StopService();
                }
            }
        }


-----------------------------------------------
castscreen.cs

        public void StartService()
        {
            OnStart(null);
        }

        public void StopService()
        {
            OnStop();
        }


-----------------------------------------------
services.msc

c:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe /u c:\Users\pprz\Projects\castscreen_prj\bin\Release\castscreen_prj.exe

c:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe c:\Users\pprz\Projects\castscreen_prj\bin\Release\castscreen_prj.exe

sc query castscreen_srv
sc start castscreen_srv
sc query castscreen_srv
sc stop castscreen_srv
sc query castscreen_srv


-----------------------------------------------
Download ProcessExtensions

castscreen_srv.cs
OnStart()
add
//ProcessExtensions.StartProcessAsCurrentUser(null, @"C:\Users\pprz\Projects\ffmpeg\bin\ffmpeg.exe -f gdigrab -s 1920x1080 -r 25 -offset_x 3840 -i desktop -r 25 -g 50 -c:v h264_nvenc -pix_fmt yuv420p -preset fast -profile:v main -b:v 16000k -maxrate 2400k -bufsize 6000k -f mpegts udp://192.168.1.237:35000");

            ProcessExtensions.StartProcessAsCurrentUser(null, @"C:\Users\pprz\Projects\ffmpeg\bin\ffmpeg.exe -f gdigrab -s 1920x1080 -r 25 -offset_x 3840 -i desktop -r 25 -g 50 -c:v h264_nvenc -pix_fmt yuv420p -preset fast -profile:v main -b:v 16000k -maxrate 2400k -bufsize 6000k -f rtp rtp://192.168.1.237:35000");
            //ProcessExtensions.StartProcessAsCurrentUser(null, @"C:\Users\pprz\Projects\ffmpeg\bin\ffmpeg.exe -f gdigrab -r 25 -s 1920x1080 -offset_x 3840 -i desktop -c:v h264_nvenc -g 1 -f rtp rtp://192.168.1.237:35000");
            //ProcessExtensions.StartProcessAsCurrentUser(null, @"C:\Users\pprz\Projects\ffmpeg\bin\ffmpeg.exe -f gdigrab -r 15 -s 1920x1080 -offset_x 3840 -i desktop -c:v h264_nvenc -tune zerolatency -maxrate:v 200k -f rtp rtp://192.168.1.237:35000");

ProcessExtensions.StartProcessAsCurrentUser(null, @"C:\Users\pprz\Projects\ffmpeg\bin\ffmpeg.exe -f gdigrab -r 15 -s 1920x1080 -offset_x 3840 -i desktop -c:v h264_nvenc -maxrate:v 200k -f mpegts udp://192.168.1.237:2202");


-----------------------------------------------
From linux

net rpc service list -I optitrack -U pprz%pprz | grep cast

net rpc service start castscreen_srv -I optitrack -U pprz%pprz

net rpc service stop castscreen_srv -I optitrack -U pprz%pprz

