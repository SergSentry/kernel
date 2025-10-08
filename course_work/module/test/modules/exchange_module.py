import os
import subprocess
from fcntl import ioctl
import struct


class ExchangeModule:
    MODULE_FILE_NAME = 'exchange.ko'
    MODULE_NAME = 'exchange'
    DEVICE_NAME = 'exchange'
    DEVICE_PATH = f"/dev/{DEVICE_NAME}"
    PROC_PATH = f"/proc/{DEVICE_NAME}"
    SYSFS_PARAMETER = "statistics"
    SYSFS_PATH = f"/sys/kernel/{DEVICE_NAME}/{SYSFS_PARAMETER}"
    DEFAULT_WORK_MODE  = 0
    DEVICE_IOCTL_MAGIC = ord('>')
    MODULE_PARAM_WORK_MODE = 'work_mode'
    EXCHANGE_IOCTL_GET_WORK_MODE = 0x80043E00
    
    def __init__(self, path: str = ""):
        self.__path = path

    def __enter__(self):
        self.__load_default(self.__path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__unload();

    def has_loaded(self) -> bool:
        result = subprocess.run(
            [f"lsmod | awk '/^{ExchangeModule.MODULE_NAME}[ ]+[0-9]+[ ]+[0-9]+/ {{print $0}}' | tr -s ' '"],
            stdout=subprocess.PIPE, shell=True)
        if result.stderr is not None:
            return False
        params = result.stdout.decode("utf-8").split(" ")
        return ExchangeModule.MODULE_NAME in params

    def get_ioctl_work_mode(self) -> int:
        if self.has_loaded():
            fd = os.open(ExchangeModule.DEVICE_PATH, os.O_RDWR)
        
            try:
                buffer = bytearray(4)
                result = ioctl(fd, ExchangeModule.EXCHANGE_IOCTL_GET_WORK_MODE, buffer, True)
                return struct.unpack("i", buffer)[0]
            finally:
                os.close(fd)

    def get_param_work_mode(self) -> int:
        if self.has_loaded():
            _read_param(_get_parameter_path(ExchangeModule.MODULE_PARAM_WORK_MODE))

    def has_device_exist(self) -> bool:
        return os.path.exists(ExchangeModule.DEVICE_PATH)

    def _get_parameter_path(self, name):
        return f'/sys/module/{ExchangeModule.MODULE_NAME}/parameters/{name}'

    def __unload(self):
        if self.has_loaded():
            result = subprocess.run([f'rmmod {ExchangeModule.MODULE_NAME}'], stdout=subprocess.PIPE, shell=True)
            if result.stderr is not None:
                return False
            response = result.stdout.decode("utf-8").split(" ")
            return ExchangeModule.MODULE_NAME in response

        return True

    def __load_default(self, path: str) -> bool:
        self.__unload()
        module_full_path = os.path.abspath(f"{path}/{ExchangeModule.MODULE_FILE_NAME}")
        result = subprocess.run([f'insmod {module_full_path}'], stdout=subprocess.PIPE, shell=True)
        return result.stderr is not None

    def _load(self, path: str, work_mode:int) -> bool:
        self.__unload()
        module_full_path = os.path.abspath(f"{path}/{ExchangeModule.MODULE_FILE_NAME}")
        module_param = f"{ExchangeModule.MODULE_PARAM_WORK_MODE}={work_mode}"
        result = subprocess.run([f'insmod {module_full_path} {module_param}'], stdout=subprocess.PIPE, shell=True)
        return result.stderr is not None

    def _read_param(self, param_name: str):
        if param_name not in {ExchangeModule.MODULE_PARAM_WORK_MODE}:
            raise NameError(param_name)

        sys_path = self._get_parameter_path(param_name)
        if not os.path.exists(sys_path):
            raise FileNotFoundError(sys_path)

        with open(sys_path, "br") as read_file:
            result = read_file.readline()

        value = result.decode("utf-8").strip()
        return int(value) if value.isdigit() else value
