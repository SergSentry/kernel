#!/usr/bin/env python3

import os
import time
import stat
import unittest

from test.modules.get_page_module import GetPageModule
from test.tools.dmesg import Dmesg

MODULE_BUILD_DIR = "./build"
MODULE_PATH = f'{MODULE_BUILD_DIR}'


class TestGetPageModule(unittest.TestCase):

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
        with GetPageModule(path=MODULE_PATH) as getPageModule:
            self.assertTrue(getPageModule.has_loaded())

    def test_init_message(self):
        '''
        Checking the dmesg log for the module initialization string
        '''
        with GetPageModule(path=MODULE_PATH) as getPageModule:
            _, func, msg = next(Dmesg.get_messages(GetPageModule.MODULE_NAME, last=1))

            self.assertEqual("ex_get_page_init", func.strip())
            self.assertEqual("init", msg.strip())

    def test_exit_message(self):
        '''
        Checking the dmesg log for the module deinitialization string
        '''
        with GetPageModule(path=MODULE_PATH) as getPageModule:
            pass

        _, func, msg = next(Dmesg.get_messages(GetPageModule.MODULE_NAME, last=1))

        self.assertEqual("ex_get_page_exit", func.strip())
        self.assertEqual("exit", msg.strip())


    def test_permission(self):
        '''
        Check permission for parameters file /sys/module/<MODULE_NAME>/parameters/<NAME>
        '''
        with GetPageModule(path=MODULE_PATH) as getPageModule:
            param = {
                getPageModule._get_parameter_path(GetPageModule.MODULE_PARAM_CMD): 0o640,
                getPageModule._get_parameter_path(GetPageModule.MODULE_PARAM_CMD_STATUS): 0o640,
                getPageModule._get_parameter_path(GetPageModule.MODULE_PARAM_CMD_RESULT): 0o640,
            }

            for k, v in param.items():
                check_file = os.stat(k)
                self.assertTrue(bool(check_file.st_mode & v))

    def test_unknown_cmd_empty(self):
        '''
        The 'unknown_cmd' error command test. Act for empty command string
        '''
        with GetPageModule(path=MODULE_PATH) as getPageModule:
            status, result = getPageModule.execute("")
            self.assertEqual(-22, status)
            self.assertEqual(0, result)

    def test_unknown_cmd_start_with_space(self):
        '''
        The 'unknown_cmd' error command test. Act for command string with start space symbol
        '''
        with GetPageModule(path=MODULE_PATH) as getPageModule:
            with self.assertRaises(OSError):
                 status, result = getPageModule.execute(" "+GetPageModule.MODULE_CMD_GET_PAGE_MEM)

    def test_unknown_cmd_other(self):
        '''
        The 'unknown_cmd' error command test. Act for other command string
        '''
        with GetPageModule(path=MODULE_PATH) as getPageModule:
            with self.assertRaises(OSError):
                 status, result = getPageModule.execute("simsalabim")

    def test_get_page_mem(self):
        '''
        The 'get_page_mem' command test
        '''
        Dmesg.clear()

        with GetPageModule(path=MODULE_PATH) as getPageModule:
              status, result = getPageModule.execute(GetPageModule.MODULE_CMD_GET_PAGE_MEM)
              self.assertEqual(0, status)
              self.assertEqual(0, result)

        _, func, msg = next(Dmesg.get_reg_messages_by_func(GetPageModule.MODULE_NAME, "get_page_mem_cmd_handler", "get_page:\\sSUCCSESS"))

        self.assertEqual("get_page_mem_cmd_handler", func.strip())
        self.assertEqual("get_page: SUCCSESS", msg.strip())

        _, func, msg = next(Dmesg.get_messages_by_func(GetPageModule.MODULE_NAME, "get_page_mem_cmd_handler", last=1))

        if msg:
            with open("test/result/test_report.md", "ta") as report_file:
                report_file.write(f"#### Report for {GetPageModule.MODULE_FILE_NAME} with one pager allocator.\n")
                report_file.write(f"> {msg}\n")
                report_file.write(f"\n")

    def test_get_max_mem(self):
        '''
        The 'get_max_mem' command test
        '''
        Dmesg.clear()

        with GetPageModule(path=MODULE_PATH) as getPageModule:
              status, result = getPageModule.execute(GetPageModule.MODULE_CMD_GET_MAX_MEM)
              self.assertEqual(0, status)
              self.assertEqual(0, result)

        _, func, msg = next(Dmesg.get_reg_messages_by_func(GetPageModule.MODULE_NAME, "get_max_mem_cmd_handler", "get_page:\\sSUCCSESS"))

        self.assertEqual("get_max_mem_cmd_handler", func.strip())
        self.assertEqual("get_page: SUCCSESS", msg.strip())

        _, func, msg = next(Dmesg.get_messages_by_func(GetPageModule.MODULE_NAME, "get_max_mem_cmd_handler", last=1))

        if msg:
            with open("test/result/test_report.md", "ta") as report_file:
                report_file.write(f"#### Report for {GetPageModule.MODULE_FILE_NAME} with many pages allocator.\n")
                report_file.write(f"> {msg}\n")
                report_file.write(f"\n")
