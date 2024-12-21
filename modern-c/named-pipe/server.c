#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#define FIFO_NAME "myfifo"

int main(int argc, char* argv[]) {
    printf("[%s] pid: %d", argv[0], getpid());
    // Create the named pipe (FIFO)
    if (mkfifo(FIFO_NAME, 0666) == -1) {
        perror("mkfifo");
        exit(EXIT_FAILURE);
    }

    // Open the FIFO for writing
    int fd = open(FIFO_NAME, O_WRONLY);
    if (fd == -1) {
        perror("open");
        exit(EXIT_FAILURE);
    }

    // Write some data to the FIFO
    const char *data = "Hello, this is a message from the writer!";
    const size_t writeLen = strlen(data);
    if (write(fd, data, writeLen) == -1) {
        perror("write");
        close(fd);
        exit(EXIT_FAILURE);
    }

    printf("[server] written(%zu):  %s\n", writeLen, data);

    // Close the FIFO
    close(fd);
    return 0;
}
