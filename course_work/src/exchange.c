// SPDX-License-Identifier: GPL-2.0-only
/**
 * OTUS course homework 'Linux Kernel Development'
 * Task: course work
 * Module: exchange
 *
 * Copyright (c) 2007-2025 SergSentry
 */

#define pr_fmt(fmt) "%s [%s]: " fmt, KBUILD_MODNAME, __func__

#include <linux/cdev.h>
#include <linux/fs.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>

#include "exchange.h"

static dev_t exchange_dev = MKDEV(0, 0);
static struct class *exchange_class;
static struct cdev exchange_cdev;

static int device_open(struct inode *inode, struct file *filp) {
  pr_info("Device opened\n");
  return 0;
}

static int device_release(struct inode *inode, struct file *filp) {
  pr_info("Device closed\n");
  return 0;
}

static ssize_t device_read(struct file *filp, char __user *buffer, size_t count,
                           loff_t *f_pos) {
  pr_info("Device read\n");
  return 0;
}

static ssize_t device_write(struct file *filp, const char __user *buffer,
                            size_t count, loff_t *f_pos) {
  pr_info("Device write\n");
  return count;
}

static const struct file_operations exchange_fops = {
    .owner = THIS_MODULE,
    .open = device_open,
    .read = device_read,
    .write = device_write,
    .release = device_release,
};

static int __init exchange_init(void) {

  int ret;

  alloc_chrdev_region(&exchange_dev, 0, MAX_REQUESTS, DEVICE_NAME);

  exchange_class = class_create(THIS_MODULE, DEVICE_NAME);

  for (int i = 0; i < MAX_REQUESTS; ++i) {
    device_create(exchange_class, NULL, MKDEV(MAJOR(exchange_dev), i), NULL,
                  DEVICE_NAME "%d", i);
  }

  cdev_init(&exchange_cdev, &exchange_fops);

  ret = cdev_add(&exchange_cdev, exchange_dev, MAX_REQUESTS);
  if (ret < 0) {
    unregister_chrdev_region(exchange_dev, MAX_REQUESTS);
    return ret;
  }

  pr_info("init\n");
  return 0;
}

static void __exit exchange_exit(void) {
  for (int i = 0; i < MAX_REQUESTS; ++i)
    device_destroy(exchange_class, MKDEV(MAJOR(exchange_dev), i));

  class_destroy(exchange_class);
  cdev_del(&exchange_cdev);

  unregister_chrdev_region(exchange_dev, MAX_REQUESTS);

  pr_info("exit\n");
}

module_init(exchange_init);
module_exit(exchange_exit);
