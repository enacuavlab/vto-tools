#ifndef dmxproH
#define dmxproH

#include <iostream>
#include <iomanip>
#include <string>

#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#include "rs232.h"

using namespace std;

#define NB_CANAUX_MAX 512
#define NB_INTERFACES 2


//#define DEBUG_DMX_USB

typedef unsigned char byte;


typedef byte TDmxArray[NB_CANAUX_MAX+1]; //+ le startcode

typedef enum _EnttecInterfaces
{
    OPEN_DMX_USB,
    DMX_USB_PRO
} EnttecInterfaces;

/* Messages formatés */
static const char nomInterfaces [][20] = {
    "Enttec OPEN DMX USB",
    "Enttec DMX USB PRO"
} ;

/* Protocole DMX_USB_PRO */
/* packet delimiters */
const int PKT_SOM = 0x7E; /*Start Of Message*/ 
const int PKT_EOM = 0xE7; /*End Of Message*/

/* packet types */
const int PKT_GETCFG = 3; /* get / set widget parameters */
const int PKT_SETCFG = 4;
const int PKT_GETSERIAL = 10; /* retrives the hardware serial number */

/* dmx modes */
const int PKT_DMXOUT = 6;
const int PKT_DMXIN = 5;
const int PKT_DMX_RDM = 7;

/* dmx in mode control */
const int PKT_DMXIN_MODE = 8; /* set recieve mode */
const int PKT_DMXIN_UPDATE = 9; /* recieve a partial dmx update */
/* Fin du protocole DMX_USB_PRO */

/* size of the available user_data_area */
const int USER_DATA_SIZE = 508;

const int D_TIMEOUT=100;

class EnttecDMXUSB
{
   private :
      EnttecInterfaces interface;/* type d'interface USB Enttec */
      bool detected;/* has been found and active */
      byte device_mode;/* input, output, rdm */
            
      byte FirmwareH, FirmwareL;/* Firmware Version */
      string SerialNumber;/* serial number */
      
      string comport;
      bool comopen;
      bool config;
      byte BreakTime, MABTime;/* Break and MarkAfterBreak timing */
      byte FrameRate;/* tranmission frame rate 1..40 */
      
      char buffer[4096];/* packet buffer */
      CRS232 ser;/* the serial control class for this device */

      TDmxArray dmxout; /* dmx to send */
      int dmxout_length;// how many channels to send
      
      bool dmx_available;// true if new, valid dmx is revieced
      TDmxArray dmxin; /* contains the recieved dmx values */
      int dmxin_length;// contains the length of recieved dmx
      int dmxin_quality;/* non-zero is an invalid dmx frame */
                                 /* bit 0 = recieve queue overflow */
                                 /* bit 1 = recieve overrun */
      byte dmxin_mode;/* full_frame or updates */
      bool dmxin_filter; /* if true only valid dmx with a zero startcode will be sent */

      bool openPort(string port_use);
      void closePort();
        
      int sendPacket(int pkt_type, char *data, int length);
      bool recieve();
  
      void widgetRequestConfig();
      void widgetRequestSerial();
      void processUpdatePacket();
      void widgetRecieveOnChangeMode();
      void widgetRecieveAllMode();

      /* Fonctions de service */  
      int makeword16(byte lsb, byte msb);
      bool isbiton(int value, byte bit);
      void sleep(int usec);
      void hexToStr(int i, int nb, char *s);
      void intToStr(int i, char *s);
      
   protected :

   public :
      EnttecDMXUSB(EnttecInterfaces typeInterface=DMX_USB_PRO, string portInterface="/dev/ttyUSB0");
      ~EnttecDMXUSB();  

      bool IsAvailable() { return detected; }
      EnttecInterfaces GetTypeInterface() { return interface; }
      string GetNomInterface() { return string(nomInterfaces[interface]); }
      string GetSerialNumber() { return SerialNumber; }
      byte GetFirmware_L() { return FirmwareL; }
      byte GetFirmware_H() { return FirmwareH; }
      string GetPortInterface() { return comport; }
      string GetConfiguration();

      bool SetCanalDMX(int canal, byte valeur);
      bool SetNbCanauxDMX(int start=1, int length=NB_CANAUX_MAX);
      bool ResetCanauxDMX(int start=1, int end=NB_CANAUX_MAX);
      void SendDMX();
      bool SendDatasDMX(byte *datas, int start=1, int length=NB_CANAUX_MAX);
      
      void DisplayConfig();
};

#endif
