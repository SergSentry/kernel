// SPDX-License-Identifier: GPL-2.0-only
/**
 * OTUS course homework 'Linux Kernel Development'
 * Task: HW_03_collection_of_example
 * Module: ex_stack
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

#include "ex_stack.h"

struct item_struct {
	struct list_head list;
	int value;
};

static LIST_HEAD(stack_head);

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

static int is_empty(void)
{
	return list_empty(&stack_head);
}

static int push(int value)
{
	struct item_struct *new_node =
		kmalloc(sizeof(struct item_struct), GFP_KERNEL);

	if (!new_node) {
		pr_err("Error: No memory allocated.\n");
		return STATUS_CMD_ERROR_MEMORY;
	}

	new_node->value = value;
	INIT_LIST_HEAD(&new_node->list);
	list_add(&new_node->list, &stack_head);

	pr_info("Push: %d\n", value);

	return STATUS_OK;
}

static int pop(int *value)
{
	if (is_empty()) {
		pr_err("Error: stack empty\n");
		return STATUS_CMD_ERROR_ARG;
	}

	struct item_struct *node =
		list_first_entry(&stack_head, struct item_struct, list);

	if (node) {
		*value = node->value;
		list_del(&node->list);
		kfree(node);
		pr_info("Pop: %d\n", *value);
	}

	return STATUS_OK;
}

static int top(int *value)
{
	if (is_empty()) {
		pr_err("Error: stack empty\n");
		return STATUS_CMD_ERROR_ARG;
	}

	struct item_struct *node =
		list_first_entry(&stack_head, struct item_struct, list);

	if (node) {
		*value = node->value;
		pr_info("Top: %d\n", *value);
	}

	return STATUS_OK;
}

static void free_stack(struct list_head *head)
{
	if (head && !list_empty(head)) {
		struct item_struct *node, *tmp;

		list_for_each_entry_safe(node, tmp, head, list) {
			list_del(&node->list);
			kfree(node);
		}

		pr_info("clear\n");
	}
}

static int push_cmd_handler(const char *argv)
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
	cmd_status = push(value);
	if (cmd_status == STATUS_OK) {
		cmd_result = value;
	}

	return cmd_status;
}

static int pop_cmd_handler(const char *argv)
{
	cmd_status = pop(&cmd_result);
	return cmd_status;
}

static int is_empty_cmd_handler(const char *argv)
{
	cmd_result = is_empty();

	return STATUS_OK;
}

static int top_cmd_handler(const char *argv)
{
	cmd_status = top(&cmd_result);
	return cmd_status;
}

static int bracket_cmd_handler(const char *argv)
{
	if (!argv || strlen(argv) == 0) {
		cmd_result = 0;
		return STATUS_OK;
	}

	cmd_result = 0;
	for (size_t i = 0; i < strlen(argv); i++) {
	    int currentChar = argv[i];
	    if (currentChar == '(' || currentChar == '[' || currentChar == '{') {
	        push(currentChar);
	    } else if (currentChar == ')' || currentChar == ']' || currentChar == '}') {
	        if (is_empty()) {
	            cmd_result = 1;
				break;
	        }

	        int topElement;
	        pop(&topElement);
	        if ((currentChar == ')' && topElement != '(')
	         || (currentChar == ']' && topElement != '[')
	         || (currentChar == '}' && topElement != '{')) {
	            cmd_result = 1;
	        	break;
	        }
	    }
	}

    if (!cmd_result) {
		 cmd_result = is_empty() ? 0 : 1;
	}

	free_stack(&stack_head);
	
	return STATUS_OK;
}

static int size_cmd_handler(const char *argv)
{
	unsigned int count = 0;
	struct list_head *pos;

	list_for_each(pos, &stack_head) {
		count++;
	}

	cmd_result = count;
	
	pr_info("Size: %d\n", count);
	return STATUS_OK;
}

static int clear_cmd_handler(const char *argv)
{
	free_stack(&stack_head);

	cmd_result = 0;
	return STATUS_OK;
}

static int print_cmd_handler(const char *argv)
{
	struct item_struct *node;

	pr_info("Values: ");
	list_for_each_entry(node, &stack_head, list) {
		pr_cont("%d ", node->value);
	}
	pr_cont("\n");

	cmd_result = 0;
	return STATUS_OK;
}

static struct command COMMANDS[] = {
	COMMAND(push),
	COMMAND(pop),
	COMMAND(is_empty),
	COMMAND(top),
	COMMAND(size),
	COMMAND(clear),
	COMMAND(bracket),
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

static int __init ex_stack_init(void)
{
	pr_info("init\n");
	return 0;
}

static void __exit ex_stack_exit(void)
{
	free_stack(&stack_head);
	pr_info("exit\n");
}

module_init(ex_stack_init);
module_exit(ex_stack_exit);
