// SPDX-License-Identifier: GPL-2.0-only
/**
 * OTUS course homework 'Linux Kernel Development'
 * Task: course work
 * Module: exchange
 *
 * Copyright (c) 2007-2025 SergSentry
 */

#define pr_fmt(fmt) "%s [%s]: " fmt, KBUILD_MODNAME, __func__

#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>

#include "exchange.h"

static int __init exchange_init(void) {
  pr_info("init\n");
  return 0;
}

static void __exit exchange_exit(void) {
  pr_info("exit\n");
}

module_init(exchange_init);
module_exit(exchange_exit);
