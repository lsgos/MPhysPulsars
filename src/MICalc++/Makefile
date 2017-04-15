CXX=clang++
CXXFLAGS=-I/usr/local/include/FEAST -L/usr/local/lib/ -lFSToolbox -std=c++11 -O3
CC = clang

build: MICalc.o hellinger_measure.o
	$(CXX) -o micalc MICalc.o hellinger_measure.o $(CXXFLAGS)


MICalc.o: hellinger_measure.h
hellinger_measure.o: 


format:
	clang-format -i MICalc.cc
