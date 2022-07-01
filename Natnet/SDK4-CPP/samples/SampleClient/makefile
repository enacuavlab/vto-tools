include=-I../../include
libpath=-L../../lib
libs=-lNatNet

all:build/SampleClient build/natnetunicast

build/SampleClient: 
	g++ SampleClient.cpp $(include) $(libpath) $(libs) -o build/SampleClient

build/natnetunicast: 
	g++ natnetunicast.cpp $(include) $(libpath) $(libs) -o build/natnetunicast

.PHONY: clean
clean:
	@rm -f ./build/SampleClient ./build/natnetunicast
