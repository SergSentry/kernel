#!/usr/bin/env python3

import os
import stat
import unittest

from test.modules.list_module import ListModule
from test.tools.dmesg import Dmesg

MODULE_BUILD_DIR = "./build"
MODULE_PATH = f'{MODULE_BUILD_DIR}'


class TestListModule(unittest.TestCase):

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
        with ListModule(path=MODULE_PATH) as list_module:
            self.assertTrue(list_module.has_loaded())

    def test_init_message(self):
        '''
        Checking the dmesg log for the module initialization string
        '''
        with ListModule(path=MODULE_PATH) as list_module:
            _, func, msg = next(Dmesg.get_messages(ListModule.MODULE_NAME, last=1))

            self.assertEqual("ex_list_init", func.strip())
            self.assertEqual("init", msg.strip())

    def test_exit_message(self):
        '''
        Checking the dmesg log for the module deinitialization string
        '''
        with ListModule(path=MODULE_PATH) as list_module:
            pass

        _, func, msg = next(Dmesg.get_messages(ListModule.MODULE_NAME, last=1))

        self.assertEqual("ex_list_exit", func.strip())
        self.assertEqual("exit", msg.strip())

    def test_permission(self):
        '''
        Check permission for parameters file /sys/module/<MODULE_NAME>/parameters/<NAME>
        '''
        with ListModule(path=MODULE_PATH) as list_module:
            param = {
                list_module._get_parameter_path(ListModule.MODULE_PARAM_CMD): 0o640,
                list_module._get_parameter_path(ListModule.MODULE_PARAM_CMD_STATUS): 0o640,
                list_module._get_parameter_path(ListModule.MODULE_PARAM_CMD_RESULT): 0o640,
            }

            for k, v in param.items():
                check_file = os.stat(k)
                self.assertTrue(bool(check_file.st_mode & v))

    def test_unknown_cmd_empty(self):
        '''
        The 'unknown_cmd' error command test. Act for empty command string
        '''
        with ListModule(path=MODULE_PATH) as list_module:
            status, result = list_module.execute("")
            self.assertEqual(-22, status)
            self.assertEqual(0, result)

    def test_unknown_cmd_start_with_space(self):
        '''
        The 'unknown_cmd' error command test. Act for command string with start space symbol
        '''
        with ListModule(path=MODULE_PATH) as list_module:
            with self.assertRaises(OSError):
                 status, result = list_module.execute(" "+ListModule.MODULE_CMD_EMPTY)

    def test_unknown_cmd_other(self):
        '''
        The 'unknown_cmd' error command test. Act for other command string
        '''
        with ListModule(path=MODULE_PATH) as list_module:
            with self.assertRaises(OSError):
                 status, result = list_module.execute("simsalabim")

    def test_empty(self):
        '''
        The 'empty' command test
        '''
        with ListModule(path=MODULE_PATH) as list_module:
            status, result = list_module.execute(ListModule.MODULE_CMD_EMPTY)
            self.assertEqual(0, status)
            self.assertEqual(1, result)

    def test_zero_size(self):
        '''
        The zero 'size' command test
        '''
        with ListModule(path=MODULE_PATH) as list_module:
            status, result = list_module.execute(ListModule.MODULE_CMD_SIZE)
            self.assertEqual(0, status)
            self.assertEqual(0, result)
    
    def test_clear(self):
        '''
        The 'clear' command test
        '''
        with ListModule(path=MODULE_PATH) as list_module:
            status, result = list_module.execute(f'{ListModule.MODULE_CMD_ADD} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = list_module.execute(ListModule.MODULE_CMD_CLEAR)
            self.assertEqual(0, status)
            self.assertEqual(0, result)

            status, result = list_module.execute(ListModule.MODULE_CMD_EMPTY)
            self.assertEqual(0, status)
            self.assertEqual(1, result)

    def test_no_empty(self):
        '''
        The no 'empty' command test
        '''
        with ListModule(path=MODULE_PATH) as list_module:
            status, result = list_module.execute(f'{ListModule.MODULE_CMD_TADD} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = list_module.execute(ListModule.MODULE_CMD_EMPTY)
            self.assertEqual(0, status)
            self.assertEqual(0, result)

    def test_size(self):
        '''
        The 'size' command test
        '''
        with ListModule(path=MODULE_PATH) as list_module:
            status, result = list_module.execute(f'{ListModule.MODULE_CMD_TADD} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = list_module.execute(ListModule.MODULE_CMD_SIZE)
            self.assertEqual(0, status)
            self.assertEqual(1, result)

    def test_add(self):
        '''
        The add 'add' command test 
        '''
        with ListModule(path=MODULE_PATH) as list_module:
            status, result = list_module.execute(f'{ListModule.MODULE_CMD_ADD} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = list_module.execute(f'{ListModule.MODULE_CMD_ADD} 2')
            self.assertEqual(0, status)
            self.assertEqual(2, result)

            status, result = list_module.execute(f'{ListModule.MODULE_CMD_ADD} 3')
            self.assertEqual(0, status)
            self.assertEqual(3, result)

            status, result = list_module.execute(ListModule.MODULE_CMD_PRINT)
            self.assertEqual(0, status)
            self.assertEqual(0, result)

            _, func, msg = next(Dmesg.get_messages(ListModule.MODULE_NAME, last=1))
            self.assertEqual("print_cmd_handler", func.strip())
            self.assertEqual("Values: 3 2 1", msg.strip())

    def test_tadd(self):
        '''
        The add to tail 'tadd' command test 
        '''
        with ListModule(path=MODULE_PATH) as list_module:
            status, result = list_module.execute(f'{ListModule.MODULE_CMD_TADD} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = list_module.execute(f'{ListModule.MODULE_CMD_TADD} 2')
            self.assertEqual(0, status)
            self.assertEqual(2, result)

            status, result = list_module.execute(f'{ListModule.MODULE_CMD_TADD} 3')
            self.assertEqual(0, status)
            self.assertEqual(3, result)

            status, result = list_module.execute(ListModule.MODULE_CMD_PRINT)
            self.assertEqual(0, status)
            self.assertEqual(0, result)

            _, func, msg = next(Dmesg.get_messages(ListModule.MODULE_NAME, last=1))
            self.assertEqual("print_cmd_handler", func.strip())
            self.assertEqual("Values: 1 2 3", msg.strip())

    def test_sadd(self):
        '''
        The add and sort 'sadd' command test 
        '''
        with ListModule(path=MODULE_PATH) as list_module:
            status, result = list_module.execute(f'{ListModule.MODULE_CMD_SADD} 3')
            self.assertEqual(0, status)
            self.assertEqual(3, result)

            status, result = list_module.execute(f'{ListModule.MODULE_CMD_SADD} 8')
            self.assertEqual(0, status)
            self.assertEqual(8, result)

            status, result = list_module.execute(f'{ListModule.MODULE_CMD_SADD} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = list_module.execute(ListModule.MODULE_CMD_PRINT)
            self.assertEqual(0, status)
            self.assertEqual(0, result)

            _, func, msg = next(Dmesg.get_messages(ListModule.MODULE_NAME, last=1))
            self.assertEqual("print_cmd_handler", func.strip())
            self.assertEqual("Values: 8 3 1", msg.strip())

    def test_next(self):
        '''
        The navy 'next' command test 
        '''
        with ListModule(path=MODULE_PATH) as list_module:
            status, result = list_module.execute(f'{ListModule.MODULE_CMD_TADD} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)
            
            status, result = list_module.execute(f'{ListModule.MODULE_CMD_TADD} 2')
            self.assertEqual(0, status)
            self.assertEqual(2, result)

            status, result = list_module.execute(ListModule.MODULE_CMD_NEXT)
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = list_module.execute(ListModule.MODULE_CMD_NEXT)
            self.assertEqual(0, status)
            self.assertEqual(2, result)

            # Act for test cycle next
            status, result = list_module.execute(ListModule.MODULE_CMD_NEXT)
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = list_module.execute(ListModule.MODULE_CMD_NEXT)           
            self.assertEqual(0, status)
            self.assertEqual(2, result)

    def test_next_error(self):
        '''
        Checking 'next' command with empty list
        '''
        with ListModule(path=MODULE_PATH) as list_module:
            with self.assertRaises(OSError):
                status, result = list_module.execute(ListModule.MODULE_CMD_NEXT)

    def test_prev(self):
        '''
        The navy 'prev' command test 
        '''
        with ListModule(path=MODULE_PATH) as list_module:
            status, result = list_module.execute(f'{ListModule.MODULE_CMD_TADD} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)
            
            status, result = list_module.execute(f'{ListModule.MODULE_CMD_TADD} 2')
            self.assertEqual(0, status)
            self.assertEqual(2, result)

            status, result = list_module.execute(ListModule.MODULE_CMD_PREV)
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = list_module.execute(ListModule.MODULE_CMD_PREV)
            self.assertEqual(0, status)
            self.assertEqual(2, result)

            # Act for test cycle next
            status, result = list_module.execute(ListModule.MODULE_CMD_PREV)   
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = list_module.execute(ListModule.MODULE_CMD_PREV)
            self.assertEqual(0, status)
            self.assertEqual(2, result)

    def test_prev_error(self):
        '''
        Checking 'prev' command with empty list
        '''
        with ListModule(path=MODULE_PATH) as list_module:
            with self.assertRaises(OSError):
                status, result = list_module.execute(ListModule.MODULE_CMD_PREV)

    def test_del(self):
        '''
        The 'del' command test
        '''
        with ListModule(path=MODULE_PATH) as list_module:
            status, result = list_module.execute(f'{ListModule.MODULE_CMD_TADD} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = list_module.execute(ListModule.MODULE_CMD_SIZE)
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = list_module.execute(f'{ListModule.MODULE_CMD_DEL} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = list_module.execute(ListModule.MODULE_CMD_SIZE)
            self.assertEqual(0, status)
            self.assertEqual(0, result)
