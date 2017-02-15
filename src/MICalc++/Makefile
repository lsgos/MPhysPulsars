CC=clang++
CFLAGS=-I/usr/local/include/FEAST -L/usr/local/lib/ -lFSToolbox -std=c++11 -O3
all:
	$(CC) -o micalc MICalc.cc $(CFLAGS)
format:
	clang-format -i MICalc.cc
