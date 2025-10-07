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

#define EXCHANGE_BUFFER_SIZE 1024

#define EXCHANGE_IOCTL_MAGIC '>'

enum exchange_mode {
    EXCHANGE_UNICAST = 0,
    EXCHANGE_BROADCAST,
};

enum exchange_ioctl_commands {
    EXCHANGE_IOCTL_GET_WORK_MODE = _IOR(EXCHANGE_IOCTL_MAGIC, 0, int),
};

#endif
