#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "exchange/api.h"

int main(int argc, char *argv[]) {

  printf("[TEST]: Example device read PID list from %s file.\n\n",
         DEVICE_PROC_FILE);

  int fd = open(DEVICE_PATH, O_RDWR);
  if (fd < 0) {
    perror("[TEST FAILED]: Failed to open device, check and load module.\n");
    return EXIT_FAILURE;
  }

  FILE *proc_fp = fopen(DEVICE_PROC_FILE, "r");
  if (!proc_fp) {
    perror("[TEST FAILED]: Failed to open proc file.\n");
    close(fd);
    return EXIT_FAILURE;
  }

  char line[128];
  int my_pid = getpid();
  int found_my_pid = 0;

  printf("[TEST PROCESS]: Read PID list:\n");
  while (fgets(line, sizeof(line), proc_fp)) {
    int pid = atoi(line);
    printf("%d\n", pid);
    if (pid == my_pid) {
      found_my_pid = 1;
      break;
    }
  }

  fclose(proc_fp);
  printf("\n");

  if (!found_my_pid) {
    printf("[TEST FAILED]: PID %d not found in active sessions list\n", my_pid);
    close(fd);
    return EXIT_FAILURE;
  }

  printf("[TEST PROCESS]: PID %d found in active sessions list\n", my_pid);

  int proc_fd = open(DEVICE_PROC_FILE, O_WRONLY);
  if (!proc_fd) {
    perror("[TEST FAILED]: Failed to truncate proc file.\n");
    close(fd);
    return EXIT_FAILURE;
  }

  char message[] = " ";
  write(proc_fd, message, strlen(message));
  close(proc_fd);

  proc_fp = fopen(DEVICE_PROC_FILE, "r");
  if (!proc_fp) {
    perror("[TEST FAILED]: Failed to reopen proc file.\n");
    close(fd);
    return EXIT_FAILURE;
  }

  while (fgets(line, sizeof(line), proc_fp)) {
    printf("[TEST FAILED]: Unexpected PID found: %s.\n", line);
    fclose(proc_fp);
    close(fd);
    return EXIT_FAILURE;
  }

  fclose(proc_fp);
  close(fd);

  printf("[TEST PASSED]: Tests passed successfully\n");
  return EXIT_SUCCESS;
}
