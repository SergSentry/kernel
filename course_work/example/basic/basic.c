#include <fcntl.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "exchange/api.h"

int main(int argc, char *argv[]) {
  int fd;
  char message[] = "This is a test message.";

  printf("[TEST]: Example device RW operation.\n\n");

  fd = open(DEVICE_PATH, O_RDWR);
  if (fd < 0) {
    perror("[TEST FAILED]: Error opening device, check and load module.\n");
    return EXIT_FAILURE;
  }

  ssize_t bytes_written = write(fd, message, strlen(message));
  if (bytes_written < 0)
    perror("[TEST FAILED]: Write operation failed.\n");
  else
    printf("[TEST PROCESS]: Wrote %zd bytes to device.\n", bytes_written);

  sleep(1);

  char buffer[EXCHANGE_BUFFER_SIZE];
  ssize_t bytes_read = read(fd, buffer, EXCHANGE_BUFFER_SIZE - 1);
  if (bytes_read < 0) {
    perror("[TEST FAILED]: Read operation failed.\n");
  } else {
    buffer[bytes_read] = '\0';
    printf("[TEST PROCESS]: Received message: %s\n", buffer);
  }

  if (strncmp(buffer, message, sizeof(buffer) - 1) != 0) {
    fprintf(stderr, "[TEST FAILED]: Message mismatch: wrote '%s', got '%s'.\n",
            buffer, message);
    close(fd);
    return -1;
  }

  close(fd);
  printf("[TEST PASSED]: Basic read/write test passed.\n");
  return EXIT_SUCCESS;
}
