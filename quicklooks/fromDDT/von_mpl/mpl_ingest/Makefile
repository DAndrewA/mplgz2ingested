# $Id: $

CC = gcc
LC = gcc
LIB = -L/home/dturner/netcdf/lib -lnetcdf -lcurl -lm
CFLAGS = -g -I/home/dturner/netcdf/include

all: read_mpl

read_mpl: 
	$(CC) $(CFLAGS) -o dingest_mpl_2 -m32 dave_mpl.polarization.c $(LIB)
	$(CC) $(CFLAGS) -o dingest_mpl_1 -m32 swap.c dave_mpl.1_channel.c $(LIB)

clean:
	rm *.o dingest_mpl_1 dingest_mpl_2
