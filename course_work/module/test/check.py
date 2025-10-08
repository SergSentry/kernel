#!/usr/bin/env python3

import os
import time
import stat
import unittest
import subprocess
from time import sleep

from test.modules.exchange_module import ExchangeModule
from test.tools.dmesg import Dmesg
from test.tools.osfile import OsFile

MODULE_BUILD_DIR = "./build"
MODULE_PATH = f'{MODULE_BUILD_DIR}'


class TestExchangeModule(unittest.TestCase):

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
        with ExchangeModule(path=MODULE_PATH) as exchangeModule:
            self.assertTrue(exchangeModule.has_loaded())

    def test_init_message(self):
        '''
        Checking the dmesg log for the module initialization string
        '''
        with ExchangeModule(path=MODULE_PATH) as exchangeModule:
            _, func, msg = next(Dmesg.get_messages(ExchangeModule.MODULE_NAME, last=1))

            self.assertEqual("exchange_init", func.strip())
            self.assertEqual("init", msg.strip())
    
    def test_default_work_mode(self):
        '''
        Checking the default work mode
        '''
        with ExchangeModule(path=MODULE_PATH) as exchangeModule:
            self.assertTrue(exchangeModule.has_device_exist())
            target_data = exchangeModule._read_param(ExchangeModule.MODULE_PARAM_WORK_MODE)
            self.assertEqual(0, target_data)

    def test_permission(self):
        '''
        Check permission for parameters file /sys/module/<MODULE_NAME>/parameters/<NAME>
        '''
        with ExchangeModule(path=MODULE_PATH) as exchangeModule:
            self.assertTrue(exchangeModule.has_device_exist())

            work_mode_file = os.stat(exchangeModule._get_parameter_path(ExchangeModule.MODULE_PARAM_WORK_MODE))
        
        self.assertTrue(bool(work_mode_file.st_mode & (stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)))

    def test_exit_message(self):
        '''
        Checking the dmesg log for the module deinitialization string
        '''
        with ExchangeModule(path=MODULE_PATH) as exchangeModule:
            pass

        _, func, msg = next(Dmesg.get_messages(ExchangeModule.MODULE_NAME, last=1))

        self.assertEqual("exchange_exit", func.strip())
        self.assertEqual("exit", msg.strip())

    def test_dev_path(self):
        '''
        Checking the device pessent in /dev path
        '''
        with ExchangeModule(path=MODULE_PATH) as exchangeModule:
            self.assertTrue(exchangeModule.has_device_exist())

    def test_dev_open_close_messages(self):
        '''
        Checking message for open and close device 
        '''
        with ExchangeModule(path=MODULE_PATH) as exchangeModule:
            self.assertTrue(exchangeModule.has_device_exist())

            with open(ExchangeModule.DEVICE_PATH, "wb") as device:
                _, func, msg = next(Dmesg.get_messages(ExchangeModule.MODULE_NAME, last=1))
                self.assertEqual("device_open", func.strip())
                self.assertEqual("Device opened", msg.strip())
            
            _, func, msg = next(Dmesg.get_messages(ExchangeModule.MODULE_NAME, last=1))
            self.assertEqual("device_release", func.strip())
            self.assertEqual("Device closed", msg.strip())

    def test_insmod_argument(self):
        '''
        Module loading test with specified parameters
        '''
        exchangeModule = ExchangeModule(path=MODULE_PATH)
        
        exchangeModule._load(path=MODULE_PATH, work_mode=1)
        self.assertTrue(exchangeModule.has_loaded())
        
        target_data = exchangeModule._read_param(ExchangeModule.MODULE_PARAM_WORK_MODE)
        self.assertEqual(1, target_data)

    def test_dev_read_messages(self):
        '''
        Checking message for read device 
        '''
        with ExchangeModule(path=MODULE_PATH) as exchangeModule:
            self.assertTrue(exchangeModule.has_device_exist())

            Dmesg.clear()
            with OsFile(ExchangeModule.DEVICE_PATH) as device:
                _, func, msg = next(Dmesg.get_messages(ExchangeModule.MODULE_NAME, last=1))
                self.assertEqual("device_open", func.strip())
                self.assertEqual("Device opened", msg.strip())
                response = device.read(10)
                sleep(1)
                _, func, msg = next(Dmesg.get_messages_by_func(ExchangeModule.MODULE_NAME, "device_read", last=1))
                self.assertEqual("device_read", func.strip())
                self.assertEqual("Device read", msg.strip())

            _, func, msg = next(Dmesg.get_messages(ExchangeModule.MODULE_NAME, last=1))
            self.assertEqual("device_release", func.strip())
            self.assertEqual("Device closed", msg.strip())

    def test_dev_write_messages(self):
        '''
        Checking message for write device 
        '''
        with ExchangeModule(path=MODULE_PATH) as exchangeModule:
            self.assertTrue(exchangeModule.has_device_exist())
            
            Dmesg.clear()
            with OsFile(ExchangeModule.DEVICE_PATH) as device:
                _, func, msg = next(Dmesg.get_messages(ExchangeModule.MODULE_NAME, last=1))
                self.assertEqual("device_open", func.strip())
                self.assertEqual("Device opened", msg.strip())
                
                device.write("hello".encode())
                sleep(1)
                _, func, msg = next(Dmesg.get_messages_by_func(ExchangeModule.MODULE_NAME, "device_write", last=1))
                self.assertEqual("device_write", func.strip())
                self.assertEqual("Device write", msg.strip())  
                
            _, func, msg = next(Dmesg.get_messages(ExchangeModule.MODULE_NAME, last=1))
            self.assertEqual("device_release", func.strip())
            self.assertEqual("Device closed", msg.strip())
    
    def test_ioctl_get_work_mode(self):
        '''
        test ioctl function get_work_mode
        '''
        with ExchangeModule(path=MODULE_PATH) as exchangeModule:
            self.assertTrue(exchangeModule.has_device_exist())

            work_mode = exchangeModule.get_ioctl_work_mode()
            self.assertEqual(ExchangeModule.DEFAULT_WORK_MODE, work_mode)

    def run_command(self, command):
        return subprocess.run(command, shell=True, capture_output=True, text=True)

    def test_proc_session_pids(self):
        '''
        test write to proc device active session pid
        '''
        with ExchangeModule(path=MODULE_PATH) as exchangeModule:
            self.assertTrue(exchangeModule.has_device_exist())
            
            with OsFile(ExchangeModule.DEVICE_PATH) as device:
                result = self.run_command(f"cat {ExchangeModule.PROC_PATH}")
                self.assertEqual(str(os.getpid()), result.stdout.strip())

                self.run_command(f"echo '' > {ExchangeModule.PROC_PATH}")
                result = self.run_command(f"cat {ExchangeModule.PROC_PATH}")
                self.assertFalse(result.stdout.strip())
