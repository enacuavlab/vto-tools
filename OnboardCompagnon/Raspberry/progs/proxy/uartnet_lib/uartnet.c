#include "uartnet.h"
 
uint8_t bufin[uartnet_maxbufsize];
uint8_t bufout[uartnet_maxbufsize];
uint8_t lenin=0;
uint8_t lenout=0;

pthread_cond_t cvin;
pthread_cond_t cvout;
pthread_mutex_t lockin; 
pthread_mutex_t lockout; 

pthread_t thread_uart2net;
pthread_t thread_net2uart;

int sockfd=-1;
int serfd=-1;

struct sockaddr_in to;
struct sockaddr_in from;

/*****************************************************************************/
uint8_t uartnet_getin(uint8_t *ptr)
{
  uint8_t ret=0;

  pthread_mutex_lock(&lockin);
  while(lenin==0) 
    pthread_cond_wait(&cvin, &lockin);

  ret=lenin;
  memcpy(ptr, &bufin, lenin);
  lenin=0;
  pthread_mutex_unlock(&lockin);

  return(ret);
}

/*****************************************************************************/
uint8_t uartnet_getout(uint8_t *ptr)
{
  uint8_t ret=0;

  pthread_mutex_lock(&lockout);
  while(lenout==0) 
    pthread_cond_wait(&cvout, &lockout);

  ret=lenout;
  memcpy(ptr, &bufout, lenout);
  lenout=0;
  pthread_mutex_unlock(&lockout);

  return(ret);
}

/*****************************************************************************/
int net_init(char *netipdest, int netportout, int netportin)
{
  int fd=-1;
  int res=-1;
  int broadenabled = 1;

  if ((fd = socket(AF_INET, SOCK_DGRAM, 0)) == -1) {
    printf("error creating socket");
  } else {
    memset((char *)&from, 0, sizeof(from));
    from.sin_addr.s_addr = htonl(INADDR_ANY);
    from.sin_port = htons(netportin);
    from.sin_family = AF_INET;
    if (bind(fd, (struct sockaddr *)&from,sizeof(from)) == -1) {
        printf("error bind");
    } else {
      
      if (setsockopt(fd, SOL_SOCKET, SO_BROADCAST, (void *) &broadenabled, 
                     sizeof(broadenabled)) < 0) {
        printf("error broad");
      } else {
        memset((char *)&to, 0, sizeof(to));
        to.sin_addr.s_addr = inet_addr(netipdest);
        to.sin_port = htons(netportout);
        to.sin_family = AF_INET;
        res=fd;
      }
    }
  }
  return(res);
}

/*****************************************************************************/
int uart_init(char *serdev, int serspeed)
{
  int fd = open(serdev, O_RDWR | O_NOCTTY);
  if (fd < 0) {
    printf("error opening device");
  } else {
    struct termios new_settings;
    tcgetattr(fd, &new_settings);
    /* input modes  */
    new_settings.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | INPCK | ISTRIP | INLCR | IGNCR
                         | ICRNL | IUCLC | IXON | IXANY | IXOFF | IMAXBEL);
    new_settings.c_iflag |= IGNPAR;
    /* control modes*/
    new_settings.c_cflag &= ~(CSIZE | PARENB | CRTSCTS | PARODD | HUPCL | CSTOPB);
    new_settings.c_cflag |= CREAD | CS8 | CLOCAL;
    /* local modes  */
    new_settings.c_lflag &= ~(ISIG | ICANON | IEXTEN | ECHO | FLUSHO | PENDIN);
    new_settings.c_lflag |= NOFLSH;
    /* output modes */
    new_settings.c_oflag &=~(OPOST|ONLCR|OCRNL|ONOCR|ONLRET);

    cfsetispeed(&new_settings, serspeed);
    cfsetospeed(&new_settings, serspeed);
    tcsetattr(fd, TCSADRAIN, &new_settings);

    tcflush(fd, TCIFLUSH);
  }
  return(fd);
}

/*****************************************************************************/
void *uart2net()
{
  int res=0;
  int rdlen;
  uint8_t buf[uartnet_maxbufsize];

  while (true) {
    // blocking read
    rdlen = read(serfd, &buf, sizeof(buf));
    if(rdlen > 0) {
      pthread_mutex_lock(&lockout);
      sendto(sockfd, &buf, rdlen, 0, (struct sockaddr *)&to, sizeof(to));
      memcpy(&bufout , &buf, rdlen);
      lenout = rdlen;
      pthread_mutex_unlock(&lockout);
      pthread_cond_signal(&cvout); 
    }
  }
}
 
/*****************************************************************************/
void *net2uart()
{
  int rdlen;
  uint8_t buf[uartnet_maxbufsize];
  int addrlen = sizeof(from);

  while (true) {
    // blocking recvfrom
    rdlen = recvfrom(sockfd, &buf, sizeof(buf), 0, (struct sockaddr *)&from, &addrlen);
    if(rdlen > 0) {
      pthread_mutex_lock(&lockin);
      write(serfd, &buf, rdlen); 
      memcpy(&bufin , &buf, rdlen);
      lenin = rdlen;
      pthread_mutex_unlock(&lockin);
      pthread_cond_signal(&cvin); 
    }
  }
}

/*****************************************************************************/
void pthread_start_uart2net()
{
  pthread_attr_t thread_attrs;
  struct sched_param param;

  pthread_attr_init(&thread_attrs);
  pthread_attr_setschedpolicy(&thread_attrs, SCHED_RR);
  param.sched_priority = 20; // SCHED_RR
  pthread_attr_setschedparam(&thread_attrs, &param);
   
  if(pthread_create(&thread_uart2net, &thread_attrs, uart2net, NULL) != 0) {
    printf("error thread creation failed");
  }
}

void pthread_detach_uart2net()
{
  pthread_detach(thread_uart2net);
}
   
void pthread_join_uart2net()
{
  pthread_join(thread_uart2net, NULL);
}

/*****************************************************************************/
void pthread_start_net2uart()
{
  pthread_attr_t thread_attrs;
  struct sched_param param;

  pthread_attr_init(&thread_attrs);
  pthread_attr_setschedpolicy(&thread_attrs, SCHED_RR);
  param.sched_priority = 20; // SCHED_RR
  pthread_attr_setschedparam(&thread_attrs, &param);
   
  if(pthread_create(&thread_net2uart, &thread_attrs, net2uart, NULL) != 0) {
    printf("error thread creation failed");
  }
}

void pthread_detach_net2uart()
{
  pthread_detach(thread_net2uart);
}
   
void pthread_join_net2uart()
{
  pthread_join(thread_net2uart, NULL);
}

/*****************************************************************************/
void *uartnet_run(uartnet_t *arg)
{
  sockfd = net_init(arg->netipdest,
                    arg->netportout,
		    arg->netportin);
  if(sockfd > 0) {
    serfd = uart_init(arg->serdev, 
                      arg->serspeed);
    if(serfd > 0) {
      pthread_start_uart2net();
      pthread_start_net2uart();
      sleep(1);
      pthread_join_uart2net();
      pthread_join_net2uart();
    }
  }
}
