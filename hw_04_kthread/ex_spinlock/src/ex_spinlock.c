// SPDX-License-Identifier: GPL-2.0-only
/**
 * OTUS course homework 'Linux Kernel Development'
 * Task: hw_04_kthread
 * Module: ex_spinlock
 *
 * Copyright (c) 2007-2025 SergSentry
 */

#define pr_fmt(fmt) "%s [%s]: " fmt, KBUILD_MODNAME, __func__

#include <linux/delay.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/kthread.h>
#include <linux/module.h>
#include <linux/slab.h>
#include <linux/spinlock.h>
#include <linux/string.h>

#include "ex_spinlock.h"

DEFINE_SPINLOCK(spinlock);

volatile unsigned long global_value = 0;

static struct task_struct *reader_task;
static struct task_struct *writer_task;

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

static int writer_thread(void *arg) {
  while (!kthread_should_stop()) {
    spin_lock(&spinlock);
    global_value++;
    pr_info("Updated value to %lu\n", global_value);
    spin_unlock(&spinlock);
    msleep_interruptible(500);
  }

  pr_info("Worker thread stopped gracefully.\n");
  return 0;
}

static int reader_thread(void *arg) {
  while (!kthread_should_stop()) {
    spin_lock(&spinlock);
    pr_info("Fetched value is %lu\n", global_value);
    spin_unlock(&spinlock);
    msleep_interruptible(500);
  }

  pr_info("Worker thread stopped gracefully.\n");
  return 0;
}

static int run_cmd_handler(const char *argv) {
  reader_task = kthread_create(reader_thread, NULL, "reader_thread");
  if (IS_ERR(reader_task)) {
    pr_err("Failed to create reader_thread thread.\n");
    cmd_result = PTR_ERR(reader_task);
    return STATUS_CMD_ERROR;
  }

  writer_task = kthread_create(writer_thread, NULL, "writer_thread");
  if (IS_ERR(writer_task)) {
    pr_err("Failed to create writer_thread thread.\n");
    cmd_result = PTR_ERR(writer_task);
    return STATUS_CMD_ERROR;
  }

  wake_up_process(writer_task);
  msleep_interruptible(100);
  wake_up_process(reader_task);

  cmd_result = 0;
  return STATUS_OK;
}

static int stop_cmd_handler(const char *argv) {
  if (reader_task != NULL) {
    kthread_stop(reader_task);
    reader_task = NULL;
  }

  if (writer_task != NULL) {
    kthread_stop(writer_task);
    writer_task = NULL;
  }

  cmd_result = global_value;
  return STATUS_OK;
}

static struct command COMMANDS[] = {
    COMMAND(run),
    COMMAND(stop),
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
    strncpy(cmd, cmd_str, strlen(cmd_str));
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

static int __init ex_spinlock_init(void) {
  pr_info("init\n");
  return 0;
}

static void __exit ex_spinlock_exit(void) {
  if (reader_task != NULL) {
    kthread_stop(reader_task);
    reader_task = NULL;
  }

  if (writer_task != NULL) {
    kthread_stop(writer_task);
    writer_task = NULL;
  }

  pr_info("exit\n");
}

module_init(ex_spinlock_init);
module_exit(ex_spinlock_exit);
