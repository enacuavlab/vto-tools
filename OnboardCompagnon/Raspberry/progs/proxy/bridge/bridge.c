#include "uartnet.h"


void main(int c, char **argv) 
{
  uartnet_t arg;
  strcpy(arg.serdev,"/dev/ttyAMA0");
  arg.serspeed=B115200;
  strcpy(arg.netipdest,"192.168.1.255");
  arg.netportout = 4242;
  arg.netportin = 4243;
 
  uartnet_run(&arg);
}
