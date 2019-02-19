#include "rs232.h"

CRS232::CRS232()
{
    this->fd = -1;
}

int CRS232::OpenSerial(string port)
{
   int res;

   if ( this->fd != INVALID_HANDLE_VALUE ) CloseSerial();
 
   if ((this->fd = open(port.c_str(),O_RDWR|O_NONBLOCK)) == -1) res = -1;
   else   res = 0;
   #ifdef DEBUG_RS232
		std::cerr << " CRS232::OpenSerial() " << port << " -> " << this->fd << " (" << res << ")" << std::endl;
	#endif
   return res;
}

int CRS232::OpenSerial(string port, int flags)
{
   int res;

   if ( this->fd != INVALID_HANDLE_VALUE ) CloseSerial(); 
   if ((this->fd = open(port.c_str(), flags)) == -1) res = -1;
   else   res = 0;
   #ifdef DEBUG_RS232
        std::cerr << " CRS232::OpenSerial() " << port << " -> " << this->fd << " (" << res << ")" << std::endl;
    #endif
   return res;
}

int CRS232::WaitingData(Pending pending/*=pendingInput*/, timeout_t timeout/*= TIMEOUT_INF*/)
{
    int status;
    struct timeval tv;
    fd_set grp;
    struct timeval *tvp = &tv;

    if ( this->fd == INVALID_HANDLE_VALUE ) return 0;
    if(timeout == TIMEOUT_INF)
        tvp = NULL;
    else
    {
        tv.tv_usec = (timeout % 1000) * 1000;
        tv.tv_sec = timeout / 1000;
    }
    
    FD_ZERO(&grp);
    FD_SET(this->fd, &grp);
    switch(pending)
    {
    case pendingInput:
        status = select(this->fd + 1, &grp, NULL, NULL, tvp);
        break;
    case pendingOutput:
        status = select(this->fd + 1, NULL, &grp, NULL, tvp);
        break;
    case pendingError:
        status = select(this->fd + 1, NULL, NULL, &grp, tvp);
        break;
    }
    if(status < 1)
        return 0;
    
    if(FD_ISSET(this->fd, &grp))
        return 1;
    return 0;
}

int CRS232::SetSerialParams(long speed, int bits, int parity, int stops, int flow_control)
{
	int result = E2ERR_OPENFAILED;

	if ( fd != -1 )
	{
		if (speed >= 300 && speed <= 115200)
			actual_speed = speed;
		if (bits >= 1 && bits <= 16)
			actual_bits = bits;
		if (parity == 'N' || parity == 'E' || parity == 'O')
			actual_parity = parity;
		if (stops >= 1 && stops <= 2)
			actual_stops = stops;
		if (flow_control >= 0 && flow_control <= 2)
			actual_flowcontrol = flow_control;

		struct termios termios;

		if ( tcgetattr(fd, &termios) != 0 )
			return result;

		cfmakeraw(&termios);
		termios.c_cflag |= CLOCAL;		//Disable modem status line check

		//Flow control
		if (actual_flowcontrol == 0)
		{
			termios.c_cflag &= ~CRTSCTS;	//Disable hardware flow control
			termios.c_iflag &= ~(IXON|IXOFF);	//Disable software flow control
		}
		else
		if (actual_flowcontrol == 1)
		{
			termios.c_cflag |= CRTSCTS;
			termios.c_iflag &= ~(IXON|IXOFF);
		}
		else
		{
			termios.c_cflag &= ~CRTSCTS;
			termios.c_iflag |= (IXON|IXOFF);
		}

		//Set size of bits
		termios.c_cflag &= ~CSIZE;
		if (actual_bits <= 5)
			termios.c_cflag |= CS5;
		else
		if (actual_bits == 6)
			termios.c_cflag |= CS6;
		else
		if (actual_bits == 7)
			termios.c_cflag |= CS7;
		else
			termios.c_cflag |= CS8;

		//Set stop bits
		if (actual_stops == 2)
			termios.c_cflag |= CSTOPB;
		else
			termios.c_cflag &= ~CSTOPB;

		//Set parity bit
		if (actual_parity == 'N')
		{
			termios.c_cflag &= ~PARENB;
		}
		else
		if (actual_parity == 'E')
		{
			termios.c_cflag |= PARENB;
			termios.c_cflag &= ~PARODD;
		}
		else
		{	//'O'
			termios.c_cflag |= (PARENB|PARODD);
		}

		//Set speed
		speed_t baudrate;
		switch (speed)
		{
		case 300:
			baudrate = B300;
			break;
		case 600:
			baudrate = B600;
			break;
		case 1200:
			baudrate = B1200;
			break;
		case 2400:
			baudrate = B2400;
			break;
		case 4800:
			baudrate = B4800;
			break;
		case 9600:
			baudrate = B9600;
			break;
		case 19200:
			baudrate = B19200;
			break;
		case 38400:
			baudrate = B38400;
			break;
		case 57600:
			baudrate = B57600;
			break;
		case 115200:
			baudrate = B115200;
			break;
		case 230400:
			baudrate = B230400;
			break;
        case 2500000:
                baudrate = B2500000;
                break;
        case 4000000:
                baudrate = B4000000;
                break;
		default:
			baudrate = B9600;
			break;
		}
		cfsetispeed(&termios,baudrate);
		cfsetospeed(&termios,baudrate);

		termios.c_cc[VMIN] = 1;
		termios.c_cc[VTIME] = 0;

		if ( tcsetattr(fd, TCSANOW, &termios) == 0 )
		{
			fcntl(this->fd,F_SETFL,fcntl(this->fd,F_GETFL)&~O_NONBLOCK);
			result = OK;
		}
	}
    #ifdef DEBUG_RS232
    std::cerr << " CRS232::SetSerialParams() : " << result << std::endl;
    if(result < 0)
      perror(" CRS232::SetSerialParams() ");
    #endif
   
    return result;
}

int CRS232::SetCustomBaudRate(int baud_rate/*=250000*/)
{
    struct serial_struct advsettings;

    if ( this->fd == INVALID_HANDLE_VALUE ) return 0;
    ioctl(fd, TIOCGSERIAL, &advsettings);
    #ifdef DEBUG_RS232
        std::cerr << " CRS232::SetCustomBaudRate() : " << baud_rate << std::endl;
        fprintf(stderr, "Avant -> Baudbase : %i Divisor : %i \n", advsettings.baud_base, advsettings.custom_divisor);
    #endif
 
    advsettings.flags = (advsettings.flags & ~ASYNC_SPD_MASK) | ASYNC_SPD_CUST;
    advsettings.custom_divisor = advsettings.baud_base / baud_rate;

    #ifdef DEBUG_RS232
        std::cerr << " CRS232::SetCustomBaudRate() : " << baud_rate << std::endl;
        fprintf(stderr, "Après -> Baudbase : %i Divisor : %i \n",advsettings.baud_base,advsettings.custom_divisor);
    #endif

    ioctl(fd, TIOCSSERIAL, &advsettings);
    return 1;
}

long CRS232::RecvBufferEX(BYTE *buffer, DWORD len, DWORD read_total_timeout)
{
	int retval = 0;

   if ( fd != INVALID_HANDLE_VALUE )
	{
		long nread, nleft;
		BYTE *ptr;

		nleft = len;
		ptr = buffer;

		/* Wait up to N seconds. */
		struct timeval tv;

		tv.tv_sec = read_total_timeout / 1000;
		tv.tv_usec = (read_total_timeout % 1000) * 1000;

		while (nleft > 0)
		{
			fd_set rfds;
			int rval;

			/* Watch file fd to see when it has input. */
			FD_ZERO(&rfds);
			FD_SET(fd, &rfds);

			rval = select(fd+1, &rfds, NULL, NULL, &tv);
			if (rval < 0)	//Error
			{
				nleft = -1;
				break;
			}
			else
			if (rval == 0)	//Timeout
			{
				nleft = -1;
				retval = E2P_TIMEOUT;
				break;
			}
			else			//Ok
			{
				nread = read(fd, ptr, nleft);
				if (nread < 0)
				{
					nleft = -1;
					break;	//Error
				}
			}

			nleft -= nread;
			ptr   += nread;
		}

		if (nleft >= 0)
			retval = (len - nleft);
	}
	
	#ifdef DEBUG_RS232
        DWORD i;
		std::cerr << " CRS232::RecvBufferEX() : " ;
        for(i=0;i<len;i++)
                fprintf(stderr, "0x%02x ", *(buffer+i));
        fprintf(stderr, "\n");
	#endif
	return retval;
}

BYTE CRS232::RecvByte(DWORD timeout)
{
  char carlu=' ';
  
  if ( this->fd == INVALID_HANDLE_VALUE ) return 0;
  read(this->fd,&carlu,1);
  
#ifdef DEBUG_RS232
  printf(" CRS232::RecvByte() : 0x%02X\n", (BYTE)carlu);
#endif
  return carlu;
}

long CRS232::SendBuffer(BYTE *buffer, DWORD len)
{
	DWORD i;
	#ifdef DEBUG_RS232
		std::cerr << " CRS232::SendBuffer() : " ;
		for(i=0;i<len;i++)
				fprintf(stderr, "0x%02x ", *(buffer+i));
			fprintf(stderr, "\n");
	#endif
	int nwritten, retval = -1;

    if ( this->fd == INVALID_HANDLE_VALUE ) return 0;
	for(i=0;i<len;i++)
	{
		nwritten = write(this->fd, buffer+i, 1);
		if (nwritten <= 0)
			return retval;	//return error
	}
	return len;
}

long CRS232::SendByte(BYTE buffer)
{
   DWORD len = 1;
   
	#ifdef DEBUG_RS232
		std::cerr << " CRS232::SendByte() : " ;
		fprintf(stderr, "0x%02x ", buffer);
		fprintf(stderr, "\n");
	#endif
	int nwritten, retval = -1;

    if ( this->fd == INVALID_HANDLE_VALUE ) return 0;
	nwritten = write(this->fd, &buffer, 1);
	if (nwritten <= 0)
		return retval;	//return error

	return len;
}

void CRS232::CloseSerial()
{
	#ifdef DEBUG_RS232
		std::cerr << " CRS232::CloseSerial() " << std::endl;
	#endif
	close(this->fd);
}

int CRS232::flushInput(void)
{
    if ( this->fd == INVALID_HANDLE_VALUE ) return 0;
    tcflush(this->fd, TCIFLUSH);
    return 1;
}

int CRS232::flushOutput(void)
{
    if ( this->fd == INVALID_HANDLE_VALUE ) return 0;
    tcflush(this->fd, TCOFLUSH);
    return 1;
}

void CRS232::Purge(void)
{
   flushInput();
   flushOutput();
}

int CRS232::SendBreak(void)
{
    if ( this->fd == INVALID_HANDLE_VALUE ) return 0;
    tcsendbreak(this->fd, 0);
    return 1;
}

void CRS232::WaitForTxEmpty()
{
    if ( fd != INVALID_HANDLE_VALUE )
        tcdrain(fd);
}

int CRS232::SetSerialBreak(int state)
{
    int result = E2ERR_OPENFAILED;

    if ( this->fd == INVALID_HANDLE_VALUE ) return 0;
#if defined(TIOCSBRK) && defined(TIOCCBRK) //check if available for compilation 
    if (state) 
        result = ioctl(fd,TIOCSBRK,0); 
    else 
        result = ioctl(fd,TIOCCBRK,0); 
	#ifdef DEBUG_RS232
		std::cerr << " CRS232::SetSerialBreak() : " << state << std::endl;
	#endif
#else 
    #ifndef DEBUG_RS232
    fprintf(stderr, " CRS232::SetSerialBreak can't get IOCTL\n");
    #endif
#endif 
    return result;
}

int CRS232::SetSerialTimeouts(long init_read, long while_read)
{
    long result = E2ERR_OPENFAILED;

    if (while_read >= 0)
        read_interval_timeout = while_read;
    if (init_read >= 0)
        read_total_timeout = init_read;

    result = OK;

    return result;
}

int CRS232::SetSerialDTR(int dtr)
{
    int result = E2ERR_OPENFAILED;
    int flags; 

    if ( this->fd == INVALID_HANDLE_VALUE ) return 0;
    ioctl(fd,TIOCMGET, &flags); 
    if (dtr)
        flags |= TIOCM_DTR; 
    else
        flags &= ~TIOCM_DTR; 
    result = ioctl(fd,TIOCMSET, &flags); 

    return result;
}

int CRS232::SetSerialRTS(int rts)
{
    int result = E2ERR_OPENFAILED;
    int flags; 

    if ( this->fd == INVALID_HANDLE_VALUE ) return 0;
    ioctl(fd,TIOCMGET, &flags); 
    if (rts)
        flags |= TIOCM_RTS; 
    else
        flags &= ~TIOCM_RTS; // Set RTS High ?
    result = ioctl(fd,TIOCMSET, &flags); 

    return result;
}

int CRS232::SetSerialRTSDTR(int state)
{
    int result = E2ERR_OPENFAILED;
    int flags; 

    if ( this->fd == INVALID_HANDLE_VALUE ) return 0;
    ioctl(fd,TIOCMGET, &flags); 
    if (state)
    {
        flags |= (TIOCM_RTS|TIOCM_DTR); 
    }
    else
    {
        flags &= ~(TIOCM_RTS|TIOCM_DTR); 
    }
    result = ioctl(fd,TIOCMSET, &flags); 

    return result;
}

int CRS232::GetSerialDSR() const
{
    int result = E2ERR_OPENFAILED;
    int flags; 

    if ( this->fd == INVALID_HANDLE_VALUE ) return 0;
    if (ioctl(fd,TIOCMGET, &flags) != -1)
        result = (flags & TIOCM_DSR); 

    return result;
}

int CRS232::GetSerialCTS() const
{
    int result = E2ERR_OPENFAILED;
    int flags; 

    if ( this->fd == INVALID_HANDLE_VALUE ) return 0;
    if (ioctl(fd,TIOCMGET, &flags) != -1)
        result = (flags & TIOCM_CTS); 

    return result;
}
