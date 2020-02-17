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
/home/pi/pprzlink/tools/generator/gen_messages.py --protocol 2.0 --lang C_standalone --no-validate -o pprzlink/my_pprz_messages.h /home/pi/pprzlink/message_definitions/v1.0/messages.xml telemetry --opt ALIVE,GPS,IMU_ACCEL_SCALED,IMU_GYRO_SCALED,AIR_DATA,ACTUATORS
gcc -g pprz_uart_out.c -I. -o pprz_uart_out
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
  if (message_id == PPRZ_MSG_ID_ALIVE) {
    printf("ALIVE\n");
  } 
  else if (message_id == PPRZ_MSG_ID_GPS) {
    printf("GPS (%d)\n",pprzlink_get_GPS_mode(buf));
  }
  else if (message_id == PPRZ_MSG_ID_ACTUATORS) {
    uint8_t nb=pprzlink_get_ACTUATORS_values_length(buf);
    printf("ACTUATORS (%d)",nb);
    int16_t tmp[6];
    memcpy(&tmp,pprzlink_get_ACTUATORS_values(buf),nb*sizeof(int16_t));
    for(int i=0;i<nb;i++) printf("(%ld)",tmp[i]);
    printf("\n");
  }
  else if (message_id == PPRZ_MSG_ID_IMU_GYRO_SCALED) {
    printf("GYRO ");
    printf("p(%ld)",pprzlink_get_IMU_GYRO_SCALED_gp(buf));
    printf("q(%ld)",pprzlink_get_IMU_GYRO_SCALED_gq(buf));
    printf("r(%ld)",pprzlink_get_IMU_GYRO_SCALED_gr(buf));
    printf("\n");
  }
  else if (message_id == PPRZ_MSG_ID_IMU_ACCEL_SCALED) {
    printf("ACCEL ");
    printf("p(%ld)",pprzlink_get_IMU_ACCEL_SCALED_ax(buf));
    printf("q(%ld)",pprzlink_get_IMU_ACCEL_SCALED_ay(buf));
    printf("r(%ld)",pprzlink_get_IMU_ACCEL_SCALED_az(buf));
    printf("\n");
  }
  else if (message_id == PPRZ_MSG_ID_AIR_DATA) {
    printf("AIR_DATA ");
    printf("pressure (%f) ",pprzlink_get_AIR_DATA_pressure(buf));
    printf("amsl baro (%f) ",pprzlink_get_AIR_DATA_amsl_baro(buf));
    printf("\n");
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
    while(true) pprzlink_check_and_parse(&dev_rx, new_message);
  }
}
