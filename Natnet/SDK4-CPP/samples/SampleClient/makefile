include=-I../../include
libpath=-L../../lib
libs=-lNatNet

all:	build/SampleClient build/natnetunicast build/natnetunicast2ivy build/test

build/test: 
	g++ test.cpp $(include) $(libpath) $(libs) -o build/test

build/SampleClient: 
	g++ SampleClient.cpp $(include) $(libpath) $(libs) -o build/SampleClient

build/natnetunicast: 
	g++ natnetunicast.cpp $(include) $(libpath) $(libs) -o build/natnetunicast

build/natnetunicast2ivy:
	g++ natnetunicast2ivy.cpp $(include) $(libpath) $(libs) -livy -o build/natnetunicast2ivy

.PHONY: clean
clean:
	@rm -f ./build/SampleClient ./build/natnetunicast ./build/natnetunicast2ivy ./build/test
