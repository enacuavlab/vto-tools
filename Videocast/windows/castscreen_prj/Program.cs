using System;
using System.ServiceProcess;
using System.Threading;

/*
services.msc

c:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe /u c:\Users\pprz\Projects\castscreen_prj\bin\Release\castscreen_prj.exe

c:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe c:\Users\pprz\Projects\castscreen_prj\bin\Release\castscreen_prj.exe

sc query castscreen_srv
sc start castscreen_srv
sc stop castscreen_srv

*/

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
