/*
   This program is a bridge beetween a serial interface and ethernet network
   The serial interface is fullduplex. 
   The network interface is halfduplex with dedicated ports for incoming and outcoming
   Outcoming data are broadcasted to all receivers connected to the subnetwork
*/
#include "uartnet.h"


void main(int c, char **argv) 
{
  uartnet_t arg;
//  strcpy(arg.serdev,"/dev/ttyAMA0");
  strcpy(arg.serdev,"/dev/ttyUSB0");
  arg.serspeed=B115200;
//  strcpy(arg.netipdest,"192.168.1.255");
  strcpy(arg.netipdest,"127.0.0.1");
  arg.netportout = 4242;
  arg.netportin = 4243;
 
  uartnet_run((void *)&arg);
}
