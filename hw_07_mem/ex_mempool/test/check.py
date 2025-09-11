#!/usr/bin/env python3

import os
import time
import stat
import unittest

from test.modules.mempool_module import MempoolModule
from test.tools.dmesg import Dmesg

MODULE_BUILD_DIR = "./build"
MODULE_PATH = f'{MODULE_BUILD_DIR}'


class TestMempoolModule(unittest.TestCase):

    def test_file_exists(self):
        '''
        Test for the presence of a module file in the build directory
        '''
        self.assertTrue(os.path.abspath(MODULE_BUILD_DIR))
        self.assertTrue(os.path.exists(MODULE_PATH))

    def test_lsmod(self):
        '''
        Checking for a loaded module
        '''
        with MempoolModule(path=MODULE_PATH) as mempool_module:
            self.assertTrue(mempool_module.has_loaded())

    def test_init_message(self):
        '''
        Checking the dmesg log for the module initialization string
        '''
        with MempoolModule(path=MODULE_PATH) as mempool_module:
            _, func, msg = next(Dmesg.get_messages(MempoolModule.MODULE_NAME, last=1))

            self.assertEqual("ex_mempool_init", func.strip())
            self.assertEqual("init", msg.strip())

    def test_exit_message(self):
        '''
        Checking the dmesg log for the module deinitialization string
        '''
        with MempoolModule(path=MODULE_PATH) as mempool_module:
            pass

        _, func, msg = next(Dmesg.get_messages(MempoolModule.MODULE_NAME, last=1))

        self.assertEqual("ex_mempool_exit", func.strip())
        self.assertEqual("exit", msg.strip())


    def test_permission(self):
        '''
        Check permission for parameters file /sys/module/<MODULE_NAME>/parameters/<NAME>
        '''
        with MempoolModule(path=MODULE_PATH) as mempool_module:
            param = {
                mempool_module._get_parameter_path(MempoolModule.MODULE_PARAM_CMD): 0o640,
                mempool_module._get_parameter_path(MempoolModule.MODULE_PARAM_CMD_STATUS): 0o640,
                mempool_module._get_parameter_path(MempoolModule.MODULE_PARAM_CMD_RESULT): 0o640,
            }

            for k, v in param.items():
                check_file = os.stat(k)
                self.assertTrue(bool(check_file.st_mode & v))

    def test_unknown_cmd_empty(self):
        '''
        The 'unknown_cmd' error command test. Act for empty command string
        '''
        with MempoolModule(path=MODULE_PATH) as mempool_module:
            status, result = mempool_module.execute("")
            self.assertEqual(-22, status)
            self.assertEqual(0, result)

    def test_unknown_cmd_start_with_space(self):
        '''
        The 'unknown_cmd' error command test. Act for command string with start space symbol
        '''
        with MempoolModule(path=MODULE_PATH) as mempool_module:
            with self.assertRaises(OSError):
                 status, result = mempool_module.execute(" "+MempoolModule.MODULE_CMD_GET_MEM)

    def test_unknown_cmd_other(self):
        '''
        The 'unknown_cmd' error command test. Act for other command string
        '''
        with MempoolModule(path=MODULE_PATH) as mempool_module:
            with self.assertRaises(OSError):
                 status, result = mempool_module.execute("simsalabim")

    def test_get_mem(self):
        '''
        The 'get_mem' command test
        '''
        Dmesg.clear()

        with MempoolModule(path=MODULE_PATH) as mempool_module:
              status, result = mempool_module.execute(MempoolModule.MODULE_CMD_GET_MEM)
              self.assertEqual(0, status)
              self.assertEqual(0, result)

        _, func, msg = next(Dmesg.get_reg_messages_by_func(MempoolModule.MODULE_NAME, "get_mem_cmd_handler", "mempool:\\sSUCCSESS"))

        self.assertEqual("get_mem_cmd_handler", func.strip())
        self.assertEqual("mempool: SUCCSESS", msg.strip())

        _, func, msg = next(Dmesg.get_messages_by_func(MempoolModule.MODULE_NAME, "get_mem_cmd_handler", last=1))

        if msg:
            with open("test/result/test_report.md", "ta") as report_file:
                report_file.write(f"#### Report for {MempoolModule.MODULE_NAME} with kmalloc allocator.\n")
                report_file.write(f"> {msg}\n")
                report_file.write(f"\n")


    def test_get_page_mem(self):
        '''
        The 'get_page_mem' command test
        '''
        Dmesg.clear()

        with MempoolModule(path=MODULE_PATH) as mempool_module:
              status, result = mempool_module.execute(MempoolModule.MODULE_CMD_GET_PAGE_MEM)
              self.assertEqual(0, status)
              self.assertEqual(0, result)

        _, func, msg = next(Dmesg.get_reg_messages_by_func(MempoolModule.MODULE_NAME, "get_page_mem_cmd_handler", "mempool:\\sSUCCSESS"))

        self.assertEqual("get_page_mem_cmd_handler", func.strip())
        self.assertEqual("mempool: SUCCSESS", msg.strip())

        _, func, msg = next(Dmesg.get_messages_by_func(MempoolModule.MODULE_NAME, "get_page_mem_cmd_handler", last=1))

        if msg:
            with open("test/result/test_report.md", "ta") as report_file:
                report_file.write(f"#### Report for {MempoolModule.MODULE_FILE_NAME} with mempool allocator.\n")
                report_file.write(f"> {msg}\n")
                report_file.write(f"\n")

