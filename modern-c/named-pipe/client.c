#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

#define FIFO_NAME "myfifo"

int main(int argc, char* argv[]) {
    printf("[%s] pid: %d", argv[0], getpid());

    // Write some data to the FIFO
    char data[256] = { 0 };
    int fd = open(FIFO_NAME, O_RDONLY);
    if (fd == -1) {
        perror("open");
        exit(EXIT_FAILURE);
    }

    if (read(fd, data, sizeof(data)) == -1) {
        perror("read");
        close(fd);
        exit(EXIT_FAILURE);
    }

    printf("[client] read: %s\n", data);

    // Close the FIFO
    close(fd);
    return 0;
}
