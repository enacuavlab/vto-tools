/*
 *	
 *
 *	Copyright (C) 2017
 *	Ecole Nationale de l'Aviation Civile
 */
 



/* SCENARIO  
   
   ° traitement des options :
   -b <bus>, -d <use serial device> -n <DMX node name>


   UTILISATION TYPIQUES:
   ivy_dmx -n FAN
*/


#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <string>

#include "ivysocket.h"
#include "ivy.h"
#include "ivyloop.h"
#include "enttecdmxusb.h"



extern char *optarg;
extern int   optind, opterr, optopt;
EnttecDMXUSB *interfaceDMX;
bool verbose = false;

void dmxOrderCB (IvyClientPtr app, void *user_data, int argc, char *argv[]);

int main(int argc, char *argv[])
{
  int c;
  char *bus ;
  std::string dmxNodeName, dmxDevice = "/dev/ttyUSB0";
  
  const char* helpmsg =
    "[options] \n"
    "\t -b bus\tdefines the Ivy bus to which to connect to, defaults to 127:2010\n"
    "\t -d dev\tdefines the enttec usb pro device (default is /dev/ttyUSB0)\n"
    "\t -v \tverbose\n"
    "\t -n \t name of the DMX node\n" ;



  if (getenv("IVYBUS") != NULL) {
    bus = strdup (getenv("IVYBUS"));
  } else {
    bus = strdup ("127.0.0.1:2000") ;
  }

  while ((c = getopt(argc, argv, "b:n:d:v")) != EOF)
    switch (c) {
    case 'b':
      bus = strdup (optarg);
      break;
    case 'n':
      dmxNodeName = optarg;
      break;
    case 'd':
      dmxDevice = optarg;
      break;
    case 'v':
      verbose = true;
      break;
    default:
      printf("usage: %s %s",argv[0],helpmsg);
      exit(1);
    }

  interfaceDMX = new EnttecDMXUSB(DMX_USB_PRO, dmxDevice);
  string configurationDMX;
    
  if(interfaceDMX->IsAvailable())    {
    configurationDMX = interfaceDMX->GetConfiguration();
    cout << "Interface " << interfaceDMX->GetNomInterface() << " detectee"
	 << std::endl << configurationDMX << std::endl;
  } else {
    cout << "Interface non detectee !" << endl;
    exit (1);
  }
  
  // remet à zéro les valeurs des 512 canaux
  interfaceDMX->ResetCanauxDMX();
  // émet les valeurs des 512 canaux
  interfaceDMX->SendDMX();

  const std::string agentName ("Dmx_" + dmxNodeName);
  const std::string agentNameReady (agentName + " Ready");
    
  IvyInit (agentName.c_str(), agentNameReady.c_str(), NULL, NULL,NULL,NULL);
    
  IvyBindMsg (dmxOrderCB, NULL, "%s channel(\\d+)=(\\d+)", agentName.c_str());
    
  IvyStart (bus);
  IvyMainLoop ();
}



void dmxOrderCB (IvyClientPtr app, void *user_data, int argc, char *argv[])
{
  const uint node = atoi(argv[0]);
  const uint value = atoi(argv[1]);

  if ((node > 511) or (value > 255))
    return;

  if (verbose) {
    printf ("DMX NODE[%d] = %d\n", node, value);
  }
  
  interfaceDMX->SetCanalDMX(node, value);
  interfaceDMX->SendDMX();
}
