#!/usr/bin/env python

import os
import stat
import unittest

from test.modules.hello_module import HelloModule
from test.tools.dmesg import Dmesg

MODULE_BUILD_DIR = "./build"
MODULE_PATH = f'{MODULE_BUILD_DIR}'


class TestHelloModule(unittest.TestCase):

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
        hello_module = HelloModule()
        
        hello_module.load_default(path=MODULE_PATH)
        self.assertTrue(hello_module.has_loaded())
        hello_module.unload()

    def test_insmod_argument(self):
        '''
        Module loading test with specified parameters
        '''
        hello_module = HelloModule()
        
        hello_module.load(path=MODULE_PATH, idx=1, ch_val='h', my_str="ho-ho-ho")
        self.assertTrue(hello_module.has_loaded())
        
        target_data = hello_module._read_param(HelloModule.MODULE_PARAM_IDX)
        self.assertEqual(1, target_data)
        target_data = hello_module._read_param(HelloModule.MODULE_PARAM_CH_VAL)
        self.assertEqual('h', target_data)
        target_data = hello_module._read_param(HelloModule.MODULE_PARAM_MY_STR)
        self.assertEqual("ho-ho-ho", target_data)

        hello_module.unload()

    def test_init_message(self):
        '''
        Checking the dmesg log for the module initialization string
        '''
        hello_module = HelloModule()

        hello_module.load_default(path=MODULE_PATH)
        _, msg = next(Dmesg.get_messages(HelloModule.MODULE_NAME, last=1))
        hello_module.unload()

        self.assertEqual("init", msg.strip())

    def test_exit_message(self):
        '''
        Checking the dmesg log for the module deinitialization string
        '''
        hello_module = HelloModule()

        hello_module.load_default(path=MODULE_PATH)
        hello_module.unload()

        _, msg = next(Dmesg.get_messages(HelloModule.MODULE_NAME, last=1))

        self.assertEqual("exit", msg.strip())

    def test_permission(self):
        '''
        Check permission for parameters file /sys/module/<MODULE_NAME>/parameters/<NAME>
        '''
        hello_module = HelloModule()
        hello_module.load_default(path=MODULE_PATH)

        idx_file = os.stat(hello_module._get_parameter_path(HelloModule.MODULE_PARAM_IDX))
        ch_val_file = os.stat(hello_module._get_parameter_path(HelloModule.MODULE_PARAM_CH_VAL))
        my_str_file = os.stat(hello_module._get_parameter_path(HelloModule.MODULE_PARAM_MY_STR))
        
        hello_module.unload()
        
        self.assertTrue(bool(idx_file.st_mode & (stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)))
        self.assertTrue(bool(ch_val_file.st_mode & (stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)))
        self.assertTrue(bool(my_str_file.st_mode & 0o644))


    def test_init_value_param_my_str(self):
        '''
        The 'my_str' parameter default setting test
        '''
        hello_module = HelloModule()

        hello_module.load_default(path=MODULE_PATH)
        target_data = hello_module._read_param(HelloModule.MODULE_PARAM_MY_STR)
        hello_module.unload()
        self.assertTrue(len(target_data) == 0)
        self.assertTrue("" in target_data)

    def test_init_value_param_ch_val(self):
        '''
        The 'ch_val' parameter default setting test
        '''
        hello_module = HelloModule()

        hello_module.load_default(path=MODULE_PATH)
        target_data = hello_module._read_param(HelloModule.MODULE_PARAM_CH_VAL)
        hello_module.unload()
        self.assertTrue(len(target_data) == 0)
        self.assertTrue("" in target_data)

    def test_init_value_param_idx(self):
        '''
        The 'idx' parameter default setting test
        '''
        hello_module = HelloModule()

        hello_module.load_default(path=MODULE_PATH)
        target_data = hello_module._read_param(HelloModule.MODULE_PARAM_IDX)
        hello_module.unload()

        self.assertEqual(0, target_data)

    def test_set_value_param_ch_val(self):
        '''
        The 'ch_val' parameter setting test
        '''
        source_data = 'h'
        hello_module = HelloModule()

        hello_module.load_default(path=MODULE_PATH)
        hello_module._write_param(HelloModule.MODULE_PARAM_CH_VAL, source_data)
        target_data = hello_module._read_param(HelloModule.MODULE_PARAM_CH_VAL)
        hello_module.unload()

        self.assertTrue(len(target_data) == 1)
        self.assertEqual(source_data, target_data)

    def test_set_value_param_idx(self):
        '''
        The 'idx' parameter setting test
        '''
        source_data = 1
        hello_module = HelloModule()

        hello_module.load_default(path=MODULE_PATH)
        hello_module._write_param(HelloModule.MODULE_PARAM_IDX, source_data)
        target_data = hello_module._read_param(HelloModule.MODULE_PARAM_IDX)
        hello_module.unload()

        self.assertEqual(source_data, target_data)

    def test_out_range_value_param_idx(self):
        '''
        Checking if the 'idx' parameter is out of range
        '''
        source_data = HelloModule.MODULE_PARAM_MY_STR_MAX_LEN +1
        hello_module = HelloModule()

        hello_module.load_default(path=MODULE_PATH)
        with self.assertRaises(OSError):
            hello_module._write_param(HelloModule.MODULE_PARAM_IDX, source_data)

        hello_module.unload()

    def test_get_value_param_my_str(self):
        '''
        Test for the value of 'my_str' when writing the character 'h' to position 0
        '''
        source_index = 0
        source_data = 'h'
        hello_module = HelloModule()

        hello_module.load_default(path=MODULE_PATH)
        hello_module._write_param(HelloModule.MODULE_PARAM_IDX, source_index)
        hello_module._write_param(HelloModule.MODULE_PARAM_CH_VAL, source_data)

        target_data = hello_module._read_param(HelloModule.MODULE_PARAM_MY_STR)
        hello_module.unload()

        self.assertTrue(len(target_data) == 1)
        self.assertEqual(source_data, target_data[0].strip())

    def test_write_read(self):
        '''
        The test of writing the string 'Hello, world!'
        '''
        source_data = 'Hello, world!'
        hello_module = HelloModule()

        hello_module.load_default(path=MODULE_PATH)
        hello_module.write(source_data)
        target_data = hello_module.read()
        hello_module.unload()

        self.assertEqual(source_data, target_data)
