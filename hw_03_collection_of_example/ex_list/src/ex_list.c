// SPDX-License-Identifier: GPL-2.0-only
/**
 * OTUS course homework 'Linux Kernel Development'
 * Task: HW_03_collection_of_example
 * Module: ex_list
 * 
 * Copyright (c) 2007-2025 SergSentry
 */

#define pr_fmt(fmt) "%s [%s]: " fmt, KBUILD_MODNAME, __func__

#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>

#include <linux/slab.h>
#include <linux/string.h>
#include <linux/list.h>

#include "ex_list.h"

struct item_struct {
	struct list_head list;
	int value;
};

static LIST_HEAD(list_head);

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

static int add(int value)
{
	struct item_struct *new_node =
		kmalloc(sizeof(struct item_struct), GFP_KERNEL);

	if (!new_node) {
		pr_err("Error: No memory allocated.\n");
		return STATUS_CMD_ERROR_MEMORY;
	}

	new_node->value = value;
	INIT_LIST_HEAD(&new_node->list);
	list_add(&new_node->list, &list_head);

	pr_info("Add value: %d\n", value);

	return STATUS_OK;
}

static int add_to_tail(int value)
{
	struct item_struct *new_node =
		kmalloc(sizeof(struct item_struct), GFP_KERNEL);

	if (!new_node) {
		pr_err("Error: No memory allocated.\n");
		return STATUS_CMD_ERROR_MEMORY;
	}

	new_node->value = value;
	INIT_LIST_HEAD(&new_node->list);
	list_add_tail(&new_node->list, &list_head);

	pr_info("Add value: %d\n", value);

	return STATUS_OK;
}

static int add_and_sort(int value)
{
	struct item_struct *new_node =
		kmalloc(sizeof(struct item_struct), GFP_KERNEL);

	if (!new_node) {
		pr_err("Error: No memory allocated.\n");
		return STATUS_CMD_ERROR_MEMORY;
	}

	struct list_head *ptr;
	struct item_struct *entry;

	new_node->value = value;

	for (ptr = list_head.next; ptr != &list_head; ptr = ptr->next) {
		entry = list_entry(ptr, struct item_struct, list);
		if (entry->value < new_node->value) {
			list_add_tail(&new_node->list, ptr);

			pr_info("Add value: %d\n", value);
			return STATUS_OK;
		}
	}

	list_add_tail(&new_node->list, &list_head);

	pr_info("Add value: %d\n", value);
	return STATUS_OK;
}

static int remove_from_list(int value)
{
	struct item_struct *node, *tmp;

	list_for_each_entry_safe(node, tmp, &list_head, list) {
		if (node->value == value) {
			list_del(&node->list);
			kfree(node);

			pr_info("Remove value: %d\n", value);
			break;
		}
	}

	return STATUS_OK;
}

static void free_list(struct list_head *head)
{
	struct item_struct *node, *tmp;

	list_for_each_entry_safe(node, tmp, &list_head, list) {
		list_del(&node->list);
		kfree(node);
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

static int tadd_cmd_handler(const char *argv)
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
	cmd_status = add_to_tail(value);
	if (cmd_status == STATUS_OK) {
		cmd_result = value;
	}

	return cmd_status;
}

static int sadd_cmd_handler(const char *argv)
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
	cmd_status = add_and_sort(value);
	if (cmd_status == STATUS_OK) {
		cmd_result = value;
	}

	return cmd_status;
}

static int del_cmd_handler(const char *argv)
{
	if (!argv || strlen(argv) == 0) {
		pr_err("Param error: del value is empty.\n");
		return STATUS_CMD_ERROR_ARG;
	}

	int value = 0;
	int res = kstrtoint(argv, 10, &value);
	if (res) {
		pr_err("Param error: del value is not a decimal number\n");
		return STATUS_CMD_ERROR_ARG;
	}

	cmd_result = 0;
	cmd_status = remove_from_list(value);
	if (cmd_status == STATUS_OK) {
		cmd_result = value;
	}

	return cmd_status;
}

static int is_empty_cmd_handler(const char *argv)
{
	cmd_result = list_empty(&list_head);

	return STATUS_OK;
}

static int size_cmd_handler(const char *argv)
{
	unsigned int count = 0;
	struct list_head *pos;

	list_for_each(pos, &list_head) {
		count++;
	}

	cmd_result = count;

	return STATUS_OK;
}

static int next_cmd_handler(const char *argv)
{
	static struct item_struct *current_item = NULL;
	if (list_empty(&list_head)) {
		cmd_result = 0;
		return STATUS_CMD_ERROR_ARG;
	}

	if (current_item == NULL) {
		current_item =
			list_first_entry(&list_head, struct item_struct, list);
	} else {
		struct item_struct *next = list_next_entry(current_item, list);

		// for cycle travers next cmd
		if (list_entry_is_head(next, &list_head, list)) {
			current_item = list_first_entry(
				&list_head, struct item_struct, list);
		} else {
			current_item = next;
		}
	}

	cmd_result = current_item->value;
	return STATUS_OK;
}

static int prev_cmd_handler(const char *argv)
{
	static struct item_struct *current_item = NULL;
	if (list_empty(&list_head)) {
		cmd_result = 0;
		return STATUS_CMD_ERROR_ARG;
	}

	if (current_item == NULL) {
		current_item =
			list_first_entry(&list_head, struct item_struct, list);
	} else {
		struct item_struct *prev = list_prev_entry(current_item, list);

		// for cycle travers prev cmd
		if (list_entry_is_head(prev, &list_head, list)) {
			current_item = list_last_entry(
				&list_head, struct item_struct, list);
		} else {
			current_item = prev;
		}
	}

	cmd_result = current_item->value;
	return STATUS_OK;
}

static int clear_cmd_handler(const char *argv)
{
	free_list(&list_head);

	cmd_result = 0;
	return STATUS_OK;
}

static int print_cmd_handler(const char *argv)
{
	struct item_struct *node;

	pr_info("Values: ");
	list_for_each_entry(node, &list_head, list) {
		pr_cont("%d ", node->value);
	}
	pr_cont("\n");

	cmd_result = 0;
	return STATUS_OK;
}

static struct command COMMANDS[] = {
	COMMAND(add),
	COMMAND(tadd),
	COMMAND(sadd),
	COMMAND(del),
	COMMAND(is_empty),
	COMMAND(print),
	COMMAND(size),
	COMMAND(next),
	COMMAND(prev),
	COMMAND(clear),
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

static int __init ex_list_init(void)
{
	pr_info("init\n");
	return 0;
}

static void __exit ex_list_exit(void)
{
	free_list(&list_head);
	pr_info("exit\n");
}

module_init(ex_list_init);
module_exit(ex_list_exit);
