# https://www.cs.colby.edu/maxwell/courses/tutorials/maketutor/
CC=gcc
CFLAGS=-Wall --std=c99 -g -static

build:
	$(CC) $(CFLAGS) server.c -o server
	$(CC) $(CFLAGS) client.c -o client

run: build
	test -e myfifo && rm myfifo || true
	./server &
	sleep 3
	./client

setup:
	echo "[check] dev tools"
	pacman -Q clang || sudo pacman -S clang
	pacman -Q lldb || sudo pacman -S lldb
	pacman -Q gdb || sudo pacman -S gdb
	pacman -Q strace || sudo pacman -S strace
