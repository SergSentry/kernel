#!/usr/bin/env python3

import os
import time
import stat
import unittest

from test.modules.workqueue_module import WorkqueueModule
from test.tools.dmesg import Dmesg

MODULE_BUILD_DIR = "./build"
MODULE_PATH = f'{MODULE_BUILD_DIR}'


class TestWorkqueueModule(unittest.TestCase):

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
        with WorkqueueModule(path=MODULE_PATH) as workqueue_module:
            self.assertTrue(workqueue_module.has_loaded())

    def test_init_message(self):
        '''
        Checking the dmesg log for the module initialization string
        '''
        with WorkqueueModule(path=MODULE_PATH) as workqueue_module:
            _, func, msg = next(Dmesg.get_messages(WorkqueueModule.MODULE_NAME, last=1))

            self.assertEqual("ex_workqueue_init", func.strip())
            self.assertEqual("init", msg.strip())

    def test_exit_message(self):
        '''
        Checking the dmesg log for the module deinitialization string
        '''
        with WorkqueueModule(path=MODULE_PATH) as workqueue_module:
            pass

        _, func, msg = next(Dmesg.get_messages(WorkqueueModule.MODULE_NAME, last=1))

        self.assertEqual("ex_workqueue_exit", func.strip())
        self.assertEqual("exit", msg.strip())


    def test_permission(self):
        '''
        Check permission for parameters file /sys/module/<MODULE_NAME>/parameters/<NAME>
        '''
        with WorkqueueModule(path=MODULE_PATH) as workqueue_module:
            param = {
                workqueue_module._get_parameter_path(WorkqueueModule.MODULE_PARAM_CMD): 0o640,
                workqueue_module._get_parameter_path(WorkqueueModule.MODULE_PARAM_CMD_STATUS): 0o640,
                workqueue_module._get_parameter_path(WorkqueueModule.MODULE_PARAM_CMD_RESULT): 0o640,
            }

            for k, v in param.items():
                check_file = os.stat(k)
                self.assertTrue(bool(check_file.st_mode & v))

    def test_unknown_cmd_empty(self):
        '''
        The 'unknown_cmd' error command test. Act for empty command string
        '''
        with WorkqueueModule(path=MODULE_PATH) as workqueue_module:
            status, result = workqueue_module.execute("")
            self.assertEqual(-22, status)
            self.assertEqual(0, result)

    def test_unknown_cmd_start_with_space(self):
        '''
        The 'unknown_cmd' error command test. Act for command string with start space symbol
        '''
        with WorkqueueModule(path=MODULE_PATH) as workqueue_module:
            with self.assertRaises(OSError):
                 status, result = workqueue_module.execute(" "+WorkqueueModule.MODULE_CMD_RUN)

    def test_unknown_cmd_other(self):
        '''
        The 'unknown_cmd' error command test. Act for other command string
        '''
        with WorkqueueModule(path=MODULE_PATH) as workqueue_module:
            with self.assertRaises(OSError):
                 status, result = workqueue_module.execute("simsalabim")

    def test_run(self):
        '''
        The 'run' command test
        '''
        with WorkqueueModule(path=MODULE_PATH) as workqueue_module:
              status, result = workqueue_module.execute(WorkqueueModule.MODULE_CMD_RUN)
              self.assertEqual(0, status)
              self.assertEqual(0, result)

        ms_gen = Dmesg.get_messages(WorkqueueModule.MODULE_NAME, last=2)
        _, func, msg = next(ms_gen)
        self.assertEqual("reader_thread", func.strip())
        self.assertEqual("Worker thread stopped gracefully.", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("ex_workqueue_exit", func.strip())
        self.assertEqual("exit", msg.strip())

    def test_stop_before_run(self):
        '''
        The 'stop' command test, before run
        '''
        with WorkqueueModule(path=MODULE_PATH) as workqueue_module:
              status, result = workqueue_module.execute(WorkqueueModule.MODULE_CMD_STOP)
              self.assertEqual(0, status)
              self.assertEqual(0, result)

        ms_gen = Dmesg.get_messages(WorkqueueModule.MODULE_NAME, last=2)
        _, func, msg = next(ms_gen)
        self.assertEqual("ex_workqueue_init", func.strip())
        self.assertEqual("init", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("ex_workqueue_exit", func.strip())
        self.assertEqual("exit", msg.strip())

    def test_work(self):
        '''
        Check work 'run' and 'stop' command
        '''

        counter = 0
        with WorkqueueModule(path=MODULE_PATH) as workqueue_module:
              status, result = workqueue_module.execute(WorkqueueModule.MODULE_CMD_RUN)
              self.assertEqual(0, status)
              self.assertEqual(0, result)

              for i in range(5):
                  time.sleep(1)

              status, result = workqueue_module.execute(WorkqueueModule.MODULE_CMD_STOP)
              self.assertEqual(0, status)
              counter = result

        msg_counter = (counter*2)+4

        ms_gen = Dmesg.get_messages(WorkqueueModule.MODULE_NAME, last=msg_counter)
        _, func, msg = next(ms_gen)
        # TODO: Check shift message
        if "ex_workqueue_exit" == func.strip():
            _, func, msg = next(ms_gen)

        self.assertEqual("ex_workqueue_init", func.strip())
        self.assertEqual("init", msg.strip())

        index = 1
        while index <= counter:
            _, func, msg = next(ms_gen)
            self.assertEqual("my_callback_function", func.strip())
            self.assertEqual(f"Updated value to {index}", msg.strip())

            _, func, msg = next(ms_gen)
            self.assertEqual("reader_thread", func.strip())
            self.assertEqual(f"Fetched value is {index}", msg.strip())
            
            index += 1

        _, func, msg = next(ms_gen)
        self.assertEqual("reader_thread", func.strip())
        # TODO: Check shift message
        if "Timeout expired!" == msg.strip():
            _, func, msg = next(ms_gen)

        self.assertEqual("reader_thread", func.strip())
        self.assertEqual("Worker thread stopped gracefully.", msg.strip())

        _, func, msg = next(ms_gen)
        self.assertEqual("ex_workqueue_exit", func.strip())
        self.assertEqual("exit", msg.strip())

