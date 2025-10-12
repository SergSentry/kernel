#include <fcntl.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

#include "exchange/api.h"

#define NUM_WRITERS 3
#define NUM_READERS 3

struct thread_params {
  int id;
};

void *writer_thread(void *params) {
  struct thread_params *p = params;
  int fd;
  char message[EXCHANGE_BUFFER_SIZE];

  sprintf(message, "[TEST FAILED]: Message from Writer #%d.\n", p->id);

  fd = open(DEVICE_PATH, O_WRONLY);
  if (fd < 0) {
    perror("[TEST FAILED]: Writer: Error opening device.\n");
    return NULL;
  }

  ssize_t bytes_written = write(fd, message, strlen(message));
  if (bytes_written < 0) {
    perror("[TEST FAILED]: Writer: Write operation failed.\n");
  } else {
    printf("[TEST PROCESS]: Writer #%d: Sent message: %s\n", p->id, message);
  }

  close(fd);
  return NULL;
}

void *reader_thread(void *params) {
  struct thread_params *p = params;
  int fd;
  char buffer[EXCHANGE_BUFFER_SIZE];

  fd = open(DEVICE_PATH, O_RDONLY);
  if (fd < 0) {
    perror("[TEST FAILED]: Reader: Error opening device.\n");
    return NULL;
  }

  sleep(1);

  ssize_t bytes_read = read(fd, buffer, EXCHANGE_BUFFER_SIZE - 1);
  while (bytes_read != 0) {
    if (bytes_read < 0) {
      perror("[TEST FAILED]: Reader: Read operation failed.\n");
    } else {
      buffer[bytes_read] = '\0';
      printf("[TEST PROCESS]: Reader #%d: Received message: %s\n", p->id,
             buffer);
    }

    bytes_read = read(fd, buffer, EXCHANGE_BUFFER_SIZE - 1);
  }

  close(fd);
  return NULL;
}

int main(int argc, char *argv[]) {
  pthread_t writers[NUM_WRITERS], readers[NUM_READERS];
  struct thread_params params[NUM_WRITERS + NUM_READERS];

  printf("[TEST]: Example device broadcast RW operation.\n\n");

  int fd = open(DEVICE_PATH, O_RDWR);
  if (fd < 0) {
    perror("[TEST FAILED]: Error opening device, check and load module.\n");
    return EXIT_FAILURE;
  }

  int work_mode;
  int res = ioctl(fd, EXCHANGE_IOCTL_GET_WORK_MODE, &work_mode);
  if (res < 0) {
    fprintf(stderr, "[TEST FAILED]: Failed ioctl read work_mode.\n");
    close(fd);
    return -1;
  }

  if (work_mode == EXCHANGE_UNICAST) {
    fprintf(stderr, "[TEST FAILED]: Module not in broadcast mode.\n");
    close(fd);
    return -1;
  }

  close(fd);

  for (int i = 0; i < NUM_WRITERS; i++) {
    params[i].id = i;
    pthread_create(&writers[i], NULL, writer_thread, &params[i]);
  }

  for (int i = 0; i < NUM_READERS; i++) {
    params[i + NUM_WRITERS].id = i;
    pthread_create(&readers[i], NULL, reader_thread, &params[i + NUM_WRITERS]);
  }

  for (int i = 0; i < NUM_WRITERS; i++) {
    pthread_join(writers[i], NULL);
  }

  for (int i = 0; i < NUM_READERS; i++) {
    pthread_join(readers[i], NULL);
  }

  printf("[TEST PASSED]: Extend test passed.\n");
  return EXIT_SUCCESS;
}
