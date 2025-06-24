#!/usr/bin/env python

import os
import stat
import unittest

from test.modules.rb_tree_module import RbTreeModule
from test.tools.dmesg import Dmesg

MODULE_BUILD_DIR = "./build"
MODULE_PATH = f'{MODULE_BUILD_DIR}'


class TestRbTreeModule(unittest.TestCase):

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
        with RbTreeModule(path=MODULE_PATH) as rb_tree_module:
            self.assertTrue(rb_tree_module.has_loaded())

    def test_init_message(self):
        '''
        Checking the dmesg log for the module initialization string
        '''
        with RbTreeModule(path=MODULE_PATH) as rb_tree_module:
            _, func, msg = next(Dmesg.get_messages(RbTreeModule.MODULE_NAME, last=1))

            self.assertEqual("ex_rb_tree_init", func.strip())
            self.assertEqual("init", msg.strip())

    def test_exit_message(self):
        '''
        Checking the dmesg log for the module deinitialization string
        '''
        with RbTreeModule(path=MODULE_PATH) as rb_tree_module:
            pass

        _, func, msg = next(Dmesg.get_messages(RbTreeModule.MODULE_NAME, last=1))

        self.assertEqual("ex_rb_tree_exit", func.strip())
        self.assertEqual("exit", msg.strip())

    def test_permission(self):
        '''
        Check permission for parameters file /sys/module/<MODULE_NAME>/parameters/<NAME>
        '''
        with RbTreeModule(path=MODULE_PATH) as rb_tree_module:
            param = {
                rb_tree_module._get_parameter_path(RbTreeModule.MODULE_PARAM_CMD): 0o640,
                rb_tree_module._get_parameter_path(RbTreeModule.MODULE_PARAM_CMD_STATUS): 0o640,
                rb_tree_module._get_parameter_path(RbTreeModule.MODULE_PARAM_CMD_RESULT): 0o640,
            }

            for k, v in param.items():
                check_file = os.stat(k)
                self.assertTrue(bool(check_file.st_mode & v))

    def test_unknown_cmd_empty(self):
        '''
        The 'unknown_cmd' error command test. Act for empty command string
        '''
        with RbTreeModule(path=MODULE_PATH) as rb_tree_module:
            status, result = rb_tree_module.execute("")
            self.assertEqual(-22, status)
            self.assertEqual(0, result)

    def test_unknown_cmd_start_with_space(self):
        '''
        The 'unknown_cmd' error command test. Act for command string with start space symbol
        '''
        with RbTreeModule(path=MODULE_PATH) as rb_tree_module:
            with self.assertRaises(OSError):
                 status, result = rb_tree_module.execute(" "+RbTreeModule.MODULE_CMD_ADD)

    def test_unknown_cmd_other(self):
        '''
        The 'unknown_cmd' error command test. Act for other command string
        '''
        with RbTreeModule(path=MODULE_PATH) as rb_tree_module:
            with self.assertRaises(OSError):
                 status, result = rb_tree_module.execute("simsalabim")

    def test_add(self):
        '''
        The 'add' command test
        '''
        with RbTreeModule(path=MODULE_PATH) as rb_tree_module:
            status, result = rb_tree_module.execute(f'{RbTreeModule.MODULE_CMD_ADD} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

    def test_del(self):
        '''
        The 'del' command test
        '''
        with RbTreeModule(path=MODULE_PATH) as rb_tree_module:
            status, result = rb_tree_module.execute(f'{RbTreeModule.MODULE_CMD_ADD} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = rb_tree_module.execute(f'{RbTreeModule.MODULE_CMD_DEL} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

    def test_search(self):
        '''
        The 'search' command test
        '''
        with RbTreeModule(path=MODULE_PATH) as rb_tree_module:
            status, result = rb_tree_module.execute(f'{RbTreeModule.MODULE_CMD_ADD} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = rb_tree_module.execute(f'{RbTreeModule.MODULE_CMD_ADD} 5')
            self.assertEqual(0, status)
            self.assertEqual(5, result)

            status, result = rb_tree_module.execute(f'{RbTreeModule.MODULE_CMD_ADD} 2')
            self.assertEqual(0, status)
            self.assertEqual(2, result)

            status, result = rb_tree_module.execute(f'{RbTreeModule.MODULE_CMD_ADD} 6')
            self.assertEqual(0, status)
            self.assertEqual(6, result)

            status, result = rb_tree_module.execute(f'{RbTreeModule.MODULE_CMD_ADD} 3')
            self.assertEqual(0, status)
            self.assertEqual(3, result)

            status, result = rb_tree_module.execute(f'{RbTreeModule.MODULE_CMD_ADD} 7')
            self.assertEqual(0, status)
            self.assertEqual(7, result)

            status, result = rb_tree_module.execute(f'{RbTreeModule.MODULE_CMD_ADD} 4')
            self.assertEqual(0, status)
            self.assertEqual(4, result)
            
            status, result = rb_tree_module.execute(f'{RbTreeModule.MODULE_CMD_SEARCH} 3')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

    def test_print(self):
        '''
        The 'print' command test
        '''
        with RbTreeModule(path=MODULE_PATH) as rb_tree_module:
            status, result = rb_tree_module.execute(f'{RbTreeModule.MODULE_CMD_ADD} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = rb_tree_module.execute(f'{RbTreeModule.MODULE_CMD_ADD} 5')
            self.assertEqual(0, status)
            self.assertEqual(5, result)

            status, result = rb_tree_module.execute(f'{RbTreeModule.MODULE_CMD_ADD} 2')
            self.assertEqual(0, status)
            self.assertEqual(2, result)

            status, result = rb_tree_module.execute(f'{RbTreeModule.MODULE_CMD_ADD} 6')
            self.assertEqual(0, status)
            self.assertEqual(6, result)

            status, result = rb_tree_module.execute(f'{RbTreeModule.MODULE_CMD_ADD} 3')
            self.assertEqual(0, status)
            self.assertEqual(3, result)

            status, result = rb_tree_module.execute(f'{RbTreeModule.MODULE_CMD_ADD} 7')
            self.assertEqual(0, status)
            self.assertEqual(7, result)

            status, result = rb_tree_module.execute(f'{RbTreeModule.MODULE_CMD_ADD} 4')
            self.assertEqual(0, status)
            self.assertEqual(4, result)
            
            status, result = rb_tree_module.execute(RbTreeModule.MODULE_CMD_PRINT)
            self.assertEqual(0, status)
            self.assertEqual(0, result)

            _, func, msg = next(Dmesg.get_messages(RbTreeModule.MODULE_NAME, last=1))
            self.assertEqual("print_cmd_handler", func.strip())
            self.assertEqual("Values: 1 2 3 4 5 6 7", msg.strip())