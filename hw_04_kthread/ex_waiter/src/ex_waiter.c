// SPDX-License-Identifier: GPL-2.0-only
/**
 * OTUS course homework 'Linux Kernel Development'
 * Task: hw_04_kthread
 * Module: ex_waiter
 *
 * Copyright (c) 2007-2025 SergSentry
 */

#define pr_fmt(fmt) "%s [%s]: " fmt, KBUILD_MODNAME, __func__

#include <linux/delay.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/kthread.h>
#include <linux/module.h>
#include <linux/sched.h>
#include <linux/slab.h>
#include <linux/string.h>
#include <linux/wait.h>

#include "ex_waiter.h"

DECLARE_WAIT_QUEUE_HEAD(event_queue);

volatile bool event_triggered = true;
volatile bool event_occurred = false;

static struct task_struct *waiter_task;

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

static int waiter_thread(void *unused) {
  while (!kthread_should_stop()) {
    pr_info("Waiting for event...");
    wait_event_interruptible(event_queue, event_triggered);
    event_triggered = false;

    int ret = wait_event_timeout(event_queue, event_occurred,
                                 HZ * 5); // wait 5 second
    if (ret == 0) {
      pr_info("Timeout expired!");
    } else {
      pr_info("Event received!");
      event_occurred = false;
      msleep_interruptible(500);
    }
  }

  pr_info("Worker thread stopped gracefully.");
  return 0;
}

static int run_cmd_handler(const char *argv) {
  waiter_task = kthread_create(waiter_thread, NULL, "waiter_thread");
  if (IS_ERR(waiter_task)) {
    pr_err("Failed to create waiter_task thread.\n");
    cmd_result = PTR_ERR(waiter_task);
    return STATUS_CMD_ERROR;
  }

  wake_up_process(waiter_task);

  cmd_result = 0;
  return STATUS_OK;
}

static int stop_cmd_handler(const char *argv) {
  if (waiter_task != NULL) {
    kthread_stop(waiter_task);
    waiter_task = NULL;
  }

  cmd_result = 0;
  return STATUS_OK;
}

static int trigger_cmd_handler(const char *argv) {
  event_triggered = true;
  wake_up_all(&event_queue);
  cmd_result = event_triggered ? 1 : 0;
  return STATUS_OK;
}

static int occurre_cmd_handler(const char *argv) {
  event_occurred = true;
  wake_up_all(&event_queue);
  cmd_result = event_occurred ? 1 : 0;
  return STATUS_OK;
}

static struct command COMMANDS[] = {
    COMMAND(run),
    COMMAND(stop),
    COMMAND(trigger),
    COMMAND(occurre),
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

static int __init ex_waiter_init(void) {
  pr_info("init\n");
  return 0;
}

static void __exit ex_waiter_exit(void) {
  if (waiter_task != NULL) {
    kthread_stop(waiter_task);
    waiter_task = NULL;
  }

  pr_info("exit\n");
}

module_init(ex_waiter_init);
module_exit(ex_waiter_exit);
