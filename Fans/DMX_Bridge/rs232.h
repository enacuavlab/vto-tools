#ifndef RS232_H
#define RS232_H

#include <iostream>
#include <iomanip>
#include <string>

#include <stdio.h>
#include <errno.h>
#include <termios.h>
#include <linux/serial.h>
#include <termio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/signal.h>
#include <sys/time.h>
#include <fcntl.h>

#include "errcode.h"
#include "types.h"

#define	MAX_COMPORTS	4
#define	MAXLINESIZE	128

#define ErrTimeout 9997
#define TIMEOUT_INF ~((timeout_t) 0)

#define INVALID_HANDLE_VALUE -1

//#define DEBUG_RS232

typedef enum _Pending
{
    pendingInput,
    pendingOutput,
    pendingError
} Pending;

typedef  unsigned long  timeout_t;

using namespace std;

class CRS232
{
	private:
        long actual_speed;
        int actual_bits, actual_parity, actual_stops;
        int actual_flowcontrol;
        int fd;
        struct termios old_termios;
        long read_total_timeout, read_interval_timeout;
        int flushInput(void);
        int flushOutput(void);

	public:
        CRS232();
	    int OpenSerial(string port);
        int OpenSerial(string port, int flags);
	    void CloseSerial();
        int WaitingData(Pending pending=pendingInput, timeout_t timeout= TIMEOUT_INF);
        long RecvBufferEX(BYTE *buffer, DWORD len, DWORD read_total_timeout=0);
        BYTE RecvByte(DWORD timeout=0);
	    long SendBuffer(BYTE *buffer, DWORD len);
        long SendByte(BYTE buffer);
	    int SetSerialParams(long speed = -1, int bits = -1, int parity = -1, int stops = -1, int flow_control = -1);
        int SetCustomBaudRate(int baud_rate=250000);
        void Purge(void);
        void WaitForTxEmpty();
        int SendBreak(void);
        int SetSerialTimeouts(long init_read, long while_read);
        int SetSerialBreak(int state);
        int SetSerialDTR(int dtr);
        int SetSerialRTS(int rts);
        int GetSerialDSR() const;
        int GetSerialCTS() const;
        int SetSerialRTSDTR(int state);
};

#endif
