#!/usr/bin/env python3

import os
import stat
import unittest

from test.modules.bin_search_module import BinSearchModule
from test.tools.dmesg import Dmesg

MODULE_BUILD_DIR = "./build"
MODULE_PATH = f'{MODULE_BUILD_DIR}'


class TestBinSearchModule(unittest.TestCase):

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
        with BinSearchModule(path=MODULE_PATH) as bin_search_module:
            self.assertTrue(bin_search_module.has_loaded())

    def test_init_message(self):
        '''
        Checking the dmesg log for the module initialization string
        '''
        with BinSearchModule(path=MODULE_PATH) as bin_search_module:
            _, func, msg = next(Dmesg.get_messages(BinSearchModule.MODULE_NAME, last=1))

            self.assertEqual("ex_bin_search_init", func.strip())
            self.assertEqual("init", msg.strip())

    def test_exit_message(self):
        '''
        Checking the dmesg log for the module deinitialization string
        '''
        with BinSearchModule(path=MODULE_PATH) as bin_search_module:
            pass

        _, func, msg = next(Dmesg.get_messages(BinSearchModule.MODULE_NAME, last=1))

        self.assertEqual("ex_bin_search_exit", func.strip())
        self.assertEqual("exit", msg.strip())

    def test_permission(self):
        '''
        Check permission for parameters file /sys/module/<MODULE_NAME>/parameters/<NAME>
        '''
        with BinSearchModule(path=MODULE_PATH) as bin_search_module:
            param = {
                bin_search_module._get_parameter_path(BinSearchModule.MODULE_PARAM_CMD): 0o640,
                bin_search_module._get_parameter_path(BinSearchModule.MODULE_PARAM_CMD_STATUS): 0o640,
                bin_search_module._get_parameter_path(BinSearchModule.MODULE_PARAM_CMD_RESULT): 0o640,
            }

            for k, v in param.items():
                check_file = os.stat(k)
                self.assertTrue(bool(check_file.st_mode & v))

    def test_unknown_cmd_empty(self):
        '''
        The 'unknown_cmd' error command test. Act for empty command string
        '''
        with BinSearchModule(path=MODULE_PATH) as bin_search_module:
            status, result = bin_search_module.execute("")
            self.assertEqual(0, status)
            self.assertEqual(0, result)

    def test_unknown_cmd_start_with_space(self):
        '''
        The 'unknown_cmd' error command test. Act for command string with start space symbol
        '''
        with BinSearchModule(path=MODULE_PATH) as bin_search_module:
            with self.assertRaises(OSError):
                 status, result = bin_search_module.execute(" "+BinSearchModule.MODULE_CMD_ADD)

    def test_unknown_cmd_other(self):
        '''
        The 'unknown_cmd' error command test. Act for other command string
        '''
        with BinSearchModule(path=MODULE_PATH) as bin_search_module:
            with self.assertRaises(OSError):
                 status, result = bin_search_module.execute("simsalabim")

    def test_add(self):
        '''
        The 'add' command test
        '''
        with BinSearchModule(path=MODULE_PATH) as bin_search_module:
            status, result = bin_search_module.execute(f"{BinSearchModule.MODULE_CMD_ADD} 1")
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            _, func, msg = next(Dmesg.get_messages(BinSearchModule.MODULE_NAME, last=1))

            self.assertEqual("add", func.strip())
            self.assertTrue('Add index: 0 value: 1' in msg.strip())

    def test_sort(self):
        '''
        The 'sort' command test
        '''
        with BinSearchModule(path=MODULE_PATH) as bin_search_module:
            status, result = bin_search_module.execute(f"{BinSearchModule.MODULE_CMD_ADD} 4")
            self.assertEqual(0, status)
            self.assertEqual(4, result)

            status, result = bin_search_module.execute(f"{BinSearchModule.MODULE_CMD_ADD} 1")
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = bin_search_module.execute(f"{BinSearchModule.MODULE_CMD_ADD} 3")
            self.assertEqual(0, status)
            self.assertEqual(3, result)

            status, result = bin_search_module.execute(BinSearchModule.MODULE_CMD_SORT)
            self.assertEqual(0, status)
            self.assertEqual(0, result)

            status, result = bin_search_module.execute(BinSearchModule.MODULE_CMD_PRINT)
            self.assertEqual(0, status)
            self.assertEqual(0, result)

            _, func, msg = next(Dmesg.get_messages(BinSearchModule.MODULE_NAME, last=1))
            self.assertEqual("print_cmd_handler", func.strip())
            self.assertTrue('Values: 1 3 4' in msg.strip())

    def test_search(self):
        '''
        The 'search' command test
        '''
        with BinSearchModule(path=MODULE_PATH) as bin_search_module:
            status, result = bin_search_module.execute(f"{BinSearchModule.MODULE_CMD_ADD} 4")
            self.assertEqual(0, status)
            self.assertEqual(4, result)

            status, result = bin_search_module.execute(f"{BinSearchModule.MODULE_CMD_ADD} 1")
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = bin_search_module.execute(f"{BinSearchModule.MODULE_CMD_ADD} 3")
            self.assertEqual(0, status)
            self.assertEqual(3, result)

            status, result = bin_search_module.execute(f"{BinSearchModule.MODULE_CMD_SEARCH} 3")
            self.assertEqual(0, status)
            self.assertEqual(3, result)

    def test_no_found(self):
        '''
        The empty 'search' command test
        '''
        with BinSearchModule(path=MODULE_PATH) as bin_search_module:
            status, result = bin_search_module.execute(f"{BinSearchModule.MODULE_CMD_ADD} 4")
            self.assertEqual(0, status)
            self.assertEqual(4, result)

            status, result = bin_search_module.execute(f"{BinSearchModule.MODULE_CMD_ADD} 1")
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = bin_search_module.execute(f"{BinSearchModule.MODULE_CMD_ADD} 3")
            self.assertEqual(0, status)
            self.assertEqual(3, result)

            status, result = bin_search_module.execute(f"{BinSearchModule.MODULE_CMD_SEARCH} 2")
            self.assertEqual(0, status)
            self.assertEqual(0, result)

    def test_print(self):
        '''
        The 'print' command test
        '''
        with BinSearchModule(path=MODULE_PATH) as bin_search_module:
            status, result = bin_search_module.execute(f"{BinSearchModule.MODULE_CMD_ADD} 4")
            self.assertEqual(0, status)
            self.assertEqual(4, result)

            status, result = bin_search_module.execute(f"{BinSearchModule.MODULE_CMD_ADD} 1")
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = bin_search_module.execute(f"{BinSearchModule.MODULE_CMD_ADD} 3")
            self.assertEqual(0, status)
            self.assertEqual(3, result)

            status, result = bin_search_module.execute(BinSearchModule.MODULE_CMD_PRINT)
            self.assertEqual(0, status)
            self.assertEqual(0, result)

            _, func, msg = next(Dmesg.get_messages(BinSearchModule.MODULE_NAME, last=1))
            self.assertEqual("print_cmd_handler", func.strip())
            self.assertTrue('Values: 4 1 3' in msg.strip())
