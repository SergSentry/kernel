#!/usr/bin/env python

import os
import stat
import unittest

from test.modules.hash_module import HashModule
from test.tools.dmesg import Dmesg

MODULE_BUILD_DIR = "./build"
MODULE_PATH = f'{MODULE_BUILD_DIR}'


class TestHashModule(unittest.TestCase):

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
        with HashModule(path=MODULE_PATH) as hash_module:
            self.assertTrue(hash_module.has_loaded())

    def test_init_message(self):
        '''
        Checking the dmesg log for the module initialization string
        '''
        with HashModule(path=MODULE_PATH) as hash_module:
            _, func, msg = next(Dmesg.get_messages(HashModule.MODULE_NAME, last=1))

            self.assertEqual("ex_hash_init", func.strip())
            self.assertEqual("init", msg.strip())

    def test_exit_message(self):
        '''
        Checking the dmesg log for the module deinitialization string
        '''
        with HashModule(path=MODULE_PATH) as hash_module:
            pass

        _, func, msg = next(Dmesg.get_messages(HashModule.MODULE_NAME, last=1))

        self.assertEqual("ex_hash_exit", func.strip())
        self.assertEqual("exit", msg.strip())

    def test_permission(self):
        '''
        Check permission for parameters file /sys/module/<MODULE_NAME>/parameters/<NAME>
        '''
        with HashModule(path=MODULE_PATH) as hash_module:
            param = {
                hash_module._get_parameter_path(HashModule.MODULE_PARAM_CMD): 0o640,
                hash_module._get_parameter_path(HashModule.MODULE_PARAM_CMD_STATUS): 0o640,
                hash_module._get_parameter_path(HashModule.MODULE_PARAM_CMD_RESULT): 0o640,
            }

            for k, v in param.items():
                check_file = os.stat(k)
                self.assertTrue(bool(check_file.st_mode & v))

    def test_unknown_cmd_empty(self):
        '''
        The 'unknown_cmd' error command test. Act for empty command string
        '''
        with HashModule(path=MODULE_PATH) as hash_module:
            status, result = hash_module.execute("")
            self.assertEqual(-22, status)
            self.assertEqual(0, result)

    def test_unknown_cmd_start_with_space(self):
        '''
        The 'unknown_cmd' error command test. Act for command string with start space symbol
        '''
        with HashModule(path=MODULE_PATH) as hash_module:
            with self.assertRaises(OSError):
                 status, result = hash_module.execute(" "+HashModule.MODULE_CMD_ADD)

    def test_unknown_cmd_other(self):
        '''
        The 'unknown_cmd' error command test. Act for other command string
        '''
        with HashModule(path=MODULE_PATH) as hash_module:
            with self.assertRaises(OSError):
                 status, result = hash_module.execute("simsalabim")

    def test_add(self):
        '''
        The 'add' command test.
        '''
        with HashModule(path=MODULE_PATH) as hash_module:
            status, result = hash_module.execute(f"{HashModule.MODULE_CMD_ADD} ivanov")
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            _, func, msg = next(Dmesg.get_messages(HashModule.MODULE_NAME, last=1))

            self.assertEqual("add", func.strip())
            self.assertTrue('Add Username: ivanov, ID:' in msg.strip())

    def test_del(self):
        '''
        The 'del' command test.
        '''
        with HashModule(path=MODULE_PATH) as hash_module:
            status, result = hash_module.execute(f"{HashModule.MODULE_CMD_ADD} ivanov")
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = hash_module.execute(f"{HashModule.MODULE_CMD_DEL} ivanov")
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            _, func, msg = next(Dmesg.get_messages(HashModule.MODULE_NAME, last=1))

            self.assertEqual("del", func.strip())
            self.assertTrue('Del Username: ivanov, ID:' in msg.strip())

    def test_no_search(self):
        '''
        The no 'search' command test.
        '''
        with HashModule(path=MODULE_PATH) as hash_module:
            status, result = hash_module.execute(f"{HashModule.MODULE_CMD_SEARCH} ivanov")
            self.assertEqual(0, status)
            self.assertEqual(0, result)

            _, func, msg = next(Dmesg.get_messages(HashModule.MODULE_NAME, last=1))

            self.assertEqual("search_cmd_handler", func.strip())
            self.assertTrue('No found: ivanov' in msg.strip())

    def test_search(self):
        '''
        The 'search' command test.
        '''
        with HashModule(path=MODULE_PATH) as hash_module:
            status, result = hash_module.execute(f"{HashModule.MODULE_CMD_ADD} ivanov")
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = hash_module.execute(f"{HashModule.MODULE_CMD_SEARCH} ivanov")
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            _, func, msg = next(Dmesg.get_messages(HashModule.MODULE_NAME, last=1))

            self.assertEqual("search_cmd_handler", func.strip())
            self.assertTrue('Find Username: ivanov, ID:' in msg.strip())

    def test_print(self):
        '''
        The 'print' command test.
        '''
        with HashModule(path=MODULE_PATH) as hash_module:
            status, result = hash_module.execute(f"{HashModule.MODULE_CMD_ADD} ivanov")
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = hash_module.execute(HashModule.MODULE_CMD_PRINT)
            self.assertEqual(0, status)
            self.assertEqual(0, result)

            _, func, msg = next(Dmesg.get_messages(HashModule.MODULE_NAME, last=1))

            self.assertEqual("print_cmd_handler", func.strip())
            self.assertTrue('Username: ivanov, ID:' in msg.strip())
