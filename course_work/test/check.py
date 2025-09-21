#!/usr/bin/env python3

import os
import time
import stat
import unittest

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
