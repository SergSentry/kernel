// SPDX-License-Identifier: GPL-2.0-only
/**
 * OTUS course homework 'Linux Kernel Development'
 * Task: HW_03_collection_of_example
 * Module: ex_rb_tree
 *
 * Copyright (c) 2007-2025 SergSentry
 */

#define pr_fmt(fmt) "%s [%s]: " fmt, KBUILD_MODNAME, __func__

#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>

#include <linux/rbtree.h>
#include <linux/slab.h>
#include <linux/string.h>

#include "ex_rb_tree.h"

struct tree_node {
  int key;
  struct rb_node node;
};

static struct rb_root root = RB_ROOT;

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

static void free_rb_tree(void) {
  struct tree_node *entry, *tmp;

  rbtree_postorder_for_each_entry_safe(entry, tmp, &root, node) {
    rb_erase(&entry->node, &root);
    kfree(entry);
  }
}

static struct tree_node *find_node(int key) {
  struct rb_node *iter;

  iter = root.rb_node;
  while (iter) {
    struct tree_node *this = rb_entry(iter, struct tree_node, node);

    if (key < this->key)
      iter = iter->rb_left;
    else if (key > this->key)
      iter = iter->rb_right;
    else
      return this;
  }
  return NULL;
}

static int insert_node(int key) {
  struct tree_node *new_node = kmalloc(sizeof(struct tree_node), GFP_KERNEL);
  if (!new_node) {
    pr_err("Error: No memory allocated.\n");
    return STATUS_CMD_ERROR_MEMORY;
  }

  new_node->key = key;

  struct rb_node **pos = &(root.rb_node), *parent = NULL;

  while (*pos) {
    parent = *pos;
    struct tree_node *cur = rb_entry(parent, struct tree_node, node);

    if (key < cur->key)
      pos = &((*pos)->rb_left);
    else if (key > cur->key)
      pos = &((*pos)->rb_right);
    else {
      pr_err("Key dublicate found: %d\n", key);
      kfree(new_node);
      return STATUS_NONE;
    }
  }

  rb_link_node(&new_node->node, parent, pos);
  rb_insert_color(&new_node->node, &root);

  pr_info("Node add: %d\n", key);
  return STATUS_OK;
}

static int delete_node(int key) {
  struct tree_node *node = find_node(key);
  if (!node) {
    pr_info("No found node %d.\n", key);
    return STATUS_NONE;
  }

  rb_erase(&node->node, &root);
  kfree(node);

  pr_info("Node removed: %d\n", key);
  return STATUS_OK;
}

static void traverse_and_print(struct rb_node *node) {
  if (!node) {
    return;
  }

  struct tree_node *t = rb_entry(node, struct tree_node, node);
  traverse_and_print(node->rb_left);
  pr_cont("%d ", t->key);
  traverse_and_print(node->rb_right);
}

static int add_cmd_handler(const char *argv) {
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
  cmd_status = insert_node(value);
  if (cmd_status == STATUS_OK) {
    cmd_result = value;
  }

  return cmd_status;
}

static int del_cmd_handler(const char *argv) {
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
  cmd_status = delete_node(value);
  if (cmd_status == STATUS_OK) {
    cmd_result = value;
  }

  return cmd_status;
}

static int search_cmd_handler(const char *argv) {
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

  struct tree_node *node = find_node(value);
  cmd_result = node != NULL ? 1 : 0;

  return STATUS_OK;
}

static int print_cmd_handler(const char *argv) {
  cmd_result = 0;
  pr_info("Values: ");
  traverse_and_print(root.rb_node);
  pr_cont("\n");
  return STATUS_OK;
}

static struct command COMMANDS[] = {
    COMMAND(add),
    COMMAND(del),
    COMMAND(search),
    COMMAND(print),
};

static int cmd_execute(const char *cmd_str) {
  int cmd_status = STATUS_UNKNOWN_CMD;
  if (cmd_str == NULL || strlen(cmd_str) <= 1)
    return cmd_status;

  char cmd[MAX_CMD_STR_LEN + 1] = {0};
  char cmd_args[MAX_CMD_ARG_STR_LEN + 1] = {0};

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

static int __init ex_rb_tree_init(void) {
  pr_info("init\n");
  return 0;
}

static void __exit ex_rb_tree_exit(void) {
  free_rb_tree();
  pr_info("exit\n");
}

module_init(ex_rb_tree_init);
module_exit(ex_rb_tree_exit);
