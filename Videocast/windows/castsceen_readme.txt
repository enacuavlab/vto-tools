Install gstreamer
https://gstreamer.freedesktop.org/download/
MinGW 64-bit

c:/gstreamer


-----------------------------------------------
https://github.com/murrayju/CreateProcessAsUser
Download ZIP
Copy folder ProcessExtensions to Users\pprz\Projects


-----------------------------------------------
Install Visual Studio 2019

Creer un nouveau projet
filtrer le template C# Windows Service
Service Windows (.NET Framework)
=> castscreen_prj
Users\pprz\Projects

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

Save All

-----------------------------------------------
Update files

Program.cs
----------

using System;
using System.ServiceProcess;
using System.Threading;

namespace castscreen_prj
{
    static class Program
    {
        /// <summary>
        /// Point d'entrée principal de l'application.
        /// </summary>
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
    }
}


castscreen_srv.cs
-----------------

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

            ProcessExtensions.StartProcessAsCurrentUser(null, @"C:\gstreamer\1.0\mingw_x86\bin\gst-launch-1.0.exe -v dx9screencapsrc monitor=1 ! video/x-raw,framerate=25/1 ! queue ! videoconvert ! x264enc ! ""video/x-h264,profile=baseline"" ! h264parse config-interval=-1 ! rtph264pay pt=96 config-interval=-1 ! udpsink host=192.168.1.237 port=35000 sync=true");
        }

        protected override void OnStop()
        {
            eventLog1.WriteEntry("In OnStop.");

            foreach (var proc in Process.GetProcessesByName("gst-launch-1.0"))
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

-----------------------------------------------
Re-Open visual Studio

Properties + right click (add Existing Items pprz\Project\ProcessExtension`ProcessExtension.cs)
Build Solution => castscreen_srv \ Debug

Build / Configuration Manager => Active Release
Build Solution => castscreen_srv \ Release

-----------------------------------------------
Window key + X : Windows Power Shell Admin 

Install:
c:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe c:\Users\pprz\Projects\castscreen_prj\bin\Release\castscreen_prj.exe

Unisnstall:
c:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe /u c:\Users\pprz\Projects\castscreen_prj\bin\Release\castscreen_prj.exe


-----------------------------------------------
Commmand Prompt (console)

services.msc
start/stop

-----------------------------------------------
Commmand Prompt (console) as admin

reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\system /v LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f

check regedit:
Computer\HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\LocalAccountTokenFilterPolicy


sc query castscreen_srv
sc start castscreen_srv
sc query castscreen_srv
sc stop castscreen_srv
sc query castscreen_srv


-----------------------------------------------
optitrack_stream_on.desktop

#!/usr/bin/env xdg-open
[Desktop Entry]
Exec=net rpc service start castscreen_srv -I optitrack2 -U pprz%pprz
Icon=
Name=OPTITRACK_STREAM_ON
StartupNotify=true
Terminal=false
Type=Application
Version=1.0
X-MultipleArgs=false


-----------------------------------------------
optitrack_stream_off.desktop

#!/usr/bin/env xdg-open
[Desktop Entry]
Exec=net rpc service stop castscreen_srv -I optitrack2 -U pprz%pprz
Icon=
Name=OPTITRACK_STREAM_ON
StartupNotify=true
Terminal=false
Type=Application
Version=1.0
X-MultipleArgs=false