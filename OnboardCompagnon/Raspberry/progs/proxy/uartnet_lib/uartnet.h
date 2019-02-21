#include <stdio.h>
#include <stdbool.h>
#include <fcntl.h>
#include <termios.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
 
#define uartnet_maxbufsize 512

typedef struct {
  char serdev[80];
  int  serspeed;
  char netipdest[17];
  int  netportout;
  int  netportin;
} uartnet_t;

void *uartnet_run(uartnet_t *arg);
uint8_t uartnet_getin(uint8_t *ptr);
uint8_t uartnet_getout(uint8_t *ptr);
