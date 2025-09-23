import os
import subprocess


class ExchangeModule:
    MODULE_FILE_NAME = 'exchange.ko'
    MODULE_NAME = 'exchange'
    DEVICE_NAME = 'exchange'
    DEVICE_PATH = f"/dev/{DEVICE_NAME}0"
    
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

    def has_device_exist(self) -> bool:
        return os.path.exists(ExchangeModule.DEVICE_PATH)

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
