#!/usr/bin/env python3

import os
import time
import stat
import unittest
import threading
import subprocess
import string
import random
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


    def check_open(self):
        _, func, msg = next(Dmesg.get_messages_by_func(ExchangeModule.MODULE_NAME, "device_open", last=1))
        self.assertEqual("device_open", func.strip())
        self.assertEqual("Device opened", msg.strip())
        _, func, msg = next(Dmesg.get_messages_by_func(ExchangeModule.MODULE_NAME, "add_new_client", last=1))
        self.assertEqual("add_new_client", func.strip())
        self.assertEqual(f"Added a client, pid:{str(os.getpid())}", msg.strip())

    def check_close(self):
        _, func, msg = next(Dmesg.get_messages_by_func(ExchangeModule.MODULE_NAME, "remove_client", last=1))
        self.assertEqual("remove_client", func.strip())
        self.assertEqual(f"Client removed, pid:{str(os.getpid())}", msg.strip())
        _, func, msg = next(Dmesg.get_messages_by_func(ExchangeModule.MODULE_NAME, "device_release", last=1))
        self.assertEqual("device_release", func.strip())
        self.assertEqual("Device closed", msg.strip())

    def test_dev_open_close_messages(self):
        '''
        Checking message for open and close device 
        '''
        with ExchangeModule(path=MODULE_PATH) as exchangeModule:
            self.assertTrue(exchangeModule.has_device_exist())

            with open(ExchangeModule.DEVICE_PATH, "wb") as device:
                self.check_open()
            
            self.check_close()

    def test_insmod_argument(self):
        '''
        Module loading test with specified parameters
        '''
        exchangeModule = ExchangeModule(path=MODULE_PATH)
        
        exchangeModule.load(ExchangeModule.WORK_MODE_BROADCAST)
        self.assertTrue(exchangeModule.has_loaded())
        
        target_data = exchangeModule._read_param(ExchangeModule.MODULE_PARAM_WORK_MODE)
        self.assertEqual(ExchangeModule.WORK_MODE_BROADCAST, target_data)

    def test_dev_unicast_mode_read_messages_single_thread(self):
        '''
        Checking unicast write and read message 
        '''
        message = "hello"
        with ExchangeModule(path=MODULE_PATH) as exchangeModule:
            self.assertTrue(exchangeModule.has_device_exist())

            with OsFile(ExchangeModule.DEVICE_PATH) as device:
                self.check_open()

                device.write(message.encode())
                sleep(2)
                _, func, msg = next(Dmesg.get_messages_by_func(ExchangeModule.MODULE_NAME, "device_write", last=1))
                self.assertEqual("device_write", func.strip())
                self.assertEqual("Device write", msg.strip())  
                
                response = device.read(10).decode()
                self.assertEqual(message, response)

                _, func, msg = next(Dmesg.get_messages_by_func(ExchangeModule.MODULE_NAME, "device_read", last=1))
                self.assertEqual("device_read", func.strip())
                self.assertEqual("Device read", msg.strip())

            self.check_close()

    def test_dev_broadcast_mode_read_messages_single_thread(self):
        '''
        Checking broadcast write and read message 
        '''
        message = "hello"
        exchangeModule = ExchangeModule(path=MODULE_PATH)
        exchangeModule.load(ExchangeModule.WORK_MODE_BROADCAST)
        self.assertTrue(exchangeModule.has_device_exist())

        with OsFile(ExchangeModule.DEVICE_PATH) as device:
            self.check_open()

            device.write(message.encode())
            sleep(2)
            _, func, msg = next(Dmesg.get_messages_by_func(ExchangeModule.MODULE_NAME, "device_write", last=1))
            self.assertEqual("device_write", func.strip())
            self.assertEqual("Device write", msg.strip())

            response = device.read(10).decode()
            self.assertEqual(message, response)
                
            _, func, msg = next(Dmesg.get_messages_by_func(ExchangeModule.MODULE_NAME, "device_read", last=1))
            self.assertEqual("device_read", func.strip())
            self.assertEqual("Device read", msg.strip())

        self.check_close()
   
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

    def test_read_sysfs_statistic_param(self):
        '''
        test read statistic from sysfs
        '''
        with ExchangeModule(path=MODULE_PATH) as exchangeModule:
            self.assertTrue(exchangeModule.has_device_exist())
            
            with OsFile(ExchangeModule.DEVICE_PATH) as device:
                with open(ExchangeModule.SYSFS_PATH, "rt") as sysfs_param:
                    values = sysfs_param.readlines()
                    self.assertEqual(2, len(values))
                    self.assertEqual('0\n', values[0])
                    self.assertEqual('0\n', values[1])

    def generate_random_message(self, length=10):
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for _ in range(length))

    def client_operation(self, client_id):
        message = self.generate_random_message()
        with OsFile(ExchangeModule.DEVICE_PATH) as device:
            buf = message.encode();
            device.write(buf)
            sleep(1)
            response = device.read(len(buf)).decode()
            self.assertEqual(message, response.strip())

    def test_multithread_read_write(self):
        '''
        test multithread write and read
        '''
        with ExchangeModule(path=MODULE_PATH) as exchangeModule:
            self.assertTrue(exchangeModule.has_device_exist())
            
            threads = []
            for i in range(10):
                t = threading.Thread(target=self.client_operation, args=(i,))
                threads.append(t)
                t.start()

            for thread in threads:
                thread.join()
