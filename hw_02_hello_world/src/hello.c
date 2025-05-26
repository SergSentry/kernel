// SPDX-License-Identifier: GPL-2.0-only
/**
 * OTUS course homework 'Linux Kernel Development'
 * Task: HW_02_hello_world
 * 
 * Copyright (c) 2007-2025 SergSentry
 */

#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/stat.h>
#include <linux/types.h>

#include <linux/string.h>

#include "hello.h"

static bool isdigit_dummy(int ch);

static bool islower_dummy(int ch);

static bool isupper_dummy(int ch);

static bool isaplha_dummy(int ch);

static bool isalnum_dummy(int ch);

static bool ispunct_dummy(int ch);

static bool isspace_dummy(int ch);

static bool isprint_dummy(int ch);

static void dummy_executer(void);

#define CHAR_BUFFER_SIZE 16

static char my_str[CHAR_BUFFER_SIZE + 1] = { 0 };
module_param_string(my_str, my_str, CHAR_BUFFER_SIZE, 0644);
MODULE_PARM_DESC(my_str, "Dummy string");

static ushort idx = 0;

/**
 * param_set_idx_handler - callback for set idx param
 */
static int param_set_idx_handler(const char *val, const struct kernel_param *kp)
{
	int res;
	int new_value;

	if (!val || strlen(val) == 0) {
		pr_err("Param error: %s value is empty.\n", kp->name);
		return -EINVAL;
	}

	res = kstrtoint(val, 10, &new_value);
	if (res) {
		pr_err("Param error: %s value is not a decimal number\n",
		       kp->name);
		return res;
	}

	if (new_value < 0 || new_value > CHAR_BUFFER_SIZE) {
		pr_err("Param error: %s out of range (0, %d)\n", kp->name,
		       CHAR_BUFFER_SIZE);
		return -EINVAL;
	}

	*((ushort *)kp->arg) = new_value;
	pr_info("Set param: %s=%d\n", kp->name, new_value);
	return 0;
}

static const struct kernel_param_ops idx_ops = {
	.set = param_set_idx_handler,
	.get = param_get_short,
};

module_param_cb(idx, &idx_ops, &idx,
		S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH);
MODULE_PARM_DESC(idx, "Index of dummy string position");

static char ch_val = ' ';

/**
 * param_set_ch_val_handler - callback for set ch_val param
 */
static int param_set_ch_val_handler(const char *val,
				    const struct kernel_param *kp)
{
	if (!val || strlen(val) == 0) {
		pr_err("Param error: %s value is empty.\n", kp->name);
		return -EINVAL;
	}

	char ch = val[0];

	if (!isprint_dummy(ch)) {
		pr_err("Param error: %s value is not ascii printable symbol '%c'\n",
		       kp->name, ch);
		return -EINVAL;
	}

	*((char *)kp->arg) = ch;
	pr_info("Set param: %s=%c\n", kp->name, ch);

	// Execute main dummy function
	dummy_executer();

	return 0;
}

static int param_get_ch_val_handler(char *buffer, const struct kernel_param *kp)
{
	int result = 0;
	result = sprintf(buffer, "%c\n", *((char *)kp->arg));
	return result;
}

static const struct kernel_param_ops ch_val_ops = {
	.set = param_set_ch_val_handler,
	.get = param_get_ch_val_handler,
};

module_param_cb(ch_val, &ch_val_ops, &ch_val,
		S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH);
MODULE_PARM_DESC(
	ch_val,
	"The character for writing to the idx(index) position of the dummy string");

/**
 * dummy_executer - execute main function of this module
 */
static void dummy_executer(void)
{
	if (idx < CHAR_BUFFER_SIZE) {
		my_str[idx] = ch_val;
		pr_info("Update my_str param: %s\n", my_str);
	}
}

static int __init dummy_init(void)
{
	pr_info("init\n");
	return 0;
}

static void __exit dummy_exit(void)
{
	pr_info("exit\n");
}

module_init(dummy_init);
module_exit(dummy_exit);

static bool isdigit_dummy(int ch)
{
	static char *lower_alpha = "0123456789";
	return strchr(lower_alpha, ch) != NULL;
}

static bool islower_dummy(int ch)
{
	static char *lower_alpha = "abcdefghijklmnopqrstuvwxyz";
	return strchr(lower_alpha, ch) != NULL;
}

static bool isupper_dummy(int ch)
{
	static char *pattern = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
	return strchr(pattern, ch) != NULL;
}

static bool isaplha_dummy(int ch)
{
	return islower_dummy(ch) || isupper_dummy(ch);
}

static bool isalnum_dummy(int ch)
{
	return isaplha_dummy(ch) || isdigit_dummy(ch);
}

static bool ispunct_dummy(int ch)
{
	static char *pattern = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~";
	return strchr(pattern, ch) != NULL;
}

static bool isspace_dummy(int ch)
{
	static char *pattern = "\f\n\r\t\v ";
	return strchr(pattern, ch) != NULL;
}

static bool isprint_dummy(int ch)
{
	return isalnum_dummy(ch) || ispunct_dummy(ch) || isspace_dummy(ch);
}
