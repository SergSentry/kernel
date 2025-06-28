// SPDX-License-Identifier: GPL-2.0-only
/**
 * OTUS course homework 'Linux Kernel Development'
 * Task: HW_03_collection_of_example
 * Module: ex_bin_search
 * 
 * Copyright (c) 2007-2025 SergSentry
 */

#define pr_fmt(fmt) "%s [%s]: " fmt, KBUILD_MODNAME, __func__

#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>

#include <linux/slab.h>
#include <linux/string.h>
#include <linux/bsearch.h>
#include <linux/sort.h>

#include "ex_bin_search.h"

struct item_struct {
	int w_index;
	int size;
	int* data;
};

static struct item_struct data_item;

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

static int init_data_item(struct item_struct *data_item, int size) {
	int *data =	kmalloc(sizeof(int), GFP_KERNEL);

	if (!data) {
		pr_err("Error: No memory allocated.\n");
		return STATUS_CMD_ERROR_MEMORY;
	}

    data_item->w_index = 0;
	data_item->size = size;
	data_item->data = data;

	return STATUS_OK;
}

static int add(int value)
{
	if (data_item.w_index + 1 >= data_item.size)
		data_item.w_index = 0;

	data_item.data[data_item.w_index] = value;

	pr_info("Add index: %d value: %d\n", data_item.w_index,  data_item.data[data_item.w_index]);

	data_item.w_index += 1;
	
	return STATUS_OK;
}

static void free_data_item(struct item_struct *data_item)
{
	if (data_item != NULL && data_item->data != NULL) {
		kfree(data_item->data);
	}
}

static int add_cmd_handler(const char *argv)
{
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

	cmd_result = 0;
	cmd_status = add(value);
	if (cmd_status == STATUS_OK) {
		cmd_result = value;
	}

	return cmd_status;
}

static int int_data_cmp(const void *a, const void *b)
{
	int *data_a = (int *)a;
	int *data_b = (int *)b;
	return (int)(*data_a - *data_b);
}

static void int_data_swap(void *a, void *b, int size)
{
	int *data_a = (int *)a;
	int *data_b = (int *)b;

	int tmp = *data_b;
	*data_b = *data_a;
	*data_a = tmp;
}

static int sort_cmd_handler(const char *argv)
{
	cmd_result = 0;
	sort((void *)data_item.data, data_item.w_index, sizeof(int), int_data_cmp,  int_data_swap);

	return STATUS_OK;
}

static int search_cmd_handler(const char *argv)
{
	if (!argv || strlen(argv) == 0) {
		pr_err("Param error: search value is empty.\n");
		return STATUS_CMD_ERROR_ARG;
	}

	int value = 0;
	int res = kstrtoint(argv, 10, &value);
	if (res) {
		pr_err("Param error: search value is not a decimal number\n");
		return STATUS_CMD_ERROR_ARG;
	}

	int *result = NULL;
	result = bsearch(&value, (void *)data_item.data, data_item.w_index, sizeof(int), int_data_cmp);

    cmd_result = result != NULL ? value: 0;

	return STATUS_OK;
}

static int print_cmd_handler(const char *argv)
{
	pr_info("Values: ");
	for (int i = 0; i < data_item.w_index; i++) {
		pr_cont("%d ", data_item.data[i]);
	}
	
	pr_cont("\n");
	cmd_result = 0;
	return STATUS_OK;
}

static struct command COMMANDS[] = {
	COMMAND(add),
	COMMAND(sort),
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

static int __init ex_bin_search_init(void)
{
	cmd_status = init_data_item(&data_item, MAX_DATA_ITEM_SIZE);
	pr_info("init\n");
	return 0;
}

static void __exit ex_bin_search_exit(void)
{
	free_data_item(&data_item);
	pr_info("exit\n");
}

module_init(ex_bin_search_init);
module_exit(ex_bin_search_exit);
