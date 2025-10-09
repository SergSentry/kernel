// SPDX-License-Identifier: GPL-2.0-only
/**
 * OTUS course homework 'Linux Kernel Development'
 * Task: course work
 * Module: exchange
 *
 * Copyright (c) 2007-2025 SergSentry
 */

#ifndef EX_EXCHANGE_API_H
#define EX_EXCHANGE_API_H

#include <linux/ioctl.h>

#define DEVICE_NAME "exchange"
#define DEVICE_PATH "/dev/exchange"
#define DEVICE_PROC_FILE "/proc/exchange"
#define DEVICE_SYSFS_PATH "/sys/kernel/exchange/statistics"

#define EXCHANGE_BUFFER_SIZE (1024)

#define EXCHANGE_IOCTL_MAGIC '>'

enum exchange_mode {
  EXCHANGE_UNICAST = 0,
  EXCHANGE_BROADCAST,
};

struct message_request {
  pid_t pid;
  char data[EXCHANGE_BUFFER_SIZE];
  size_t size;
};

enum exchange_ioctl_commands {
  EXCHANGE_IOCTL_GET_WORK_MODE = _IOR(EXCHANGE_IOCTL_MAGIC, 0, int),
  EXCHANGE_IOCTL_REQUEST =
      _IOW(EXCHANGE_IOCTL_MAGIC, 1, struct message_request),
};

#endif
