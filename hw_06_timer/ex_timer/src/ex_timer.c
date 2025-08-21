// SPDX-License-Identifier: GPL-2.0-only
/**
 * OTUS course homework 'Linux Kernel Development'
 * Task: hw_06_timer
 * Module: ex_timer
 *
 * Copyright (c) 2007-2025 SergSentry
 */

#define pr_fmt(fmt) "%s [%s]: " fmt, KBUILD_MODNAME, __func__

#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/ktime.h>
#include <linux/module.h>
#include <linux/slab.h>
#include <linux/string.h>
#include <linux/timer.h>

#include "ex_timer.h"

static struct timer_list *pulse_timer = NULL;
static struct timer_list *duty_timer = NULL;

static int pulse_period = 30; // per sec
static int duty_period = 5;   // 5 per min
static int duty_count = 0;
static long jiffies_pulse_period = 0;

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

static void duty_callback(struct timer_list *timer) {
  if (pulse_timer != NULL) {
    del_timer_sync(pulse_timer);
    kfree(pulse_timer);
    pulse_timer = NULL;
  }
}

static void pulse_callback(struct timer_list *timer) {
  if (pulse_timer != NULL) {
    pr_info("min=%d: Hello, timer!\n", (++duty_count) * pulse_period);
    mod_timer(pulse_timer, jiffies + jiffies_pulse_period);
  }
}

static int run_cmd_handler(const char *argv) {
  if (pulse_timer == NULL) {
    pulse_timer = kmalloc(sizeof(struct timer_list), GFP_KERNEL);
    if (!pulse_timer) {
      pr_err("Error: No memory allocated.\n");
      return STATUS_CMD_ERROR_MEMORY;
    }

    timer_setup(pulse_timer, pulse_callback, 0);
  }

  if (duty_timer == NULL) {
    duty_timer = kmalloc(sizeof(struct timer_list), GFP_KERNEL);
    if (!duty_timer) {
      pr_err("Error: No memory allocated.\n");
      return STATUS_CMD_ERROR_MEMORY;
    }

    timer_setup(duty_timer, duty_callback, 0);
  }

  mod_timer(duty_timer, jiffies + msecs_to_jiffies(
                                      SEC_TO_MSEC(MINUTE_TO_SEC(duty_period))));

  jiffies_pulse_period = msecs_to_jiffies(SEC_TO_MSEC(pulse_period));
  mod_timer(pulse_timer, jiffies + jiffies_pulse_period);

  pr_info("run\n");

  cmd_result = 0;
  return STATUS_OK;
}

static int period_cmd_handler(const char *argv) {
  int res;
  int new_value;

  cmd_result = 0;
  if (!argv || strlen(argv) == 0) {
    pr_err("Param error: %s value is empty.\n", "pulse");
    return STATUS_CMD_ERROR_ARG;
  }

  res = kstrtoint(argv, 10, &new_value);
  if (res) {
    pr_err("Param error: %s value is not a decimal number\n", "pulse");
    return STATUS_CMD_ERROR_ARG;
  }

  if (new_value < 0 || new_value > MAX_PULSE) {
    pr_err("Param error: %s out of range (0, %d)\n", "pulse", MAX_PULSE);
    return STATUS_CMD_ERROR_ARG;
  }

  pulse_period = new_value;
  cmd_result = pulse_period;
  pr_info("Set param: %s=%d\n", "pulse", pulse_period);

  return STATUS_OK;
}

static int duty_cmd_handler(const char *argv) {
  int res;
  int new_value;

  cmd_result = 0;
  if (!argv || strlen(argv) == 0) {
    pr_err("Param error: %s value is empty.\n", "duty");
    return STATUS_CMD_ERROR_ARG;
  }

  res = kstrtoint(argv, 10, &new_value);
  if (res) {
    pr_err("Param error: %s value is not a decimal number\n", "duty");
    return STATUS_CMD_ERROR_ARG;
  }

  if (new_value < 0 || new_value > MAX_DUTY) {
    pr_err("Param error: %s out of range (0, %d)\n", "duty", MAX_DUTY);
    return STATUS_CMD_ERROR_ARG;
  }

  duty_period = new_value;
  cmd_result = duty_period;
  pr_info("Set param: %s=%d\n", "duty", duty_period);

  return STATUS_OK;
}

static int stop_cmd_handler(const char *argv) {
  if (duty_timer != NULL) {
    del_timer_sync(duty_timer);
    kfree(duty_timer);
    duty_timer = NULL;
  }

  if (pulse_timer != NULL) {
    del_timer_sync(pulse_timer);
    kfree(pulse_timer);
    pulse_timer = NULL;
  }

  pr_info("stop\n");

  cmd_result = 0;
  return STATUS_OK;
}

static struct command COMMANDS[] = {
    COMMAND(run),
    COMMAND(period),
    COMMAND(duty),
    COMMAND(stop),
};

static int cmd_execute(const char *cmd_str) {
  int cmd_status = STATUS_UNKNOWN_CMD;
  int cmd_len = strlen(cmd_str);

  if (cmd_str == NULL || cmd_len <= 1)
    return cmd_status;

  char cmd[MAX_CMD_STR_LEN + 1] = {0};
  char cmd_args[MAX_CMD_ARG_STR_LEN + 1] = {0};

  // split cmd_str to command and arguments
  char *p_index = memchr(cmd_str, ' ', MAX_CMD_STR_LEN);
  if (p_index) {
    int index = (int)(p_index - cmd_str);
    if (index > 0 && index < MAX_CMD_STR_LEN) {
      index++;
      strlcpy(cmd, cmd_str, index);
      strlcpy(cmd_args, cmd_str + index, cmd_len);
    } else {
      return cmd_status;
    }
  } else {
    strncpy(cmd, cmd_str, cmd_len);
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

static int __init ex_timer_init(void) {
  pr_info("init\n");
  return 0;
}

static void __exit ex_timer_exit(void) {
  if (duty_timer != NULL) {
    del_timer_sync(duty_timer);
    kfree(duty_timer);
    duty_timer = NULL;
  }

  if (pulse_timer != NULL) {
    del_timer_sync(pulse_timer);
    kfree(pulse_timer);
    pulse_timer = NULL;
  }

  pr_info("exit\n");
}

module_init(ex_timer_init);
module_exit(ex_timer_exit);
