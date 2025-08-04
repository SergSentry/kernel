#!/usr/bin/env python3

import os
import time
import stat
import unittest

from test.modules.waiter_module import WaiterModule
from test.tools.dmesg import Dmesg

MODULE_BUILD_DIR = "./build"
MODULE_PATH = f'{MODULE_BUILD_DIR}'


class TestWaiterModule(unittest.TestCase):

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
        with WaiterModule(path=MODULE_PATH) as wait_module:
            self.assertTrue(wait_module.has_loaded())

    def test_init_message(self):
        '''
        Checking the dmesg log for the module initialization string
        '''
        with WaiterModule(path=MODULE_PATH) as wait_module:
            _, func, msg = next(Dmesg.get_messages(WaiterModule.MODULE_NAME, last=1))

            self.assertEqual("ex_waiter_init", func.strip())
            self.assertEqual("init", msg.strip())

    def test_exit_message(self):
        '''
        Checking the dmesg log for the module deinitialization string
        '''
        with WaiterModule(path=MODULE_PATH) as wait_module:
            pass

        _, func, msg = next(Dmesg.get_messages(WaiterModule.MODULE_NAME, last=1))

        self.assertEqual("ex_waiter_exit", func.strip())
        self.assertEqual("exit", msg.strip())


    def test_permission(self):
        '''
        Check permission for parameters file /sys/module/<MODULE_NAME>/parameters/<NAME>
        '''
        with WaiterModule(path=MODULE_PATH) as wait_module:
            param = {
                wait_module._get_parameter_path(WaiterModule.MODULE_PARAM_CMD): 0o640,
                wait_module._get_parameter_path(WaiterModule.MODULE_PARAM_CMD_STATUS): 0o640,
                wait_module._get_parameter_path(WaiterModule.MODULE_PARAM_CMD_RESULT): 0o640,
            }

            for k, v in param.items():
                check_file = os.stat(k)
                self.assertTrue(bool(check_file.st_mode & v))

    def test_unknown_cmd_empty(self):
        '''
        The 'unknown_cmd' error command test. Act for empty command string
        '''
        with WaiterModule(path=MODULE_PATH) as wait_module:
            status, result = wait_module.execute("")
            self.assertEqual(-22, status)
            self.assertEqual(0, result)

    def test_unknown_cmd_start_with_space(self):
        '''
        The 'unknown_cmd' error command test. Act for command string with start space symbol
        '''
        with WaiterModule(path=MODULE_PATH) as wait_module:
            with self.assertRaises(OSError):
                 status, result = wait_module.execute(" "+WaiterModule.MODULE_CMD_RUN)

    def test_unknown_cmd_other(self):
        '''
        The 'unknown_cmd' error command test. Act for other command string
        '''
        with WaiterModule(path=MODULE_PATH) as wait_module:
            with self.assertRaises(OSError):
                 status, result = wait_module.execute("simsalabim")

    def test_run(self):
        '''
        The 'run' command test
        '''
        with WaiterModule(path=MODULE_PATH) as wait_module:
              status, result = wait_module.execute(WaiterModule.MODULE_CMD_RUN)
              self.assertEqual(0, status)
              self.assertEqual(0, result)

        ms_gen = Dmesg.get_messages(WaiterModule.MODULE_NAME, last=4)
        _, func, msg = next(ms_gen)
        self.assertEqual("waiter_thread", func.strip())
        self.assertEqual("Waiting for event...", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("waiter_thread", func.strip())
        self.assertEqual("Timeout expired!", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("waiter_thread", func.strip())
        self.assertEqual("Worker thread stopped gracefully.", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("ex_waiter_exit", func.strip())
        self.assertEqual("exit", msg.strip())

    def test_stop_before_run(self):
        '''
        The 'stop' command test, before run
        '''
        with WaiterModule(path=MODULE_PATH) as wait_module:
              status, result = wait_module.execute(WaiterModule.MODULE_CMD_STOP)
              self.assertEqual(0, status)
              self.assertEqual(0, result)

        ms_gen = Dmesg.get_messages(WaiterModule.MODULE_NAME, last=3)
        _, func, msg = next(ms_gen)
        self.assertEqual("ex_waiter_exit", func.strip())
        self.assertEqual("exit", msg.strip())

    def test_work(self):
        '''
        Check work 'run' and 'stop' command
        '''

        counter = 0
        with WaiterModule(path=MODULE_PATH) as wait_module:
              status, result = wait_module.execute(WaiterModule.MODULE_CMD_RUN)
              self.assertEqual(0, status)
              self.assertEqual(0, result)

              time.sleep(2)

              status, result = wait_module.execute(WaiterModule.MODULE_CMD_OCCURRE)
              self.assertEqual(0, status)
              counter = result

        ms_gen = Dmesg.get_messages(WaiterModule.MODULE_NAME, last=4)
        _, func, msg = next(ms_gen)
        self.assertEqual("waiter_thread", func.strip())
        self.assertEqual("Waiting for event...", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("waiter_thread", func.strip())
        self.assertEqual("Event received!", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("waiter_thread", func.strip())
        self.assertEqual("Worker thread stopped gracefully.", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("ex_waiter_exit", func.strip())
        self.assertEqual("exit", msg.strip())

