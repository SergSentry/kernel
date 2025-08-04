#!/usr/bin/env python3

import os
import time
import stat
import unittest

from test.modules.rwlock_module import RwLockModule
from test.tools.dmesg import Dmesg

MODULE_BUILD_DIR = "./build"
MODULE_PATH = f'{MODULE_BUILD_DIR}'


class TestRwLockModule(unittest.TestCase):

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
        with RwLockModule(path=MODULE_PATH) as rwlock_module:
            self.assertTrue(rwlock_module.has_loaded())

    def test_init_message(self):
        '''
        Checking the dmesg log for the module initialization string
        '''
        with RwLockModule(path=MODULE_PATH) as rwlock_module:
            _, func, msg = next(Dmesg.get_messages(RwLockModule.MODULE_NAME, last=1))

            self.assertEqual("ex_rwlock_init", func.strip())
            self.assertEqual("init", msg.strip())

    def test_exit_message(self):
        '''
        Checking the dmesg log for the module deinitialization string
        '''
        with RwLockModule(path=MODULE_PATH) as rwlock_module:
            pass

        _, func, msg = next(Dmesg.get_messages(RwLockModule.MODULE_NAME, last=1))

        self.assertEqual("ex_rwlock_exit", func.strip())
        self.assertEqual("exit", msg.strip())


    def test_permission(self):
        '''
        Check permission for parameters file /sys/module/<MODULE_NAME>/parameters/<NAME>
        '''
        with RwLockModule(path=MODULE_PATH) as rwlock_module:
            param = {
                rwlock_module._get_parameter_path(RwLockModule.MODULE_PARAM_CMD): 0o640,
                rwlock_module._get_parameter_path(RwLockModule.MODULE_PARAM_CMD_STATUS): 0o640,
                rwlock_module._get_parameter_path(RwLockModule.MODULE_PARAM_CMD_RESULT): 0o640,
            }

            for k, v in param.items():
                check_file = os.stat(k)
                self.assertTrue(bool(check_file.st_mode & v))

    def test_unknown_cmd_empty(self):
        '''
        The 'unknown_cmd' error command test. Act for empty command string
        '''
        with RwLockModule(path=MODULE_PATH) as rwlock_module:
            status, result = rwlock_module.execute("")
            self.assertEqual(-22, status)
            self.assertEqual(0, result)

    def test_unknown_cmd_start_with_space(self):
        '''
        The 'unknown_cmd' error command test. Act for command string with start space symbol
        '''
        with RwLockModule(path=MODULE_PATH) as rwlock_module:
            with self.assertRaises(OSError):
                 status, result = rwlock_module.execute(" "+RwLockModule.MODULE_CMD_RUN)

    def test_unknown_cmd_other(self):
        '''
        The 'unknown_cmd' error command test. Act for other command string
        '''
        with RwLockModule(path=MODULE_PATH) as rwlock_module:
            with self.assertRaises(OSError):
                 status, result = rwlock_module.execute("simsalabim")

    def test_run(self):
        '''
        The 'run' command test
        '''
        with RwLockModule(path=MODULE_PATH) as rwlock_module:
              status, result = rwlock_module.execute(RwLockModule.MODULE_CMD_RUN)
              self.assertEqual(0, status)
              self.assertEqual(0, result)

        ms_gen = Dmesg.get_messages(RwLockModule.MODULE_NAME, last=3)
        _, func, msg = next(ms_gen)
        self.assertEqual("reader_thread", func.strip())
        self.assertEqual("Worker thread stopped gracefully.", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("writer_thread", func.strip())
        self.assertEqual("Worker thread stopped gracefully.", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("ex_rwlock_exit", func.strip())
        self.assertEqual("exit", msg.strip())

    def test_stop_before_run(self):
        '''
        The 'stop' command test, before run
        '''
        with RwLockModule(path=MODULE_PATH) as rwlock_module:
              status, result = rwlock_module.execute(RwLockModule.MODULE_CMD_STOP)
              self.assertEqual(0, status)
              self.assertEqual(0, result)

        ms_gen = Dmesg.get_messages(RwLockModule.MODULE_NAME, last=3)
        _, func, msg = next(ms_gen)
        self.assertEqual("ex_rwlock_exit", func.strip())
        self.assertEqual("exit", msg.strip())

    def test_work(self):
        '''
        Check work 'run' and 'stop' command
        '''

        counter = 0
        with RwLockModule(path=MODULE_PATH) as rwlock_module:
              status, result = rwlock_module.execute(RwLockModule.MODULE_CMD_RUN)
              self.assertEqual(0, status)
              self.assertEqual(0, result)

              for i in range(5):
                  time.sleep(1)

              status, result = rwlock_module.execute(RwLockModule.MODULE_CMD_STOP)
              self.assertEqual(0, status)
              counter = result

        msg_counter = (counter*2)+3
        ms_gen = Dmesg.get_messages(RwLockModule.MODULE_NAME, last=msg_counter)

        index = 1
        while index <= counter:
            _, func, msg = next(ms_gen)
            self.assertEqual("writer_thread", func.strip())
            self.assertEqual(f"Updated value to {index}", msg.strip())
            _, func, msg = next(ms_gen)
            self.assertEqual("reader_thread", func.strip())
            self.assertEqual(f"Fetched value is {index}", msg.strip())
            index += 1

        _, func, msg = next(ms_gen)
        self.assertEqual("reader_thread", func.strip())
        self.assertEqual("Worker thread stopped gracefully.", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("writer_thread", func.strip())
        self.assertEqual("Worker thread stopped gracefully.", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("ex_rwlock_exit", func.strip())
        self.assertEqual("exit", msg.strip())

