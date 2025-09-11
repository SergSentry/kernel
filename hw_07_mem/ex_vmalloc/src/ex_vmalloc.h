// SPDX-License-Identifier: GPL-2.0-only
/**
 * OTUS course homework 'Linux Kernel Development'
 * Task: hw_07_mem
 * Module: ex_vmalloc
 *
 * Copyright (c) 2007-2025 SergSentry
 */

#ifndef EX_VMALLOC_H
#define EX_VMALLOC_H

#define MAX_CMD_STR_LEN (10)
#define MAX_CMD_ARG_STR_LEN (10)
#define MAX_CMD_PARAM_LEN ((MAX_CMD_STR_LEN) + (MAX_CMD_ARG_STR_LEN))

#define STATUS_NONE (-EINVAL)
#define STATUS_UNKNOWN_CMD (-EINVAL)
#define STATUS_OK (0)
#define STATUS_CMD_ERROR (-EINVAL)
#define STATUS_CMD_ERROR_ARG (-EINVAL)
#define STATUS_CMD_ERROR_MEMORY (-ENOMEM)

#define COMMAND(NAME)                                                          \
  { #NAME, NAME##_cmd_handler }

struct command {
  char *name;
  int (*handle)(const char *argv);
};

MODULE_DESCRIPTION("OTUS course homework 'Linux Kernel Development'\n\t\tTask: "
                   "hw_07_mem\n\t\tModule: ex_vmalloc");

MODULE_AUTHOR("SergSentry");
MODULE_LICENSE("GPL");
MODULE_VERSION("0.1");

#endif
