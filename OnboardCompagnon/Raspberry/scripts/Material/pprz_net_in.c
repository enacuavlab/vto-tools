#include <stdio.h>
#include <stdbool.h>
#include <unistd.h>
//#include <termios.h>
#include <fcntl.h>
#include <string.h>

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include "pprzlink/my_pprz_messages.h"

#define UART_BUFFERSIZE 512
#define PPRZ_MSGSIZE 255


uint8_t fd_net;
uint8_t netbuf[UART_BUFFERSIZE];
uint8_t pprzbuf[PPRZ_MSGSIZE];
struct pprzlink_device_rx dev_rx;

struct sockaddr_in from;
struct sockaddr_in to;
int addrlen = sizeof(from);

uint8_t netbufcpt=0;
uint8_t netbuflg=0;

/*
/home/pi/pprzlink/tools/generator/gen_messages.py --protocol 2.0 --lang C_standalone --no-validate -o pprzlink/my_pprz_messages.h /home/pi/pprzlink/message_definitions/v1.0/messages.xml datalink --opt PING
*/
/*
gcc pprz_net_in.c -I. -o pprz_net_in
*/

/*****************************************************************************/
int char_available(void) {
  if(netbufcpt == 0) {
    // blocking recvfrom
    netbuflg = recvfrom(fd_net, &netbuf, sizeof(netbuf), 0, (struct sockaddr *)&from, &addrlen);
  }
  return(true);
}

uint8_t get_char(void) {
  uint8_t ret=0;
  if(netbufcpt < netbuflg) ret= netbuf[netbufcpt++];
  if(netbufcpt == netbuflg) netbufcpt=0;
  return(ret);
}

void new_message(uint8_t sender_id, uint8_t receiver_id, uint8_t class_id, uint8_t message_id, uint8_t *buf) {
  printf("In ");
  printf("%d ",message_id);
  if (message_id == PPRZ_MSG_ID_PING) {
    printf("PING\n");
  }
}

/*****************************************************************************/
void *main(int argc, char *argv) {

  int res=-1;
  int broadenabled = 1;

  if ((fd_net = socket(AF_INET, SOCK_DGRAM, 0)) == -1) {
    printf("error creating socket");
  } else {
    memset((char *)&from, 0, sizeof(from));
    from.sin_addr.s_addr = htonl(INADDR_ANY);
    from.sin_port = htons(4243);
    from.sin_family = AF_INET;
    if (bind(fd_net, (struct sockaddr *)&from,sizeof(from)) == -1) {
        printf("error bind");
    } else {
      
      if (setsockopt(fd_net, SOL_SOCKET, SO_BROADCAST, (void *) &broadenabled, 
                     sizeof(broadenabled)) < 0) {
        printf("error broad");
      } else {
        memset((char *)&to, 0, sizeof(to));
        to.sin_addr.s_addr = inet_addr("127.0.0.1");
        to.sin_port = htons(4242);
        to.sin_family = AF_INET;
        res=fd_net;
      }
    }
    dev_rx = pprzlink_device_rx_init(char_available, get_char,(uint8_t *)pprzbuf);

    printf("Ready\n");
    while(true) pprzlink_check_and_parse(&dev_rx, new_message);
  }
}
