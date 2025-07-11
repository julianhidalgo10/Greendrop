CC=gcc
CFLAGS=-I./src
SRC=src/main.c src/controller.c src/sensor.c src/relay.c src/logger.c src/config.c src/state.c
OUT=greendrop

all:
	$(CC) $(SRC) -o $(OUT)

run: all
	./$(OUT)