#!/usr/bin/env python

import os
import stat
import unittest

from test.modules.bitmap_module import BitmapModule
from test.tools.dmesg import Dmesg

MODULE_BUILD_DIR = "./build"
MODULE_PATH = f'{MODULE_BUILD_DIR}'


class TestBitmapModule(unittest.TestCase):

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
        with BitmapModule(path=MODULE_PATH) as bitmap_module:
            self.assertTrue(bitmap_module.has_loaded())

    def test_init_message(self):
        '''
        Checking the dmesg log for the module initialization string
        '''
        with BitmapModule(path=MODULE_PATH) as bitmap_module:
            _, func, msg = next(Dmesg.get_messages(BitmapModule.MODULE_NAME, last=1))

            self.assertEqual("ex_bitmap_init", func.strip())
            self.assertEqual("init", msg.strip())

    def test_exit_message(self):
        '''
        Checking the dmesg log for the module deinitialization string
        '''
        with BitmapModule(path=MODULE_PATH) as bitmap_module:
            pass

        _, func, msg = next(Dmesg.get_messages(BitmapModule.MODULE_NAME, last=1))

        self.assertEqual("ex_bitmap_exit", func.strip())
        self.assertEqual("exit", msg.strip())

    def test_permission(self):
        '''
        Check permission for parameters file /sys/module/<MODULE_NAME>/parameters/<NAME>
        '''
        with BitmapModule(path=MODULE_PATH) as bitmap_module:
            param = {
                bitmap_module._get_parameter_path(BitmapModule.MODULE_PARAM_CMD): 0o640,
                bitmap_module._get_parameter_path(BitmapModule.MODULE_PARAM_CMD_STATUS): 0o640,
                bitmap_module._get_parameter_path(BitmapModule.MODULE_PARAM_CMD_RESULT): 0o640,
            }

            for k, v in param.items():
                check_file = os.stat(k)
                self.assertTrue(bool(check_file.st_mode & v))

    def test_unknown_cmd_empty(self):
        '''
        The 'unknown_cmd' error command test. Act for empty command string
        '''
        with BitmapModule(path=MODULE_PATH) as bitmap_module:
            status, result = bitmap_module.execute("")
            self.assertEqual(-22, status)
            self.assertEqual(0, result)

    def test_unknown_cmd_start_with_space(self):
        '''
        The 'unknown_cmd' error command test. Act for command string with start space symbol
        '''
        with BitmapModule(path=MODULE_PATH) as bitmap_module:
            with self.assertRaises(OSError):
                 status, result = bitmap_module.execute(" "+BitmapModule.MODULE_CMD_CLEAR)

    def test_unknown_cmd_other(self):
        '''
        The 'unknown_cmd' error command test. Act for other command string
        '''
        with BitmapModule(path=MODULE_PATH) as bitmap_module:
            with self.assertRaises(OSError):
                 status, result = bitmap_module.execute("simsalabim")

    def test_check(self):
        '''
        The 'check' command test
        '''
        with BitmapModule(path=MODULE_PATH) as bitmap_module:
            status, result = bitmap_module.execute(f'{BitmapModule.MODULE_CMD_CHECK} 0')
            self.assertEqual(0, status)
            self.assertEqual(0, result)

    def test_check_overload(self):
        '''
        The 'check' error command test. Act for check bit over size bitmap
        '''
        with BitmapModule(path=MODULE_PATH) as bitmap_module:
            with self.assertRaises(OSError):
                 status, result = bitmap_module.execute(f'{BitmapModule.MODULE_CMD_CHECK} 33')

    def test_set(self):
        '''
        The 'set' command test
        '''
        with BitmapModule(path=MODULE_PATH) as bitmap_module:
            status, result = bitmap_module.execute(f'{BitmapModule.MODULE_CMD_SET} 0')
            self.assertEqual(0, status)
            self.assertEqual(0, result)

    def test_set_overload(self):
        '''
        The 'set' error command test. Act for set bit over size bitmap
        '''
        with BitmapModule(path=MODULE_PATH) as bitmap_module:
            with self.assertRaises(OSError):
                 status, result = bitmap_module.execute(f'{BitmapModule.MODULE_CMD_SET} 33')

    def test_check_set(self):
        '''
        The check and set command test
        '''
        with BitmapModule(path=MODULE_PATH) as bitmap_module:
            status, result = bitmap_module.execute(f'{BitmapModule.MODULE_CMD_CHECK} 0')
            self.assertEqual(0, status)
            self.assertEqual(0, result)

            status, result = bitmap_module.execute(f'{BitmapModule.MODULE_CMD_SET} 0')
            self.assertEqual(0, status)
            self.assertEqual(0, result)

            status, result = bitmap_module.execute(f'{BitmapModule.MODULE_CMD_CHECK} 0')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

    def test_clear(self):
        '''
        The 'clear' command test
        '''
        with BitmapModule(path=MODULE_PATH) as bitmap_module:
            status, result = bitmap_module.execute(f'{BitmapModule.MODULE_CMD_SET} 0')
            self.assertEqual(0, status)
            self.assertEqual(0, result)

            status, result = bitmap_module.execute(f'{BitmapModule.MODULE_CMD_CHECK} 0')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = bitmap_module.execute(f'{BitmapModule.MODULE_CMD_CLEAR} 0')
            self.assertEqual(0, status)
            self.assertEqual(0, result)

            status, result = bitmap_module.execute(f'{BitmapModule.MODULE_CMD_CHECK} 0')
            self.assertEqual(0, status)
            self.assertEqual(0, result)

    def test_clear_overload(self):
        '''
        The 'clear' error command test. Act for clear bit over size bitmap
        '''
        with BitmapModule(path=MODULE_PATH) as bitmap_module:
            with self.assertRaises(OSError):
                 status, result = bitmap_module.execute(f'{BitmapModule.MODULE_CMD_CLEAR} 33')

    def test_search(self):
        '''
        The 'search' command test
        '''
        with BitmapModule(path=MODULE_PATH) as bitmap_module:
            status, result = bitmap_module.execute(f'{BitmapModule.MODULE_CMD_SET} 0')
            self.assertEqual(0, status)
            self.assertEqual(0, result)

            status, result = bitmap_module.execute(f'{BitmapModule.MODULE_CMD_SET} 2')
            self.assertEqual(0, status)
            self.assertEqual(2, result)

            status, result = bitmap_module.execute(BitmapModule.MODULE_CMD_SEARCH)
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = bitmap_module.execute(BitmapModule.MODULE_CMD_SEARCH)
            self.assertEqual(0, status)
            self.assertEqual(3, result)

    def test_print(self):
        '''
        The 'print' command test
        '''
        with BitmapModule(path=MODULE_PATH) as bitmap_module:
            status, result = bitmap_module.execute(f'{BitmapModule.MODULE_CMD_SET} 0')
            self.assertEqual(0, status)
            self.assertEqual(0, result)

            status, result = bitmap_module.execute(f'{BitmapModule.MODULE_CMD_SET} 2')
            self.assertEqual(0, status)
            self.assertEqual(2, result)

            status, result = bitmap_module.execute(BitmapModule.MODULE_CMD_PRINT)
            self.assertEqual(0, status)
            self.assertEqual(0, result)
        
            _, func, msg = next(Dmesg.get_messages(BitmapModule.MODULE_NAME, last=1))
            self.assertEqual("print_cmd_handler", func.strip())
            self.assertEqual("Values: 5", msg.strip())
