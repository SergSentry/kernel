#!/usr/bin/env python3

import os
import time
import stat
import unittest
from time import sleep

from test.modules.exchange_module import ExchangeModule
from test.tools.dmesg import Dmesg

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

    def test_dev_read_messages(self):
        '''
        Checking message for read device 
        '''
        with ExchangeModule(path=MODULE_PATH) as exchangeModule:
            self.assertTrue(exchangeModule.has_device_exist())

            with open(ExchangeModule.DEVICE_PATH, "rb") as device:
                _, func, msg = next(Dmesg.get_messages(ExchangeModule.MODULE_NAME, last=1))
                self.assertEqual("device_open", func.strip())
                self.assertEqual("Device opened", msg.strip())
                response = device.read()
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

            with open(ExchangeModule.DEVICE_PATH, "wb") as device:
                _, func, msg = next(Dmesg.get_messages(ExchangeModule.MODULE_NAME, last=1))
                self.assertEqual("device_open", func.strip())
                self.assertEqual("Device opened", msg.strip())
                device.write("hello".encode())
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

            work_mode = exchangeModule.get_work_mode()
            self.assertEqual(ExchangeModule.DEFAULT_WORK_MODE, work_mode)
