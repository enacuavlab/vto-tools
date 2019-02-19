#include "enttecdmxusb.h"

EnttecDMXUSB::EnttecDMXUSB(EnttecInterfaces typeInterface/*=DMX_USB_PRO*/, string portInterface/*="/dev/ttyUSB0"*/)
{
    interface = typeInterface;
    comport = portInterface;
    detected = false;
    FirmwareH = 0;
    FirmwareL = 0;/* Firmware Version */
    SerialNumber = "";/* Serial Number */
    comopen = false;
    config = false;
    BreakTime = 0;
    MABTime = 0;
    FrameRate = 0; /* tranmission frame rate 1..40 */

    memset(buffer, 0x00, 4096);

    memset(dmxout, 0x00, NB_CANAUX_MAX+1);//+ le startcode
    memset(dmxin, 0x00, NB_CANAUX_MAX+1);//+ le startcode
    dmxout_length = NB_CANAUX_MAX+1;//+ le startcode
    dmx_available = false;
    dmxin_length = 0;
    dmxin_quality = -1;
    dmxin_filter = false;

    openPort(portInterface);
}

EnttecDMXUSB::~EnttecDMXUSB()
{
    closePort();
}

bool EnttecDMXUSB::SetCanalDMX(int canal, byte valeur)
{
    if(canal > 0 && canal <= NB_CANAUX_MAX) /* 1 à 512 */
    {
        dmxout[canal] = valeur;
        #ifdef DEBUG_DMX_USB
        fprintf(stderr, " EnttecDMXUSB::SetCanalDMX() canal %d -> 0x%02X\n", canal, valeur);
        #endif
    }
    else    return false;
    return true;
}

bool EnttecDMXUSB::SetNbCanauxDMX(int start/*=1*/, int length/*=NB_CANAUX_MAX*/)
{
    if((start > 0 && start <= NB_CANAUX_MAX && length > 0) && ((start+length) <= NB_CANAUX_MAX)) /* 1 à 512 */
    {
        dmxout_length = start+length;
        #ifdef DEBUG_DMX_USB
        fprintf(stderr, " EnttecDMXUSB::SetNbCanauxDMX() de %d à %d = %d\n", start, length, dmxout_length);
        #endif
    }
    else    return false;
    return true;
}

bool EnttecDMXUSB::ResetCanauxDMX(int start/*=1*/, int end/*=NB_CANAUX_MAX*/)
{
    int canal;

    #ifdef DEBUG_DMX_USB
    fprintf(stderr, " EnttecDMXUSB::ResetCanauxDMX() mise à 0 de %d à %d\n", start, end);
    #endif
    /* 1 à 512 */
    if((start > 0 && start <= NB_CANAUX_MAX) && (end > 0 && end <= NB_CANAUX_MAX))
        for(canal=start;canal<end;canal++)
            dmxout[canal] = 0x00;
    else    return false;

    return true;
}

void EnttecDMXUSB::SendDMX()
{
  sendPacket(PKT_DMXOUT, (char *)&dmxout[0], dmxout_length);
  device_mode = PKT_DMXOUT;
}

bool EnttecDMXUSB::SendDatasDMX(byte *datas, int start/*=1*/, int length/*=NB_CANAUX_MAX*/)
{
    #ifdef DEBUG_DMX_USB
    fprintf(stderr, " EnttecDMXUSB::SendDatasDMX() de %d à %d\n", start, length);
    for(int i=0;i<length;i++)
    {
        fprintf(stderr, " canal %d -> 0x%02X\n", i, *(datas+i));
    }
    #endif
    if(datas != NULL)
    {
        if((start > 0 && start <= NB_CANAUX_MAX && length > 0) && ((start+length) <= NB_CANAUX_MAX))
        {
            memcpy((&dmxout[0]+start), datas, length);
            dmxout_length = start+length;
            sendPacket(PKT_DMXOUT, (char *)&dmxout[0], dmxout_length);
            device_mode = PKT_DMXOUT;
            return true;
        }
    }
    return false;
}

string EnttecDMXUSB::GetConfiguration()
{
    char c[256] = "";
    string configuration;

    if(interface == DMX_USB_PRO)
    {
        widgetRequestConfig();
        this->sleep(100);
        recieve();
        widgetRequestSerial();
        this->sleep(100);
        recieve();

        if(config == true)
        {
            sprintf(c, "Firmware: %d.%d\n", FirmwareH, FirmwareL);
            configuration += string(c);
            sprintf(c, "BreakTime: %.2f ms\n", (BreakTime*10.67));
            configuration += string(c);
            sprintf(c, "MABTime: %.2f ms\n", (MABTime*10.67));
            configuration += string(c);
            sprintf(c, "Frames Per Second: %d\n", FrameRate);
            configuration += string(c);
            if(SerialNumber.length() != 0)
            {
                sprintf(c, "Serial Number: %s\n", SerialNumber.c_str());
                configuration += string(c);
            }
        }
    }

    return configuration;
}

void EnttecDMXUSB::DisplayConfig()
{
    if(interface == DMX_USB_PRO)
    {
        if(config == true)
        {
            printf("Interface DMX USB PRO\n");
            printf("Firmware: %d.%d\n", FirmwareH, FirmwareL);
            printf("BreakTime: %.2f ms\n", (BreakTime*10.67));
            printf("MABTime: %.2f ms\n", (MABTime*10.67));
            printf("Frames Per Second: %d\n", FrameRate);
            if (FrameRate > 40) printf("warning: invalid frame rate\n");
            else if (FrameRate < 1) printf("warning: invalid frame rate\n");
            if(SerialNumber.length() != 0)
                printf("Serial Number: %s\n", SerialNumber.c_str());
        }
        else printf("Interface DMX USB PRO : no data config for this interface !\n");
    }
    else printf("Interface OPEN DMX USB : no data config for this interface !\n");
}

/* Emission d'une trame DMX  */
int EnttecDMXUSB::sendPacket(int pkt_type, char *data, int length)
{
	short int len = (short int)length;

    #ifdef DEBUG_DMX_USB
    fprintf(stderr, " EnttecDMXUSB::sendPacket() type : %d (%d octets)\n", pkt_type, length);
    if(comopen == false)
            fprintf(stderr, " Port %s non ouvert\n", comport.c_str());
    else    fprintf(stderr, " Port %s ouvert\n", comport.c_str());
    if(detected == false)
            fprintf(stderr, " Interface %s non détectée\n", nomInterfaces[interface]);
    else    fprintf(stderr, " Interface %s détectée\n", nomInterfaces[interface]);
    #endif
    if(comopen == false && detected == false) return 0;
    if(interface == DMX_USB_PRO)
    {
        ser.SendByte(PKT_SOM);  /* start of message */
        ser.SendByte(pkt_type); /* the packet label, type of packet */
        ser.SendBuffer((byte *)&len, sizeof(len)); /* 16-bit length of packet LSB-MSB */
        if (len > 0) ser.SendBuffer((byte *)data, len); /* packet data */
        ser.SendByte(PKT_EOM); /* end of message */
    }
    else /* OPEN_DMX_USB */
    {
        // 88us break
        ser.SetSerialBreak(1);
        this->sleep(88);
        ser.SetSerialBreak(0);
        this->sleep(8);
        if (len > 0) ser.SendBuffer((byte *)data, len); /* packet data */
    }
    return 1;
}

/* Reception de données DMX  */
bool EnttecDMXUSB::recieve()
{
  int a; /* length of data in buffer */
  int err;
  bool d_update;
  char ts[12]; /* serail number */
  bool valid = false;

  if(comopen == false && detected == false) return false;
  while (valid == false) /* check for waiting data */
    { 
      if (ser.WaitingData() != 0) {/* if data recieved */
        if (ser.RecvByte(0) != (byte)PKT_SOM) /* check to see if a vaild packet */
	  { /* not a valid packet */
#ifdef DEBUG_DMX_USB
            fprintf(stderr, "<RX> not SOM, lost sync\n");
#endif
            valid = false;
	  }
        else  /* valid packet, read rest of header... */
	  {
	    err = ser.RecvBufferEX((byte *)&buffer[0],3,D_TIMEOUT); /* get the header data */
	    
	    switch(buffer[0])    /* determine the packet type */
              { 
	      case PKT_DMXIN : /* 5 */
		{
		  d_update = false;
		  dmxin_length =  makeword16(buffer[1],buffer[2]);
		  dmxin_quality = ser.RecvByte(D_TIMEOUT); /* next byte is data quality */
		  err=ser.RecvBufferEX((byte *)&buffer[0],dmxin_length,D_TIMEOUT); /* get the dmx data + PKT_EOM */
		  if (err == ErrTimeout) { printf("<RX> timeout"); return false; }

		  for (a = 0;a<dmxin_length;a++)
		    /* check if dmx is different to last frame */
		    if (dmxin[a] != buffer[a])
		      {
			dmxin[a] = buffer[a];
			d_update = true; /* frame is different */
		      }
		  printf("<RX> length : %d\n",dmxin_length);
		  if (dmxin_quality != 0) printf("<RX> data invalid !\n");
		  if (dmxin[0] != 0) printf("<RX> non-zero startcode recieved, possible RDM frame ?\n");
		  /* only send valid data, if frame is different from last */
		  if (d_update)
		    {
		      if (dmxin_filter)
			{
			  if ((dmxin_quality = 0) && (dmxin[0] = 0))
			    dmx_available = true; /* dmx passed filter */
			}
		      else dmx_available = true; /* filter not enabled */
		    }
		  valid = true;
		}
		break;
	      case PKT_DMXIN_UPDATE : /* 9 */ /* recieve a dmx update packet */
		{
		  dmxin_length =  makeword16(buffer[1],buffer[2]);
		  err=ser.RecvBufferEX((byte *)&buffer[0],dmxin_length+1,100);
		  if (err == ErrTimeout) { printf("timeout"); return false; }
    
		  processUpdatePacket();
		  dmx_available = true; /* flag new dmx packet */
		  valid = true;
		}
		break;
	      case PKT_GETCFG : /* 3 */ /* recieve the current config from the widget */
		{

		  FirmwareL = ser.RecvByte(D_TIMEOUT);
		  FirmwareH = ser.RecvByte(D_TIMEOUT);
		  BreakTime = ser.RecvByte(D_TIMEOUT);
		  MABTime   = ser.RecvByte(D_TIMEOUT);
		  FrameRate = ser.RecvByte(D_TIMEOUT);
		  valid = true;
		  detected = true;
		  config = true;
		}
		break;
                           
	      case PKT_GETSERIAL : /* 10 */ /* recieve serial number from device */
		{
		  hexToStr(ser.RecvByte(D_TIMEOUT), 2, &ts[0]);
		  hexToStr(ser.RecvByte(D_TIMEOUT), 2, &ts[2]);
		  hexToStr(ser.RecvByte(D_TIMEOUT), 2, &ts[4]);
		  hexToStr(ser.RecvByte(D_TIMEOUT), 2, &ts[6]);

		  if ((ser.RecvByte(D_TIMEOUT)) == (byte)PKT_EOM)
		    {
		      SerialNumber = ts;
		      valid = true;
		    }
		} 
		break;
              } /* case packet_type */
	  } /* if valid packet */
      } /* if buffer has data */
    }
  return true; 
}


void EnttecDMXUSB::closePort()
{
     detected = false;
     if (comopen) 
     {
         ser.CloseSerial();
         comopen = false;
     }
}

bool EnttecDMXUSB::openPort(string port_use/*="/dev/ttyUSB0"*/)
{
    int flags;

    dmxin_filter = false;
    dmxin_length = 0;

    //pas de port ?
    if (port_use.length() == 0)
    {
        return(false);
    }

    dmxout_length = NB_CANAUX_MAX+1; //+ le startcode
    comport = port_use;
    device_mode = PKT_DMXIN; /* par défaut */

    //ouverture du port
    if(interface == DMX_USB_PRO)
    {
        flags = O_RDWR | O_NONBLOCK;
        if(ser.OpenSerial(port_use, flags) == -1) comopen = false;
        else    comopen = true;
        config = true;
    }
    else if(interface == OPEN_DMX_USB)
    {
        flags = O_WRONLY | O_NOCTTY;
        if(ser.OpenSerial(port_use, flags) == -1) comopen = false;
        else    comopen = true;
        config = false;
    }
    else
        if(ser.OpenSerial(port_use) == -1) comopen = false;

    //configuration du port
    if(comopen == true)
    {
        if(interface == DMX_USB_PRO)
                ser.SetSerialParams(4000000, 8, 'N', 1, 0); /* for DMX_USB_PRO */
        else
        {
            ser.SetCustomBaudRate(250000);
            ser.SetSerialParams(38400, 8, 'N', 2, 0); /* for OPEN_DMX_USB */
            ser.SetSerialRTS(0);//clear RTS
        }
        ser.Purge();
    }

    //détection de l'interface
    if(comopen == true)
    {
        if(interface == DMX_USB_PRO)
        {
            SendDMX(); /* set dmx out with 0 */
            this->sleep(100);
            ser.Purge(); /* clear the buffer */
    
            widgetRequestConfig();
            this->sleep(100);
            recieve();
        }
        else detected = true; /* default for OPEN_DMX_USB */
    }

    //recupere la configuration de l'interface détectée et termine
    if (detected)
    {
        if(interface == DMX_USB_PRO)
        {
            widgetRequestSerial();
            this->sleep(100);
            recieve();
        }
        //else /* for OPEN_DMX_USB */
        #ifdef DEBUG_DMX_USB
        std::cerr << " EnttecDMXUSB::OpenPort() " << port_use << std::endl;
        DisplayConfig();
        #endif
        return(true); /* ok */
    }
    closePort(); /* not ok */
    #ifdef DEBUG_DMX_USB
    std::cerr << " EnttecDMXUSB::OpenPort() " << port_use << " : failed !" << std::endl;
    #endif

    return(false);
}

/* send a packet : get configuration */
void EnttecDMXUSB::widgetRequestConfig()
{
  sendPacket(PKT_GETCFG, (char *)NULL, 0);
}

/* send a packet : get serial number */
void EnttecDMXUSB::widgetRequestSerial()
{
  sendPacket(PKT_GETSERIAL, (char *)NULL, 0);
}

/* set to only recieve updates, partial dmx frames */
void EnttecDMXUSB::widgetRecieveOnChangeMode()
{
   byte mode;
   mode = 1;
   sendPacket(PKT_DMXIN_MODE, (char *)&mode, 1);
   device_mode = PKT_DMXIN;
}

/* set to recieve all full dmx frames */
void EnttecDMXUSB::widgetRecieveAllMode()
{
   byte mode;
   mode = 0;
   sendPacket(PKT_DMXIN_MODE, (char *)&mode, 1);
   device_mode = PKT_DMXIN;
}

/* process a validated dmx input update packet from the buffer */
void EnttecDMXUSB::processUpdatePacket()
{
  int cbi, bai, tmp, bi;
  cbi = 0; tmp = 0;
  for (bi = 0;bi<4;bi++)
  {
   for (bai = 0;bai<7;bai++)
   {
     if (isbiton(buffer[1+bi], bai))
     {
        dmxin[(buffer[0] * 8) + cbi] = buffer[6+tmp];
        #ifdef DEBUG_DMX_USB
        std::cerr << " EnttecDMXUSB::ProcessUpdatePacket() ";
        fprintf(stderr, "<RX> update set channel %d to 0x%02X\n", ((buffer[0] * 8) + cbi), buffer[6+tmp]);
        #endif
        tmp++;
     }
     cbi++;
    }
  }
}

void EnttecDMXUSB::sleep(int usec)
{
#ifdef HAVE_NANOSLEEP
        struct timespec req;

        req.tv_sec = usec / 1000000;
        usec -= req.tv_sec * 1000000;
        req.tv_nsec = usec * 1000;

        nanosleep(&req, NULL);
#else
    usleep(usec);
#endif
}

void EnttecDMXUSB::hexToStr(int i, int nb, char *s)
{
   int k = nb-1, l;
   unsigned int num = (unsigned int)i;

   for(;k>=0;k--)
   {
      l=(num>>(k*4)) & 0xF;
      if(l>9) l+=7;
      l+='0';
      *(s++)=l;
   }
   *s=0;
}

void EnttecDMXUSB::intToStr(int i, char *s)
{
   int k;

   if(i<0)
   {
      *(s++)='-';
      i=-i;
   }
   for(k=1;(i/k)>9;k=k*10);
   while(k)
   {
      *(s++)='0' + (i/k);
      i-=(i/k)*k;
      k/=10;
   }
   *s=0;
}

/* function to make a word (16bit) from two bytes (2 x 8bit) */
int EnttecDMXUSB::makeword16(byte lsb, byte msb)
{
   int newnum;
   newnum = msb; newnum = newnum << 8; newnum = newnum + lsb;
   return(newnum);
}

/* bit check function */
bool EnttecDMXUSB::isbiton(int value, byte bit)
{
 int result = (value & (1 << bit));
 if(result != 0) return true;
 return false;
}
