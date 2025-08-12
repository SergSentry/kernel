// SPDX-License-Identifier: GPL-2.0-only
/**
 * OTUS course homework 'Linux Kernel Development'
 * Task: hw_05_deferred_exec_mech
 * Module: ex_workqueue
 *
 * Copyright (c) 2007-2025 SergSentry
 */

#define pr_fmt(fmt) "%s [%s]: " fmt, KBUILD_MODNAME, __func__

#include <linux/delay.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/kthread.h>
#include <linux/module.h>
#include <linux/rwlock.h>
#include <linux/sched.h>
#include <linux/slab.h>
#include <linux/spinlock.h>
#include <linux/string.h>
#include <linux/wait.h>
#include <linux/workqueue.h>

#include "ex_workqueue.h"

DEFINE_RWLOCK(rwlock);
DECLARE_WAIT_QUEUE_HEAD(wait_queue);

bool event_happened = false;

volatile unsigned long global_value = 0;

static struct task_struct *reader_task;
static struct task_struct *work_task;
static struct workqueue_struct *my_wq;

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

void my_callback_function(struct work_struct *work) {
  write_lock(&rwlock);
  global_value++;
  pr_info("Updated value to %lu\n", global_value);
  write_unlock(&rwlock);

  event_happened = true;
  wake_up_all(&wait_queue);
}

DECLARE_WORK(my_work, my_callback_function);

static int reader_thread(void *arg) {
  while (!kthread_should_stop()) {
    int ret = wait_event_timeout(wait_queue, event_happened, HZ * 3);
    if (ret == 0) {
      pr_info("Timeout expired!\n");
    } else {
      event_happened = false;

      read_lock(&rwlock);
      pr_info("Fetched value is %lu\n", global_value);
      read_unlock(&rwlock);
    }
  }

  pr_info("Worker thread stopped gracefully.\n");
  return 0;
}

static int work_thread(void *arg) {
  while (!kthread_should_stop()) {
    msleep_interruptible(500);
    queue_work(my_wq, &my_work);
  }

  return 0;
}

static int run_cmd_handler(const char *argv) {
  reader_task = kthread_create(reader_thread, NULL, "reader_thread");
  if (IS_ERR(reader_task)) {
    pr_err("Failed to create reader_thread thread.\n");
    cmd_result = PTR_ERR(reader_task);
    return STATUS_CMD_ERROR;
  }

  work_task = kthread_create(work_thread, NULL, "work_thread");
  if (IS_ERR(work_thread)) {
    pr_err("Failed to create work_thread thread.\n");
    cmd_result = PTR_ERR(work_thread);
    return STATUS_CMD_ERROR;
  }

  wake_up_process(work_task);
  wake_up_process(reader_task);

  cmd_result = 0;
  return STATUS_OK;
}

static int stop_cmd_handler(const char *argv) {
  if (work_task != NULL) {
    kthread_stop(work_task);
    work_task = NULL;
  }

  if (work_pending(&my_work)) {
    cancel_work_sync(&my_work);
  }

  flush_workqueue(my_wq);

  if (reader_task != NULL) {
    kthread_stop(reader_task);
    reader_task = NULL;
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

static int __init ex_workqueue_init(void) {
  my_wq = create_singlethread_workqueue("my_queue");
  if (!my_wq) {
    pr_err("Failed to create my_queue workqueue.\n");
    return -ENOMEM;
  }

  pr_info("init\n");
  return 0;
}

static void __exit ex_workqueue_exit(void) {
  if (work_task != NULL) {
    kthread_stop(work_task);
    work_task = NULL;
  }

  if (work_pending(&my_work)) {
    cancel_work_sync(&my_work);
  }

  flush_workqueue(my_wq);
  destroy_workqueue(my_wq);

  if (reader_task != NULL) {
    kthread_stop(reader_task);
    reader_task = NULL;
  }

  pr_info("exit\n");
}

module_init(ex_workqueue_init);
module_exit(ex_workqueue_exit);
