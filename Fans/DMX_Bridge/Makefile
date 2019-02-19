CC = g++-7 # Le compilateur utilisé
MAKE = make
RM = rm
TARGET =  ivy_dmx
MAKEDEP = makedepend

OPTS = -O0 -Wall
OBJS=enttecdmxusb.o rs232.o ivy_dmx.o
INCLUDES = -I/usr/local/include/Ivy
LIBS = -L/usr/local/lib64/ -Wl,-rpath,/usr/local/lib64/ -livy -lpcrecpp
DEBUG = -DDEBUG_DMX_USB -DDEBUG_RS232 -g
WARN = -Wall # Affichage des warnings de compilation

ifndef VERSION
VERSION = RELEASE
endif

# choix des options de compilation
ifeq (DEBUG, $(VERSION))
   CFLAGS = $(INCLUDES) $(OPTS) $(WARN) $(DEBUG)
else
   CFLAGS = $(INCLUDES) $(OPTS)
endif

all: $(TARGET) 

debug:
	@$(MAKE) VERSION=DEBUG

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) $^ -o $@ $(LIBS)

%.o: %.cpp
	$(CC) $(CFLAGS) -o $@ -c $<

clean:
	$(RM) -f *.o

cleanall:
	$(RM) -f *.o *.cpp~ *.h~ ./*~ $(TARGET)

dep:
	$(MAKEDEP) $(CFLAGS) -Y  *.cpp 
	rm -f Makefile.bak

# Dépendances by 'make dep'

enttecdmxusb.o: enttecdmxusb.h rs232.h errcode.h types.h
rs232.o: rs232.h errcode.h types.h
testEnttecDMXUSB.o: enttecdmxusb.h rs232.h errcode.h types.h
testEnttecDMXUSBPRO.o: enttecdmxusb.h rs232.h errcode.h types.h
testEnttecOPENDMXUSB.o: enttecdmxusb.h rs232.h errcode.h types.h
# DO NOT DELETE

enttecdmxusb.o: enttecdmxusb.h rs232.h errcode.h types.h
ivy_dmx.o: /usr/local/include/Ivy/ivysocket.h /usr/local/include/Ivy/ivy.h
ivy_dmx.o: /usr/local/include/Ivy/ivyloop.h
ivy_dmx.o: /usr/local/include/Ivy/ivychannel.h enttecdmxusb.h rs232.h
ivy_dmx.o: errcode.h types.h
rs232.o: rs232.h errcode.h types.h
