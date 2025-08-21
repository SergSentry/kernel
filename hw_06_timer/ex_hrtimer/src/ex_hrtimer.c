// SPDX-License-Identifier: GPL-2.0-only
/**
 * OTUS course homework 'Linux Kernel Development'
 * Task: hw_06_timer
 * Module: ex_hrtimer
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

#include "ex_hrtimer.h"

static struct hrtimer *pulse_timer = NULL;
static struct hrtimer *duty_timer = NULL;

static int pulse_period = 30; // per sec
static int duty_period = 5;   // per min
static int duty_count = 0;

static ktime_t pulse_timer_time;
static ktime_t duty_timer_time;

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

static enum hrtimer_restart duty_callback(struct hrtimer *timer) {
  if (pulse_timer != NULL) {
    hrtimer_cancel(pulse_timer);
    kfree(pulse_timer);
    pulse_timer = NULL;
  }

  return HRTIMER_NORESTART;
}

static enum hrtimer_restart pulse_callback(struct hrtimer *timer) {
  if (timer != NULL) {
    hrtimer_forward_now(timer, pulse_timer_time);

    pr_info("min=%d: Hello, timer!\n", (++duty_count) * pulse_period);
    return HRTIMER_RESTART;
  }

  return HRTIMER_NORESTART;
}

static int run_cmd_handler(const char *argv) {
  if (pulse_timer == NULL) {
    pulse_timer = kmalloc(sizeof(struct hrtimer), GFP_KERNEL);
    if (!pulse_timer) {
      pr_err("Error: No memory allocated.\n");
      return STATUS_CMD_ERROR_MEMORY;
    }

    hrtimer_init(pulse_timer, CLOCK_MONOTONIC, HRTIMER_MODE_REL);
    pulse_timer->function = &pulse_callback;
  }

  if (duty_timer == NULL) {
    duty_timer = kmalloc(sizeof(struct hrtimer), GFP_KERNEL);
    if (!duty_timer) {
      pr_err("Error: No memory allocated.\n");
      return STATUS_CMD_ERROR_MEMORY;
    }

    hrtimer_init(duty_timer, CLOCK_MONOTONIC, HRTIMER_MODE_REL);
    duty_timer->function = &duty_callback;
  }

  duty_timer_time = ktime_set(MINUTE_TO_SEC(duty_period), 0);
  hrtimer_start(duty_timer, duty_timer_time, HRTIMER_MODE_REL);

  pulse_timer_time = ktime_set(pulse_period, 0);
  hrtimer_start(pulse_timer, pulse_timer_time, HRTIMER_MODE_REL);

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
    hrtimer_cancel(duty_timer);
    kfree(duty_timer);
    duty_timer = NULL;
  }

  if (pulse_timer != NULL) {
    hrtimer_cancel(pulse_timer);
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

static int __init ex_hrtimer_init(void) {
  pr_info("init\n");
  return 0;
}

static void __exit ex_hrtimer_exit(void) {
  if (duty_timer != NULL) {
    hrtimer_cancel(duty_timer);
    kfree(duty_timer);
    duty_timer = NULL;
  }

  if (pulse_timer != NULL) {
    hrtimer_cancel(pulse_timer);
    kfree(pulse_timer);
    pulse_timer = NULL;
  }

  pr_info("exit\n");
}

module_init(ex_hrtimer_init);
module_exit(ex_hrtimer_exit);
