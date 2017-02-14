CC=clang++
CFLAGS=-I/usr/local/include/FEAST -I/usr/local/include/MIToolbox -L/usr/local/lib/ -lFSToolbox -lMIToolbox -std=c++11 
all:
	$(CC) -o micalc MICalc.cc $(CFLAGS)
format:
	clang-format -i MICalc.cc