// SPDX-License-Identifier: GPL-2.0-only
/**
 * OTUS course homework 'Linux Kernel Development'
 * Task: hw_07_mem
 * Module: ex_vmalloc
 *
 * Copyright (c) 2007-2025 SergSentry
 */

#define pr_fmt(fmt) "%s [%s]: " fmt, KBUILD_MODNAME, __func__

#include <linux/init.h>
#include <linux/io.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/slab.h>
#include <linux/string.h>
#include <linux/time.h>

#include "ex_vmalloc.h"

#define MAX_SIZE (ULONG_MAX)

static char *test_ptr = NULL;

static int cmd_execute(const char *cmd_str);

static int cmd_result = 0;
module_param(cmd_result, int, 0640);
MODULE_PARM_DESC(cmd_result, "A command result param");

static int cmd_status = STATUS_NONE;
module_param(cmd_status, int, 0640);
MODULE_PARM_DESC(cmd_status, "A command status param");

static char cmd_param[MAX_CMD_PARAM_LEN + 1];
static int set_cmd_param(const char *val, const struct kernel_param *kp) {
  if (!val || strlen(val) <= 1) {
    return STATUS_CMD_ERROR_ARG;
  }

  strlcpy(cmd_param, val, MAX_CMD_PARAM_LEN);
  cmd_status = cmd_execute(cmd_param);
  return cmd_status;
}

struct kernel_param_ops param_ops_cmd_param = {.set = set_cmd_param};
module_param_cb(cmd_param, &param_ops_cmd_param, &cmd_param, 0640);
MODULE_PARM_DESC(cmd_param, "A command line param");

static int check_physical_continuity(void *ptr, size_t size) {
  unsigned long first_pfn = virt_to_phys(ptr) >> PAGE_SHIFT;
  unsigned long last_pfn = virt_to_phys((char *)ptr + size - 1) >> PAGE_SHIFT;

  return (last_pfn - first_pfn) == (size / PAGE_SIZE) ? 1 : 0;
}

static int get_mem_cmd_handler(const char *argv) {
  cmd_result = 0;

  size_t max_size = MAX_SIZE;
  unsigned long start_time, end_time;

  while (max_size > 0) {
    start_time = ktime_get_ns();
    test_ptr = vmalloc(max_size);
    end_time = ktime_get_ns();
    if (!test_ptr) {
      pr_info("vmalloc: %zu byte\n", max_size);
      max_size >>= 1;
    } else {
      break;
    }
  }

  if (!test_ptr) {
    pr_err("vmalloc: FAIL, err_msg = no memory allocated!\n");
    return STATUS_CMD_ERROR_MEMORY;
  }

  unsigned long time_mem_allocating = (end_time - start_time) / 1000;

  pr_info("vmalloc: SUCCSESS\n");

  char *type = check_physical_continuity(test_ptr, max_size) ? "CONTINUOUS"
                                                             : "NOT CONTINUOUS";
  pr_info("vmalloc: %zu byte, %zu ms, type: %s\n", max_size,
          time_mem_allocating, type);

  vfree(test_ptr);
  test_ptr = NULL;

  return STATUS_OK;
}

static struct command COMMANDS[] = {
    COMMAND(get_mem),
};

static int cmd_execute(const char *cmd_str) {
  int cmd_status = STATUS_UNKNOWN_CMD;
  if (cmd_str == NULL || strlen(cmd_str) <= 1)
    return cmd_status;

  char cmd[MAX_CMD_STR_LEN + 1] = {0};
  char cmd_args[MAX_CMD_ARG_STR_LEN + 1] = {0};

  // split cmd_str to command and arguments
  char *p_index = memchr(cmd_str, ' ', MAX_CMD_STR_LEN);
  if (p_index) {
    int index = (int)(p_index - cmd_str);
    if (index > 0 && index < MAX_CMD_STR_LEN) {
      strlcpy(cmd, cmd_str, index + 1);
      strlcpy(cmd_args, cmd_str + index + 1, strlen(cmd_str));
    } else {
      return cmd_status;
    }
  } else {
    int size = min(MAX_CMD_STR_LEN, strlen(cmd_str));
    strncpy(cmd, cmd_str, size);
  }

  // find and execute cmd
  int cmd_count = ARRAY_SIZE(COMMANDS);
  for (int i = 0; i < cmd_count; i++) {
    struct command cur_cmd = COMMANDS[i];
    if (strncmp(cmd, cur_cmd.name, strlen(cur_cmd.name)) == 0) {
      cmd_status = cur_cmd.handle(cmd_args);
      break;
    }
  }

  return cmd_status;
}

static int __init ex_vmalloc_init(void) {
  pr_info("init\n");
  return 0;
}

static void __exit ex_vmalloc_exit(void) {
  if (test_ptr) {
    vfree(test_ptr);
    test_ptr = NULL;
  }

  pr_info("exit\n");
}

module_init(ex_vmalloc_init);
module_exit(ex_vmalloc_exit);
