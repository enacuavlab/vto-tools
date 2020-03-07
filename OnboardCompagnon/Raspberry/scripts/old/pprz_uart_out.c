#include <stdio.h>
#include <stdbool.h>
#include <unistd.h>
#include <termios.h>
#include <fcntl.h>
#include <string.h>

#include "pprzlink/my_pprz_messages.h"

//#define UART_DEVICE "/dev/ttyAMA0"
#define UART_DEVICE "/dev/ttyUSB0"
#define UART_BAUDRATE B115200
#define UART_BUFFERSIZE 512

#define PPRZ_MSGSIZE 255


uint8_t fd_uart;
uint8_t uartbuf[UART_BUFFERSIZE];
uint8_t pprzbuf[PPRZ_MSGSIZE];
struct pprzlink_device_rx dev_rx;

uint8_t uartbufcpt=0;
uint8_t uartbuflg=0;

/*
/home/pi/pprzlink/tools/generator/gen_messages.py --protocol 2.0 --lang C_standalone --no-validate -o pprzlink/my_pprz_messages.h /home/pi/pprzlink/message_definitions/v1.0/messages.xml telemetry --opt AUTOPILOT_VERSION,ALIVE,ENERGY,SVINFO,DL_VALUE,DATALINK_REPORT,WP_MOVED_ENU,ROTORCRAFT_FP,INS_REF,GPS_INT,ROTORCRAFT_NAV_STATUS,INS,UART_ERRORS,AIR_DATA,ROTORCRAFT_STATUS

gcc pprz_uart_out.c -I. -o pprz_uart_out
*/

/*****************************************************************************/
int char_available(void) {
  if(uartbufcpt == 0) {
    uartbuflg = read(fd_uart, &uartbuf, sizeof(uartbuf)); // blocking read
  }
  return(true);
}

uint8_t get_char(void) {
  uint8_t ret=0;
  if(uartbufcpt < uartbuflg) ret= uartbuf[uartbufcpt++];
  if(uartbufcpt == uartbuflg) uartbufcpt=0;
  return(ret);
}

void new_message(uint8_t sender_id, uint8_t receiver_id, uint8_t class_id, uint8_t message_id, uint8_t *buf) {
  printf("In ");
  printf("%d ",message_id);
  if (message_id == PPRZ_MSG_ID_AUTOPILOT_VERSION) {
    printf("AUTOPILOT_VERSION\n");
  }
  else if (message_id == PPRZ_MSG_ID_ALIVE) {
    printf("ALIVE\n");
  }
  else if (message_id == PPRZ_MSG_ID_ENERGY) {
    printf("ENERGY\n");
  }
  else if (message_id == PPRZ_MSG_ID_SVINFO) {
    printf("SVINFO\n");
  }
  else if (message_id == PPRZ_MSG_ID_DL_VALUE) {
    printf("DL_VALUE\n");
  }
  else if (message_id == PPRZ_MSG_ID_DATALINK_REPORT) {
    printf("DATALINK_REPORT\n");
  }
  else if (message_id == PPRZ_MSG_ID_WP_MOVED_ENU) {
    printf("WP_MOVED_ENU\n");
  }
  else if (message_id == PPRZ_MSG_ID_ROTORCRAFT_FP) {
    printf("ROTORCRAFT_FP\n");
  }
  else if (message_id == PPRZ_MSG_ID_GPS_INT) {
    printf("GPS_INT\n");
  }
  else if (message_id == PPRZ_MSG_ID_INS_REF) {
    printf("INS_REF\n");
  }
  else if (message_id == PPRZ_MSG_ID_ROTORCRAFT_NAV_STATUS) {
    printf("ROTORCRAFT_NAV_STATUS\n");
  }
  else if (message_id == PPRZ_MSG_ID_INS) {
    printf("INS\n");
  }
  else if (message_id == PPRZ_MSG_ID_UART_ERRORS) {
    printf("UART_ERRORS\n");
  }
  else if (message_id == PPRZ_MSG_ID_AIR_DATA) {
    printf("AIR_DATA\n");
    printf("pressure (%f) ",pprzlink_get_AIR_DATA_pressure(buf));
    printf("amsl baro (%f) ",pprzlink_get_AIR_DATA_amsl_baro(buf));
    printf("\n");
  }
  else if (message_id == PPRZ_MSG_ID_ROTORCRAFT_STATUS) {
    printf("ROTORCRAFT_STATUS\n");
  }
}

/*****************************************************************************/
void *main(int argc, char *argv) {

  fd_uart = open(UART_DEVICE, O_RDWR | O_NOCTTY);
  if(fd_uart > 0) {
  
    struct termios tty;
    memset (&tty, 0, sizeof(tty));
    tcgetattr ( fd_uart, &tty );
    /* configuration needed for ttyUSB */
    /* input modes  */
    tty.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | INPCK | ISTRIP | INLCR | IGNCR
		   | ICRNL | IUCLC | IXON | IXANY | IXOFF | IMAXBEL);
    tty.c_iflag |= IGNPAR;
    /* control modes*/
    tty.c_cflag &= ~(CSIZE | PARENB | CRTSCTS | PARODD | HUPCL | CSTOPB);
    tty.c_cflag |= CREAD | CS8 | CLOCAL;
    /* local modes  */
    tty.c_lflag &= ~(ISIG | ICANON | IEXTEN | ECHO | FLUSHO | PENDIN);
    tty.c_lflag |= NOFLSH;
    /* output modes */
    tty.c_oflag &=~(OPOST|ONLCR|OCRNL|ONOCR|ONLRET);
    cfsetospeed (&tty, (speed_t)UART_BAUDRATE);
    cfsetispeed (&tty, (speed_t)UART_BAUDRATE);
    tcsetattr ( fd_uart, TCSANOW, &tty ); 
    tcflush(fd_uart, TCIFLUSH);
    
    dev_rx = pprzlink_device_rx_init(char_available, get_char,(uint8_t *)pprzbuf);

    printf("Ready\n");
    while(true) pprzlink_check_and_parse(&dev_rx, new_message);
  }
}
