#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

#include "exchange/api.h"

int main(int argc, char *argv[]) {

  printf("[TEST]: Example device ioctl.\n\n");

  int fd = open(DEVICE_PATH, O_RDWR);
  if (fd < 0) {
    perror("[TEST FAILED]: Failed to open device, check and load module.\n");
    return EXIT_FAILURE;
  }

  int work_mode;
  int res = ioctl(fd, EXCHANGE_IOCTL_GET_WORK_MODE, &work_mode);
  if (res < 0) {
    fprintf(stderr, "[TEST FAILED]: Failed ioctl read work_mode.\n");
    close(fd);
    return -1;
  }

  printf("[TEST PROCESS]: Current work mode: %d\n", work_mode);

  char message[] = "This is a test message.";

  struct message_request request;
  request.pid = (unsigned int)getpid();
  request.size = (unsigned int)strlen(message);
  memcpy(&request.data, &message, strlen(message));

  printf("[TEST PROCESS]: Send message to self.\n");
  res = ioctl(fd, EXCHANGE_IOCTL_REQUEST, &request);
  if (res < 0) {
    fprintf(stderr, "[TEST FAILED]: Failed ioctl write request.\n");
    close(fd);
    return -1;
  }

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
  printf("[TEST PASSED]: IOCTL test passed.\n");
  return EXIT_SUCCESS;
}
