CC=gcc
CCPP=g++
 
CFLAGS=
LDFLAGS=-lpthread

INC_LIB=-I./uartnet_lib 
INC_PPRZLINK=-I./from_gcs/var/include
INC_ROS=-I/opt/ros/kinetic/include 

LIB_ROS=-L/opt/ros/kinetic/lib  -Wl,-rpath,/opt/ros/kinetic/lib -lroscpp -lrosconsole -lroscpp_serialization -lrostime


OBJ=obj
EXE=exe


#all:$(EXE)/pprz_ros_publisher
all:$(EXE)/bridge

$(EXE)/pprz_ros_publisher: $(OBJ)/pprz_ros_publisher.o $(OBJ)/uartnet.o $(OBJ)/pprz_transport.o
	$(CCPP) -o $@ $^ $(LDFLAGS) $(LIB_ROS)

$(EXE)/pprz_ros_subscriber: $(OBJ)/pprz_ros_subscriber.o $(OBJ)/uartnet.o $(OBJ)/pprz_transport.o
	$(CCPP) -o $@ $^ $(LDFLAGS)  $(LIB_ROS)

$(EXE)/pprz_in: $(OBJ)/pprz_in.o $(OBJ)/uartnet.o $(OBJ)/pprz_transport.o
	$(CC) -o $@ $^ $(LDFLAGS)

$(EXE)/pprz_out: $(OBJ)/pprz_out.o $(OBJ)/uartnet.o $(OBJ)/pprz_transport.o
	$(CC) -o $@ $^ $(LDFLAGS)

$(EXE)/bridge: $(OBJ)/bridge.o $(OBJ)/uartnet.o
	$(CC) -o $@ $^ $(LDFLAGS)

$(OBJ)/pprz_transport.o: ./from_gcs/var/share/pprzlink/src/pprz_transport.c
	$(CC) -o $@ -c $< $(CFLAGS) $(INC_PPRZLINK)

$(OBJ)/pprz_ros_publisher.o: pprz_ros/pprz_ros_publisher.cpp
	$(CCPP) -o $@ -c $< $(CFLAGS) $(INC_LIB) $(INC_PPRZLINK) $(INC_ROS)

$(OBJ)/pprz_ros_subscriber.o: pprz_ros/pprz_ros_subscriber.cpp
	$(CCPP) -o $@ -c $< $(CFLAGS) $(INC_LIB) $(INC_PPRZLINK) $(INC_ROS)

$(OBJ)/pprz_in.o: pprz_inout/pprz_in.c
	$(CC) -o $@ -c $< $(CFLAGS) $(INC_LIB) $(INC_PPRZLINK)

$(OBJ)/pprz_out.o: pprz_inout/pprz_out.c
	$(CC) -o $@ -c $< $(CFLAGS) $(INC_LIB) $(INC_PPRZLINK)

$(OBJ)/uartnet.o: uartnet_lib/uartnet.c
	$(CC) -o $@ -c $< $(CFLAGS)

$(OBJ)/bridge.o: bridge/bridge.c
	$(CC) -o $@ -c $< $(CFLAGS) $(INC_LIB)

clean:
	rm -rf $(OBJ)/*

mrproper: clean
	rm -rf $(EXE)/*
