// SPDX-License-Identifier: GPL-2.0-only
/**
 * OTUS course homework 'Linux Kernel Development'
 * Task: HW_03_collection_of_example
 * Module: ex_hash
 * 
 * Copyright (c) 2007-2025 SergSentry
 */

#define pr_fmt(fmt) "%s [%s]: " fmt, KBUILD_MODNAME, __func__

#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>

#include <linux/slab.h>
#include <linux/string.h>
#include <linux/types.h>
#include <linux/jhash.h>
#include <linux/hashtable.h>

#include "ex_hash.h"

struct user_record {
    u32 uid;                 
    char username[USER_NAME_SIZE + 1];          
    struct hlist_node node;     
};

static DEFINE_HASHTABLE(htable, HASH_TABLE_SIZE);

static u32 hash_function(const char *key) {
    return jhash(key, strlen(key), 0xdeadbeef);
}

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

static struct user_record *find_by_name(const char *username) {
    u32 hash_idx = hash_function(username);
        struct user_record *rec;

    hash_for_each_possible(htable, rec, node, hash_idx) {
        if (!strcmp(rec->username, username))
            return rec;
    }

    return NULL;
}

static int add(const char *username) {
    struct user_record *record;
    
	record = find_by_name(username);
	if (record != NULL) {
		pr_err("Error: dublicate record.\n");
		return STATUS_CMD_ERROR_ARG;
	}

    record = kmalloc(sizeof(*record), GFP_KERNEL);
    if (!record) {
		pr_err("Error: No memory allocated.\n");
		return STATUS_CMD_ERROR_MEMORY;
    }

    strlcpy(record->username, username, USER_NAME_SIZE);
    u32 hash_idx = hash_function(username);
    record->uid = hash_idx;
    hash_add(htable, &record->node, record->uid);

	pr_info("Add Username: %s, ID: %d\n", record->username, record->uid);
    return STATUS_OK;
}

static int del(const char *username) {
    struct user_record *record;
    u32 hash_idx = hash_function(username);

    hash_for_each_possible(htable, record, node, hash_idx) {
        if (strcmp(record->username, username) == 0) {
            hash_del(&record->node);
            kfree(record);

            pr_info("Del Username: %s, ID: %d\n", record->username, record->uid);
            return STATUS_OK;
        }
    };

    return STATUS_NONE;
}

static int add_cmd_handler(const char *argv)
{
	if (!argv || strlen(argv) == 0) {
		pr_err("Param error: add value is empty.\n");
		return STATUS_CMD_ERROR_ARG;
	}

	cmd_result = 0;
	cmd_status = add(argv);
	if (cmd_status == STATUS_OK) {
		cmd_result = 1;
	}

	return cmd_status;
}

static int del_cmd_handler(const char *argv)
{
	if (!argv || strlen(argv) == 0) {
		pr_err("Param error: del value is empty.\n");
		return STATUS_CMD_ERROR_ARG;
	}

	cmd_status = del(argv);
	return cmd_status;
}

static int search_cmd_handler(const char *argv)
{
	if (!argv || strlen(argv) == 0) {
		pr_err("Param error: find value is empty.\n");
		return STATUS_CMD_ERROR_ARG;
	}

	struct user_record *item = find_by_name(argv);
	if (item != NULL) {
		cmd_result = 1;
		pr_info("Find Username: %s, ID: %d\n", item->username, item->uid);
	} else {
		cmd_result = 0;
		pr_info("No found: %s\n", argv);
	}

	return STATUS_OK;
}

static int print_cmd_handler(const char *argv)
{
	struct user_record *record;
    int i;

    hash_for_each(htable, i, record, node) {
        pr_info("Username: %s, ID: %d\n", record->username, record->uid);
    };

	cmd_result = 0;
	return STATUS_OK;
}

static void free_table(void) {
	struct user_record *record;
	struct hlist_node *tmp;
    int i;

    hash_for_each_safe(htable, i, tmp, record, node) {
        hash_del(&record->node);
        kfree(record);
    };
}

static struct command COMMANDS[] = {
	COMMAND(add),
	COMMAND(del),
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

static int __init ex_hash_init(void)
{
	pr_info("init\n");
	return 0;
}

static void __exit ex_hash_exit(void)
{
	free_table();
	pr_info("exit\n");
}

module_init(ex_hash_init);
module_exit(ex_hash_exit);
