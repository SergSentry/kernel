#!/usr/bin/env python3

import os
import time
import stat
import unittest

from test.modules.vmalloc_module import VmallocModule
from test.tools.dmesg import Dmesg

MODULE_BUILD_DIR = "./build"
MODULE_PATH = f'{MODULE_BUILD_DIR}'


class TestVmallocModule(unittest.TestCase):

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
        with VmallocModule(path=MODULE_PATH) as vmalloc_module:
            self.assertTrue(vmalloc_module.has_loaded())

    def test_init_message(self):
        '''
        Checking the dmesg log for the module initialization string
        '''
        with VmallocModule(path=MODULE_PATH) as vmalloc_module:
            _, func, msg = next(Dmesg.get_messages(VmallocModule.MODULE_NAME, last=1))

            self.assertEqual("ex_vmalloc_init", func.strip())
            self.assertEqual("init", msg.strip())

    def test_exit_message(self):
        '''
        Checking the dmesg log for the module deinitialization string
        '''
        with VmallocModule(path=MODULE_PATH) as vmalloc_module:
            pass

        _, func, msg = next(Dmesg.get_messages(VmallocModule.MODULE_NAME, last=1))

        self.assertEqual("ex_vmalloc_exit", func.strip())
        self.assertEqual("exit", msg.strip())


    def test_permission(self):
        '''
        Check permission for parameters file /sys/module/<MODULE_NAME>/parameters/<NAME>
        '''
        with VmallocModule(path=MODULE_PATH) as vmalloc_module:
            param = {
                vmalloc_module._get_parameter_path(VmallocModule.MODULE_PARAM_CMD): 0o640,
                vmalloc_module._get_parameter_path(VmallocModule.MODULE_PARAM_CMD_STATUS): 0o640,
                vmalloc_module._get_parameter_path(VmallocModule.MODULE_PARAM_CMD_RESULT): 0o640,
            }

            for k, v in param.items():
                check_file = os.stat(k)
                self.assertTrue(bool(check_file.st_mode & v))

    def test_unknown_cmd_empty(self):
        '''
        The 'unknown_cmd' error command test. Act for empty command string
        '''
        with VmallocModule(path=MODULE_PATH) as vmalloc_module:
            status, result = vmalloc_module.execute("")
            self.assertEqual(-22, status)
            self.assertEqual(0, result)

    def test_unknown_cmd_start_with_space(self):
        '''
        The 'unknown_cmd' error command test. Act for command string with start space symbol
        '''
        with VmallocModule(path=MODULE_PATH) as vmalloc_module:
            with self.assertRaises(OSError):
                 status, result = vmalloc_module.execute(" "+VmallocModule.MODULE_CMD_GET_MEM)

    def test_unknown_cmd_other(self):
        '''
        The 'unknown_cmd' error command test. Act for other command string
        '''
        with VmallocModule(path=MODULE_PATH) as vmalloc_module:
            with self.assertRaises(OSError):
                 status, result = vmalloc_module.execute("simsalabim")

    def test_get_mem(self):
        '''
        The 'get_mem' command test
        '''
        Dmesg.clear()

        with VmallocModule(path=MODULE_PATH) as vmalloc_module:
              status, result = vmalloc_module.execute(VmallocModule.MODULE_CMD_GET_MEM)
              self.assertEqual(0, status)
              self.assertEqual(0, result)

        _, func, msg = next(Dmesg.get_reg_messages_by_func(VmallocModule.MODULE_NAME, "get_mem_cmd_handler", "vmalloc:\\sSUCCSESS"))

        self.assertEqual("get_mem_cmd_handler", func.strip())
        self.assertEqual("vmalloc: SUCCSESS", msg.strip())

        _, func, msg = next(Dmesg.get_messages_by_func(VmallocModule.MODULE_NAME, "get_mem_cmd_handler", last=1))

        if msg:
            with open("test/result/test_report.md", "ta") as report_file:
                report_file.write(f"#### Report for {VmallocModule.MODULE_FILE_NAME} with vmalloc allocator.\n")
                report_file.write(f"> {msg}\n")
                report_file.write(f"\n")
