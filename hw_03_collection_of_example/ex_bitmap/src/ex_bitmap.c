// SPDX-License-Identifier: GPL-2.0-only
/**
 * OTUS course homework 'Linux Kernel Development'
 * Task: HW_03_collection_of_example
 * Module: ex_bitmap
 * 
 * Copyright (c) 2007-2025 SergSentry
 */

#define pr_fmt(fmt) "%s [%s]: " fmt, KBUILD_MODNAME, __func__

#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>

#include <linux/slab.h>
#include <linux/string.h>
#include <linux/bitmap.h>

#include "ex_bitmap.h"

unsigned long bit_map[BITS_TO_LONGS(BITMAP_SIZE)];

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

static int set_cmd_handler(const char *argv)
{
	if (!argv || strlen(argv) == 0) {
		pr_err("Param error: set bit is empty.\n");
		return STATUS_CMD_ERROR_ARG;
	}

	int value = 0;
	int res = kstrtoint(argv, 10, &value);
	if (res) {
		pr_err("Param error: set bit is not a decimal number\n");
		return STATUS_CMD_ERROR_ARG;
	}

	if (value >= BITMAP_SIZE) {
		pr_err("Param error: out range bit set number\n");
		return STATUS_CMD_ERROR_ARG;
	}

	cmd_result = 0;
	set_bit(value, bit_map);
	cmd_result = value;
	pr_info("Set: %d\n", value);
	return STATUS_OK;
}

static int check_cmd_handler(const char *argv)
{
	if (!argv || strlen(argv) == 0) {
		pr_err("Param error: check bit is empty.\n");
		return STATUS_CMD_ERROR_ARG;
	}

	int value = 0;
	int res = kstrtoint(argv, 10, &value);
	if (res) {
		pr_err("Param error: check bit is not a decimal number\n");
		return STATUS_CMD_ERROR_ARG;
	}

	if (value >= BITMAP_SIZE) {
		pr_err("Param error: out range bit check number\n");
		return STATUS_CMD_ERROR_ARG;
	}

	cmd_result = test_bit(value, bit_map) ? 1 : 0;
	pr_info("Check: %d, result %d\n", value, cmd_result);

	return STATUS_OK;
}

static int clear_cmd_handler(const char *argv)
{
	if (!argv || strlen(argv) == 0) {
		pr_err("Param error: clear bit is empty.\n");
		return STATUS_CMD_ERROR_ARG;
	}

	int value = 0;
	int res = kstrtoint(argv, 10, &value);
	if (res) {
		pr_err("Param error: clear bit is not a decimal number\n");
		return STATUS_CMD_ERROR_ARG;
	}

	if (value >= BITMAP_SIZE) {
		pr_err("Param error: out range bit clear number\n");
		return STATUS_CMD_ERROR_ARG;
	}

	cmd_result = 0;
	clear_bit(value, bit_map);
	pr_info("Clear: %d\n", value);

	return STATUS_OK;
}

static int search_cmd_handler(const char *argv)
{
	cmd_result = -1;

	int idx = find_first_zero_bit(bit_map, BITMAP_SIZE);
	if (idx != BITMAP_SIZE) {
		set_bit(idx, bit_map);
		cmd_result = idx;
		pr_info("Find resource: %d\n", idx);
		return STATUS_OK;
	}

	pr_info("No found resource.\n");
	return STATUS_OK;
}

static ssize_t ulong_to_hex_string(unsigned long num, char *buf, size_t size)
{
	static const char hexdigits[] = "0123456789abcdef";
	ssize_t len = 0;

	if (!size || !buf)
		return -EINVAL;

	if (num == 0) {
		if (size <= 1)
			return -ENOSPC;
		buf[len++] = '0';
		buf[len] = '\0';
		return len;
	}

	int pos = 0;
	do {
		buf[pos++] = hexdigits[num & 0xf];
		num >>= 4;
	} while (num && pos < size - 1);

	if (pos >= size - 1) {
		return -ENOSPC;
	}

	for (int left = 0, right = pos - 1; left < right; left++, right--) {
		char tmp = buf[left];
		buf[left] = buf[right];
		buf[right] = tmp;
	}

	len = pos;
	buf[len] = '\0';
	return len;
}

static int print_cmd_handler(const char *argv)
{
	cmd_result = 0;
	char buf[MAX_CMD_ARG_STR_LEN + 1] = { 0 };

	pr_info("Values: ");
	for (int i = 0; i < BITS_TO_LONGS(BITMAP_SIZE); i++) {
		ssize_t ret = ulong_to_hex_string(bit_map[i], buf,
						  MAX_CMD_ARG_STR_LEN);
		if (ret) {
			pr_cont("%s ", buf);
		}
	}

	pr_cont("\n");

	return STATUS_OK;
}

static struct command COMMANDS[] = {
	COMMAND(set),
	COMMAND(check),
	COMMAND(clear),
	COMMAND(search),
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

static int __init ex_bitmap_init(void)
{
	memset(bit_map, 0, sizeof(bit_map));
	pr_info("init\n");
	return 0;
}

static void __exit ex_bitmap_exit(void)
{
	pr_info("exit\n");
}

module_init(ex_bitmap_init);
module_exit(ex_bitmap_exit);
