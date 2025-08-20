#!/usr/bin/env python3

import os
import time
import stat
import unittest

from test.modules.time_module import TimeModule
from test.tools.dmesg import Dmesg

MODULE_BUILD_DIR = "./build"
MODULE_PATH = f'{MODULE_BUILD_DIR}'


class TestTimeModule(unittest.TestCase):

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
        with TimeModule(path=MODULE_PATH) as time_module:
            self.assertTrue(time_module.has_loaded())

    def test_init_message(self):
        '''
        Checking the dmesg log for the module initialization string
        '''
        Dmesg.clear()
        with TimeModule(path=MODULE_PATH) as time_module:
            _, func, msg = next(Dmesg.get_messages(TimeModule.MODULE_NAME, last=1))

            self.assertEqual("ex_timer_init", func.strip())
            self.assertEqual("init", msg.strip())

    def test_exit_message(self):
        '''
        Checking the dmesg log for the module deinitialization string
        '''
        Dmesg.clear()
        with TimeModule(path=MODULE_PATH) as time_module:
            pass

        _, func, msg = next(Dmesg.get_messages(TimeModule.MODULE_NAME, last=1))

        self.assertEqual("ex_timer_exit", func.strip())
        self.assertEqual("exit", msg.strip())


    def test_permission(self):
        '''
        Check permission for parameters file /sys/module/<MODULE_NAME>/parameters/<NAME>
        '''
        with TimeModule(path=MODULE_PATH) as time_module:
            param = {
                time_module._get_parameter_path(TimeModule.MODULE_PARAM_CMD): 0o640,
                time_module._get_parameter_path(TimeModule.MODULE_PARAM_CMD_STATUS): 0o640,
                time_module._get_parameter_path(TimeModule.MODULE_PARAM_CMD_RESULT): 0o640,
            }

            for k, v in param.items():
                check_file = os.stat(k)
                self.assertTrue(bool(check_file.st_mode & v))

    def test_unknown_cmd_empty(self):
        '''
        The 'unknown_cmd' error command test. Act for empty command string
        '''
        with TimeModule(path=MODULE_PATH) as time_module:
            status, result = time_module.execute("")
            self.assertEqual(-22, status)
            self.assertEqual(0, result)

    def test_unknown_cmd_start_with_space(self):
        '''
        The 'unknown_cmd' error command test. Act for command string with start space symbol
        '''
        with TimeModule(path=MODULE_PATH) as time_module:
            with self.assertRaises(OSError):
                 status, result = time_module.execute(" "+TimeModule.MODULE_CMD_RUN)

    def test_unknown_cmd_other(self):
        '''
        The 'unknown_cmd' error command test. Act for other command string
        '''
        with TimeModule(path=MODULE_PATH) as time_module:
            with self.assertRaises(OSError):
                 status, result = time_module.execute("simsalabim")

    def test_set_period(self):
        '''
        The navy 'period' command test 
        '''
        with TimeModule(path=MODULE_PATH) as time_module:
            status, result = time_module.execute(f'{TimeModule.MODULE_CMD_PERIOD} 5')
            self.assertEqual(0, status)
            self.assertEqual(5, result)

    def test_set_duty(self):
        '''
        The navy 'duty' command test 
        '''
        with TimeModule(path=MODULE_PATH) as time_module:
            status, result = time_module.execute(f'{TimeModule.MODULE_CMD_DUTY} 1')
            self.assertEqual(0, status)
            self.assertEqual(1, result)

    def test_run(self):
        '''
        The 'run' command test
        '''
        Dmesg.clear()
        default_duty = 5
        with TimeModule(path=MODULE_PATH) as time_module:
              status, result = time_module.execute(TimeModule.MODULE_CMD_RUN)
              self.assertEqual(0, status)
              self.assertEqual(0, result)
              for i in range(default_duty):
                   time.sleep(62)
              status, result = time_module.execute(TimeModule.MODULE_CMD_STOP)
              self.assertEqual(0, status)
              self.assertEqual(0, result)

        ms_gen = Dmesg.get_reg_messages_by_func(TimeModule.MODULE_NAME, "pulse_callback", "min=\\d{1,3}:\\sHello, timer!")
        _, func, msg = next(ms_gen)
        self.assertEqual("pulse_callback", func.strip())
        self.assertEqual("min=30: Hello, timer!", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("pulse_callback", func.strip())
        self.assertEqual("min=60: Hello, timer!", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("pulse_callback", func.strip())
        self.assertEqual("min=90: Hello, timer!", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("pulse_callback", func.strip())
        self.assertEqual("min=120: Hello, timer!", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("pulse_callback", func.strip())
        self.assertEqual("min=150: Hello, timer!", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("pulse_callback", func.strip())
        self.assertEqual("min=180: Hello, timer!", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("pulse_callback", func.strip())
        self.assertEqual("min=210: Hello, timer!", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("pulse_callback", func.strip())
        self.assertEqual("min=240: Hello, timer!", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("pulse_callback", func.strip())
        self.assertEqual("min=270: Hello, timer!", msg.strip())
        
        if len(list(ms_gen)) == 1:
            _, func, msg = next(ms_gen)
            self.assertEqual("pulse_callback", func.strip())
            self.assertEqual("min=300: Hello, timer!", msg.strip())
        
        self.assertTrue(len(list(ms_gen)) == 0)

    def test_stop_before_run(self):
        '''
        The 'stop' command test, before run
        '''
        Dmesg.clear()
        with TimeModule(path=MODULE_PATH) as time_module:
              status, result = time_module.execute(TimeModule.MODULE_CMD_STOP)
              self.assertEqual(0, status)
              self.assertEqual(0, result)

        ms_gen = Dmesg.get_messages(TimeModule.MODULE_NAME, last=3)
        _, func, msg = next(ms_gen)
        self.assertEqual("ex_timer_init", func.strip())
        self.assertEqual("init", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("stop_cmd_handler", func.strip())
        self.assertEqual("stop", msg.strip())
        _, func, msg = next(ms_gen)
        self.assertEqual("ex_timer_exit", func.strip())
        self.assertEqual("exit", msg.strip())
