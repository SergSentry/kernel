#!/usr/bin/env python

import os
import stat
import unittest

from test.modules.stack_module import StackModule
from test.tools.dmesg import Dmesg

MODULE_BUILD_DIR = "./build"
MODULE_PATH = f'{MODULE_BUILD_DIR}'


class TestStackModule(unittest.TestCase):

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
        with StackModule(path=MODULE_PATH) as stack_module:
            self.assertTrue(stack_module.has_loaded())

    def test_init_message_new(self):
        '''
        Checking the dmesg log for the module initialization string
        '''
        with StackModule(path=MODULE_PATH) as stack_module:
            _, func, msg = next(Dmesg.get_messages(StackModule.MODULE_NAME, last=1))

            self.assertEqual("ex_stack_init", func.strip())
            self.assertEqual("init", msg.strip())

    def test_exit_message(self):
        '''
        Checking the dmesg log for the module deinitialization string
        '''
        with StackModule(path=MODULE_PATH) as stack_module:
            pass

        _, func, msg = next(Dmesg.get_messages(StackModule.MODULE_NAME, last=1))

        self.assertEqual("ex_stack_exit", func.strip())
        self.assertEqual("exit", msg.strip())

    def test_permission(self):
        '''
        Check permission for parameters file /sys/module/<MODULE_NAME>/parameters/<NAME>
        '''
        with StackModule(path=MODULE_PATH) as stack_module:
            param = {
                stack_module._get_parameter_path(StackModule.MODULE_PARAM_CMD): 0o640,
                stack_module._get_parameter_path(StackModule.MODULE_PARAM_CMD_STATUS): 0o640,
                stack_module._get_parameter_path(StackModule.MODULE_PARAM_CMD_RESULT): 0o640,
            }

            for k, v in param.items():
                check_file = os.stat(k)
                self.assertTrue(bool(check_file.st_mode & v))

    def test_unknown_cmd_empty(self):
        '''
        The 'unknown_cmd' error command test. Act for empty command string
        '''
        with StackModule(path=MODULE_PATH) as stack_module:
            status, result = stack_module.execute("")
            self.assertEqual(-22, status)
            self.assertEqual(0, result)

    def test_unknown_cmd_start_with_space(self):
        '''
        The 'unknown_cmd' error command test. Act for command string with start space symbol
        '''
        with StackModule(path=MODULE_PATH) as stack_module:
            with self.assertRaises(OSError):
                 status, result = stack_module.execute(" "+StackModule.MODULE_CMD_EMPTY)

    def test_unknown_cmd_other(self):
        '''
        The 'unknown_cmd' error command test. Act for other command string
        '''
        with StackModule(path=MODULE_PATH) as stack_module:
            with self.assertRaises(OSError):
                 status, result = stack_module.execute("simsalabim")

    def test_empty(self):
        '''
        The 'empty' command test
        '''
        with StackModule(path=MODULE_PATH) as stack_module:
            status, result = stack_module.execute(StackModule.MODULE_CMD_EMPTY)
            self.assertEqual(0, status)
            self.assertEqual(1, result)

    def test_zero_size(self):
        '''
        The zero 'size' command test
        '''
        with StackModule(path=MODULE_PATH) as stack_module:
            status, result = stack_module.execute(StackModule.MODULE_CMD_SIZE)
            self.assertEqual(0, status)
            self.assertEqual(0, result)
    
    def test_clear(self):
        '''
        The 'clear' command test
        '''
        with StackModule(path=MODULE_PATH) as stack_module:
            status, result = stack_module.execute(f'{StackModule.MODULE_CMD_PUSH} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = stack_module.execute(StackModule.MODULE_CMD_CLEAR)
            self.assertEqual(0, status)
            self.assertEqual(0, result)

            status, result = stack_module.execute(StackModule.MODULE_CMD_EMPTY)
            self.assertEqual(0, status)
            self.assertEqual(1, result)

    def test_no_empty(self):
        '''
        The no 'push' command test
        '''
        with StackModule(path=MODULE_PATH) as stack_module:
            status, result = stack_module.execute(f'{StackModule.MODULE_CMD_PUSH} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = stack_module.execute(StackModule.MODULE_CMD_EMPTY)
            self.assertEqual(0, status)
            self.assertEqual(0, result)

    def test_size(self):
        '''
        The 'size' command test
        '''
        with StackModule(path=MODULE_PATH) as stack_module:
            status, result = stack_module.execute(f'{StackModule.MODULE_CMD_PUSH} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = stack_module.execute(StackModule.MODULE_CMD_SIZE)
            self.assertEqual(0, status)
            self.assertEqual(1, result)

    def test_empty_top(self):
        '''
        The empty 'top' command test
        '''
        with StackModule(path=MODULE_PATH) as stack_module:
            with self.assertRaises(OSError):
                 status, result = stack_module.execute(StackModule.MODULE_CMD_TOP)

    def test_top(self):
        '''
        The empty 'top' command test
        '''
        with StackModule(path=MODULE_PATH) as stack_module:
            status, result = stack_module.execute(f'{StackModule.MODULE_CMD_PUSH} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)
            status, result = stack_module.execute(StackModule.MODULE_CMD_TOP)
            self.assertEqual(0, status)
            self.assertEqual(1, result)
            status, result = stack_module.execute(StackModule.MODULE_CMD_SIZE)
            self.assertEqual(0, status)
            self.assertEqual(1, result)

    def test_push(self):
        '''
        The 'push' command test
        '''
        with StackModule(path=MODULE_PATH) as stack_module:
            status, result = stack_module.execute(f'{StackModule.MODULE_CMD_PUSH} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

    def test_pop(self):
        '''
        The 'pop' command test
        '''
        with StackModule(path=MODULE_PATH) as stack_module:
            status, result = stack_module.execute(f'{StackModule.MODULE_CMD_PUSH} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = stack_module.execute(StackModule.MODULE_CMD_POP)
            self.assertEqual(0, status)
            self.assertEqual(1, result)

    def test_push_pop(self):
        '''
        The 'pop' command test
        '''
        with StackModule(path=MODULE_PATH) as stack_module:
            status, result = stack_module.execute(f'{StackModule.MODULE_CMD_PUSH} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = stack_module.execute(f'{StackModule.MODULE_CMD_PUSH} 2')
            self.assertEqual(0, status)
            self.assertEqual(2, result)

            status, result = stack_module.execute(f'{StackModule.MODULE_CMD_PUSH} 3')
            self.assertEqual(0, status)
            self.assertEqual(3, result)

            status, result = stack_module.execute(StackModule.MODULE_CMD_POP)
            self.assertEqual(0, status)
            self.assertEqual(3, result)

            status, result = stack_module.execute(StackModule.MODULE_CMD_POP)
            self.assertEqual(0, status)
            self.assertEqual(2, result)

            status, result = stack_module.execute(StackModule.MODULE_CMD_POP)
            self.assertEqual(0, status)
            self.assertEqual(1, result)

    def test_print(self):
        '''
        Check print
        '''
        with StackModule(path=MODULE_PATH) as stack_module:
            status, result = stack_module.execute(f'{StackModule.MODULE_CMD_PUSH} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = stack_module.execute(f'{StackModule.MODULE_CMD_PUSH} 2')
            self.assertEqual(0, status)
            self.assertEqual(2, result)

            status, result = stack_module.execute(f'{StackModule.MODULE_CMD_PUSH} 3')
            self.assertEqual(0, status)
            self.assertEqual(3, result)

            status, result = stack_module.execute(StackModule.MODULE_CMD_PRINT)
            self.assertEqual(0, status)
            self.assertEqual(0, result)

            _, func, msg = next(Dmesg.get_messages(StackModule.MODULE_NAME, last=1))
            self.assertEqual("print_cmd_handler", func.strip())
            self.assertEqual("Values: 3 2 1", msg.strip())

    def test_bracet(self):
        '''
        Check bracet
        '''
        param = {
            "": 0,
            "(": 1,
            "{": 1,
            "[": 1,
            ")": 1,
            "}": 1,
            "]": 1,
            "()": 0,
            "{}": 0,
            "[]": 0,
            "({[]})": 0,
            "({[": 1,
            ")]}": 1,
            "({[)]})": 1,
            "[([])({})]": 0,
        }

        with StackModule(path=MODULE_PATH) as stack_module:
            for k, v in param.items():
                status, result = stack_module.execute(f'{StackModule.MODULE_CMD_BRACKET} {k}')
                self.assertEqual(0, status)
                self.assertEqual(v, result)
