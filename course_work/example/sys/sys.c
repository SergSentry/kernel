#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "exchange/api.h"

int read_statistic(int *data) {
  FILE *sys_fp = fopen(DEVICE_SYSFS_PATH, "r");
  if (!sys_fp) {
    perror("[TEST FAILED]: Failed to open proc file.\n");
    return EXIT_FAILURE;
  }

  char line[128];
  int record = 0;

  printf("[TEST PROCESS]: Read statistic:\n");
  while (fgets(line, sizeof(line), sys_fp)) {
    int digit = atoi(line);
    if (record == 0) {
      printf("[TEST PROCESS]: total request %d\n", digit);
      *data = digit;
    } else if (record == 1) {
      printf("[TEST PROCESS]: dropped request %d\n", digit);
      data++;
      *(data) = digit;
    }

    record++;
  }

  fclose(sys_fp);
  printf("\n");
  return 0;
}

int reset_statistic(void) {
  printf("[TEST PROCESS]: Reset statistic:\n");
  int sys_fd = open(DEVICE_SYSFS_PATH, O_WRONLY);
  if (!sys_fd) {
    perror("[TEST FAILED]: Failed to truncate proc file.\n");
    return EXIT_FAILURE;
  }

  char message[] = " ";
  write(sys_fd, message, strlen(message));
  close(sys_fd);
  printf("\n");
  return 0;
}

int main(int argc, char *argv[]) {

  printf("[TEST]: Example device read statistic data from %s file.\n\n",
         DEVICE_SYSFS_PATH);

  int fd = open(DEVICE_PATH, O_RDWR);
  if (fd < 0) {
    perror("[TEST FAILED]: Failed to open device, check and load module.\n");
    return EXIT_FAILURE;
  }

  int before_reset[2] = {0};
  int result = read_statistic(&before_reset[0]);
  if (result) {
    perror("[TEST FAILED]: Failed to read statistic.\n");
    close(fd);
    return EXIT_FAILURE;
  }

  printf("[TEST PROCESS]: Write message to module\n");
  char message[] = "test";
  write(fd, message, strlen(message));
  printf("\n");

  sleep(1);

  int after_write[2] = {0};
  result = read_statistic(&after_write[0]);
  if (result) {
    close(fd);
    return EXIT_FAILURE;
  }

  int check_incriment = 0;
  if (before_reset[0] + 1 == after_write[0]) {
    printf("[TEST PROCESS]: Total request incriment\n");
    check_incriment = 1;
  }
  if (before_reset[1] + 1 == after_write[1]) {
    printf("[TEST PROCESS]: Dropped request incriment\n");
    check_incriment = 1;
  }

  result = reset_statistic();
  if (result) {
    close(fd);
    return EXIT_FAILURE;
  }

  sleep(1);

  int after_resset[2] = {0};
  result = read_statistic(&after_resset[0]);
  if (result) {
    close(fd);
    perror("[TEST FAILED]: Failed to read statistic.\n");
    return EXIT_FAILURE;
  }

  close(fd);

  if (check_incriment && after_resset[0] == 0 && after_resset[0] == 0)
    printf("[TEST PASSED]: Tests passed successfully\n");
  else {
    printf("[TEST FAILED]: Tests fail\n");
    return EXIT_FAILURE;
  }

  return EXIT_SUCCESS;
}
