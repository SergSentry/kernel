#!/usr/bin/env python

import os
import stat
import unittest

from test.modules.queue_module import QueueModule
from test.tools.dmesg import Dmesg

MODULE_BUILD_DIR = "./build"
MODULE_PATH = f'{MODULE_BUILD_DIR}'


class TestQueueModule(unittest.TestCase):

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
        with QueueModule(path=MODULE_PATH) as queue_module:
            self.assertTrue(queue_module.has_loaded())

    def test_init_message(self):
        '''
        Checking the dmesg log for the module initialization string
        '''
        with QueueModule(path=MODULE_PATH) as queue_module:
            _, func, msg = next(Dmesg.get_messages(QueueModule.MODULE_NAME, last=1))

            self.assertEqual("ex_queue_init", func.strip())
            self.assertEqual("init", msg.strip())

    def test_exit_message(self):
        '''
        Checking the dmesg log for the module deinitialization string
        '''
        with QueueModule(path=MODULE_PATH) as queue_module:
            pass

        _, func, msg = next(Dmesg.get_messages(QueueModule.MODULE_NAME, last=1))

        self.assertEqual("ex_queue_exit", func.strip())
        self.assertEqual("exit", msg.strip())

    def test_permission(self):
        '''
        Check permission for parameters file /sys/module/<MODULE_NAME>/parameters/<NAME>
        '''
        with QueueModule(path=MODULE_PATH) as queue_module:
            param = {
                queue_module._get_parameter_path(QueueModule.MODULE_PARAM_CMD): 0o640,
                queue_module._get_parameter_path(QueueModule.MODULE_PARAM_CMD_STATUS): 0o640,
                queue_module._get_parameter_path(QueueModule.MODULE_PARAM_CMD_RESULT): 0o640,
            }

            for k, v in param.items():
                check_file = os.stat(k)
                self.assertTrue(bool(check_file.st_mode & v))

    def test_unknown_cmd_empty(self):
        '''
        The 'unknown_cmd' error command test. Act for empty command string
        '''
        with QueueModule(path=MODULE_PATH) as queue_module:
            status, result = queue_module.execute("")
            self.assertEqual(-22, status)
            self.assertEqual(0, result)

    def test_unknown_cmd_start_with_space(self):
        '''
        The 'unknown_cmd' error command test. Act for command string with start space symbol
        '''
        with QueueModule(path=MODULE_PATH) as queue_module:
            with self.assertRaises(OSError):
                 status, result = queue_module.execute(" "+QueueModule.MODULE_CMD_IS_EMPTY)

    def test_unknown_cmd_other(self):
        '''
        The 'unknown_cmd' error command test. Act for other command string
        '''
        with QueueModule(path=MODULE_PATH) as queue_module:
            with self.assertRaises(OSError):
                 status, result = queue_module.execute("simsalabim")

    def test_is_empty(self):
        '''
        The 'is_empty' command test
        '''
        with QueueModule(path=MODULE_PATH) as queue_module:
            status, result = queue_module.execute(QueueModule.MODULE_CMD_IS_EMPTY)
            self.assertEqual(0, status)
            self.assertEqual(1, result)

    def test_no_is_empty(self):
        '''
        The no 'is_empty' command test
        '''
        with QueueModule(path=MODULE_PATH) as queue_module:
            status, result = queue_module.execute(f'{QueueModule.MODULE_CMD_PUSH} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = queue_module.execute(QueueModule.MODULE_CMD_IS_EMPTY)
            self.assertEqual(0, status)
            self.assertEqual(0, result)

    def test_full_size(self):
        '''
        The full 'size' command test
        '''
        with QueueModule(path=MODULE_PATH) as queue_module:
            status, result = queue_module.execute(QueueModule.MODULE_CMD_SIZE)
            self.assertEqual(0, status)
            self.assertEqual(64, result)

    def test_size(self):
        '''
        The 'size' command test
        '''
        with QueueModule(path=MODULE_PATH) as queue_module:
            status, result = queue_module.execute(f'{QueueModule.MODULE_CMD_PUSH} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = queue_module.execute(QueueModule.MODULE_CMD_SIZE)
            self.assertEqual(0, status)
            self.assertEqual(64, result)

    def test_full_avail(self):
        '''
        The full 'avail' command test
        '''
        with QueueModule(path=MODULE_PATH) as queue_module:
            status, result = queue_module.execute(QueueModule.MODULE_CMD_AVAIL)
            self.assertEqual(0, status)
            self.assertEqual(64, result)

    def test_avail(self):
        '''
        The 'avail' command test
        '''
        with QueueModule(path=MODULE_PATH) as queue_module:
            status, result = queue_module.execute(f'{QueueModule.MODULE_CMD_PUSH} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = queue_module.execute(QueueModule.MODULE_CMD_AVAIL)
            self.assertEqual(0, status)
            self.assertEqual(63, result)

    def test_push(self):
        '''
        The 'push' command test
        '''
        with QueueModule(path=MODULE_PATH) as queue_module:
            status, result = queue_module.execute(f'{QueueModule.MODULE_CMD_PUSH} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

    def test_pop(self):
        '''
        The 'pop' command test
        '''
        with QueueModule(path=MODULE_PATH) as queue_module:
            status, result = queue_module.execute(f'{QueueModule.MODULE_CMD_PUSH} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = queue_module.execute(QueueModule.MODULE_CMD_POP)
            self.assertEqual(0, status)
            self.assertEqual(1, result)

    def test_peek(self):
        '''
        The 'peek' command test
        '''
        with QueueModule(path=MODULE_PATH) as queue_module:
            status, result = queue_module.execute(f'{QueueModule.MODULE_CMD_PUSH} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

            status, result = queue_module.execute(QueueModule.MODULE_CMD_PEEK)
            self.assertEqual(0, status)
            self.assertEqual(1, result)
