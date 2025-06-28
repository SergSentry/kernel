// SPDX-License-Identifier: GPL-2.0-only
/**
 * OTUS course homework 'Linux Kernel Development'
 * Task: HW_03_collection_of_example
 * Module: ex_hash
 * 
 * Copyright (c) 2007-2025 SergSentry
 */

#ifndef EX_HASH_H
#define EX_HASH_H

#define HASH_TABLE_SIZE (8)
#define USER_NAME_SIZE (50)

#define MAX_CMD_STR_LEN (10)
#define MAX_CMD_ARG_STR_LEN (50)
#define MAX_CMD_PARAM_LEN ((MAX_CMD_STR_LEN) + (MAX_CMD_ARG_STR_LEN))

#define STATUS_NONE (-EINVAL)
#define STATUS_UNKNOWN_CMD (-EINVAL)
#define STATUS_OK (0)
#define STATUS_CMD_ERROR_ARG (-EINVAL)
#define STATUS_CMD_ERROR_MEMORY (-ENOMEM)

#define COMMAND(NAME) { #NAME, NAME##_cmd_handler }

struct command {
	char *name;
	int (*handle)(const char *argv);
};

MODULE_DESCRIPTION("OTUS course homework 'Linux Kernel Development'\n\t\tTask: "
		   "HW_03_collection_of_example\n\t\tModule: ex_hash");

MODULE_AUTHOR("SergSentry");
MODULE_LICENSE("GPL");
MODULE_VERSION("0.1");

#endif
