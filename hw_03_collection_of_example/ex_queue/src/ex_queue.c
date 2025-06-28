// SPDX-License-Identifier: GPL-2.0-only
/**
 * OTUS course homework 'Linux Kernel Development'
 * Task: HW_03_collection_of_example
 * Module: ex_queue
 * 
 * Copyright (c) 2007-2025 SergSentry
 */

#define pr_fmt(fmt) "%s [%s]: " fmt, KBUILD_MODNAME, __func__

#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>

#include <linux/string.h>
#include <linux/kfifo.h>

#include "ex_queue.h"

static struct kfifo queue;

static int cmd_execute(const char *cmd_str);

static int cmd_result = 0;
module_param(cmd_result, int, 0640);
MODULE_PARM_DESC(cmd_result, "A command result param");

static int cmd_status = STATUS_NONE;
module_param(cmd_status, int, 0640);
MODULE_PARM_DESC(cmd_status, "A command status param");

static char cmd_param[MAX_CMD_PARAM_LEN + 1];
static int set_cmd_param(const char *val, const struct kernel_param *kp)
{
	if (!val || strlen(val) <= 1) {
		return STATUS_CMD_ERROR_ARG;
	}

	strlcpy(cmd_param, val, MAX_CMD_PARAM_LEN);
	cmd_status = cmd_execute(cmd_param);
	return cmd_status;
}

struct kernel_param_ops param_ops_cmd_param = { .set = set_cmd_param };
module_param_cb(cmd_param, &param_ops_cmd_param, &cmd_param, 0640);
MODULE_PARM_DESC(cmd_param, "A command line param");

static int push_cmd_handler(const char *argv)
{
	cmd_result = 0;

	if (!argv || strlen(argv) == 0) {
		pr_err("Param error: add value is empty.\n");
		return STATUS_CMD_ERROR_ARG;
	}

	int value = 0;
	int res = kstrtoint(argv, 10, &value);
	if (res) {
		pr_err("Param error: add value is not a decimal number\n");
		return STATUS_CMD_ERROR_ARG;
	}

	if (kfifo_put(&queue, value)) {
		cmd_result = value;
		pr_info("Push: %d\n", value);
		return STATUS_OK;
	}

	return STATUS_NONE;
}

static int pop_cmd_handler(const char *argv)
{
	cmd_result = 0;

	int value = 0;
	if (kfifo_get(&queue, &value)) {
		cmd_result = value;
		pr_debug("Pop: %d\n", value);
		return STATUS_OK;
	}

	return STATUS_NONE;
}

static int avail_cmd_handler(const char *argv)
{
	cmd_result = kfifo_avail(&queue);
	return STATUS_OK;
}

static int is_full_cmd_handler(const char *argv)
{
	cmd_result = kfifo_is_full(&queue);
	return STATUS_OK;
}

static int is_empty_cmd_handler(const char *argv)
{
	cmd_result = kfifo_is_empty(&queue);
	return STATUS_OK;
}

static int size_cmd_handler(const char *argv)
{
	cmd_result = kfifo_size(&queue);
	return STATUS_OK;
}

static int peek_cmd_handler(const char *argv)
{
	cmd_result = 0;

	int value = 0;
	if (kfifo_peek(&queue, &value)) {
		cmd_result = value;
		pr_debug("Peek: %d\n", value);
		return STATUS_OK;
	}

	return STATUS_NONE;
}

static int print_cmd_handler(const char *argv)
{
	int value;

	pr_info("Values: ");
	while (kfifo_avail(&queue)) {
		if (kfifo_get(&queue, &value)) {
			pr_cont("%d ", value);
		}
	}
	pr_cont("\n");
	
	cmd_result = 0;
	return STATUS_OK;
}

static struct command COMMANDS[] = {
	COMMAND(pop),
	COMMAND(push),
	COMMAND(avail),
	COMMAND(peek),
	COMMAND(is_empty),
	COMMAND(is_full),
	COMMAND(size),
	COMMAND(print),
};

static int cmd_execute(const char *cmd_str)
{
	int cmd_status = STATUS_UNKNOWN_CMD;
	if (cmd_str == NULL || strlen(cmd_str) <= 1)
		return cmd_status;

	char cmd[MAX_CMD_STR_LEN + 1] = { 0 };
	char cmd_args[MAX_CMD_ARG_STR_LEN + 1] = { 0 };

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

static int __init ex_queue_init(void)
{
	int ret = kfifo_alloc(&queue, KFIFO_SIZE, GFP_KERNEL);
	if (ret)
		return ret;

	pr_info("init\n");
	return 0;
}

static void __exit ex_queue_exit(void)
{
	kfifo_free(&queue);
	pr_info("exit\n");
}

module_init(ex_queue_init);
module_exit(ex_queue_exit);
