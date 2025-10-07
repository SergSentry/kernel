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

#include "include/exchange/api.h"
#include "exchange.h"

static dev_t exchange_dev = MKDEV(0, 0);
static struct class *exchange_class;
static struct cdev exchange_cdev;
static int work_mode = EXCHANGE_UNICAST;

static int param_set_work_mode_handler(const char *val, const struct kernel_param *kp)
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

	if (new_value < 0 || new_value > EXCHANGE_BROADCAST) {
		pr_err("Param error: %s out of range (0, %d)\n", kp->name,
		       EXCHANGE_BROADCAST);
		return -EINVAL;
	}

	*((unsigned int *)kp->arg) = new_value;
	pr_info("Set param: %s=%d\n", kp->name, new_value);
	return 0;
}

static const struct kernel_param_ops work_mode_ops = {
	.set = param_set_work_mode_handler,
	.get = param_get_int,
};

module_param_cb(work_mode, &work_mode_ops, &work_mode,
		S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH);
MODULE_PARM_DESC(work_mode, "Exchange work mode. 0 - UNICAST. 1 - BROADCAST");


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

static long device_ioctl(struct file *file, unsigned int cmd,
                         unsigned long arg) {
  switch (cmd) {
  case EXCHANGE_IOCTL_GET_WORK_MODE: {
    if (copy_to_user((void __user *)arg, &work_mode, sizeof(int)) != 0)
      return -EFAULT;
    pr_info("ioctl: mode is %d\n", work_mode);
    break;
  }

  default:
    return -ENOTTY;
  }
  return 0;
}

static const struct file_operations exchange_fops = {.owner = THIS_MODULE,
                                                     .open = device_open,
                                                     .read = device_read,
                                                     .write = device_write,
                                                     .release = device_release,
                                                     .unlocked_ioctl =
                                                         device_ioctl};

static int __init exchange_init(void) {

  int ret;

  int err = alloc_chrdev_region(&exchange_dev, 0, 1, DEVICE_NAME);
  if (err < 0) {
    pr_err("Failed to register the primary device number\n");
    return err;
  }

  exchange_class = class_create(THIS_MODULE, DEVICE_NAME);
  if (IS_ERR(exchange_class)) {
    unregister_chrdev_region(exchange_dev, 1);
    pr_err("Class creation failed\n");
    return PTR_ERR(exchange_class);
  }

  cdev_init(&exchange_cdev, &exchange_fops);

  ret = cdev_add(&exchange_cdev, exchange_dev, 1);
  if (ret < 0) {
    class_destroy(exchange_class);
    unregister_chrdev_region(exchange_dev, 1);
    pr_err("Failed to add character device\n");
    return ret;
  }

  device_create(exchange_class, NULL, exchange_dev, NULL, DEVICE_NAME);

  pr_info("init\n");
  return 0;
}

static void __exit exchange_exit(void) {
  device_destroy(exchange_class, exchange_dev);
  cdev_del(&exchange_cdev);
  class_destroy(exchange_class);
  unregister_chrdev_region(exchange_dev, 1);

  pr_info("exit\n");
}

module_init(exchange_init);
module_exit(exchange_exit);
