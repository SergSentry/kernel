import os
import subprocess


class BinSearchModule:
    MODULE_FILE_NAME = 'ex_bin_search.ko'
    MODULE_NAME = 'ex_bin_search'
    
    MODULE_PARAM_CMD = 'cmd_param'
    MODULE_PARAM_CMD_STATUS = 'cmd_status'
    MODULE_PARAM_CMD_RESULT = 'cmd_result'

    MODULE_CMD_ADD = "add"
    MODULE_CMD_PRINT = "print"
    MODULE_CMD_SORT = "sort"
    MODULE_CMD_SEARCH = "search"

    def __init__(self, path: str = ""):
        self.__path = path

    def __enter__(self):
        self.__load_default(self.__path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__unload();

    def has_loaded(self) -> bool:
        result = subprocess.run(
            [f"lsmod | awk '/^{BinSearchModule.MODULE_NAME}[ ]+[0-9]+[ ]+[0-9]+/ {{print $0}}' | tr -s ' '"],
            stdout=subprocess.PIPE, shell=True)
        if result.stderr is not None:
            return False
        params = result.stdout.decode("utf-8").split(" ")
        return BinSearchModule.MODULE_NAME in params

    def execute(self, cmd: str):
        self._write_param(BinSearchModule.MODULE_PARAM_CMD, cmd)
        status = self._read_param(BinSearchModule.MODULE_PARAM_CMD_STATUS)
        result = self._read_param(BinSearchModule.MODULE_PARAM_CMD_RESULT)
        return (status, result)

    def _get_parameter_path(self, name):
        return f'/sys/module/{BinSearchModule.MODULE_NAME}/parameters/{name}'

    def __unload(self):
        if self.has_loaded():
            result = subprocess.run([f'rmmod {BinSearchModule.MODULE_NAME}'], stdout=subprocess.PIPE, shell=True)
            if result.stderr is not None:
                return False
            response = result.stdout.decode("utf-8").split(" ")
            return BinSearchModule.MODULE_NAME in response

        return True

    def __load_default(self, path: str) -> bool:
        self.__unload()
        module_full_path = os.path.abspath(f"{path}/{BinSearchModule.MODULE_FILE_NAME}")
        result = subprocess.run([f'insmod {module_full_path}'], stdout=subprocess.PIPE, shell=True)
        return result.stderr is not None

    def _write_param(self, param_name: str, value):
        if param_name not in {BinSearchModule.MODULE_PARAM_CMD, BinSearchModule.MODULE_PARAM_CMD_STATUS,
                              BinSearchModule.MODULE_PARAM_CMD_RESULT}:
            raise NameError(param_name)

        sys_path = self._get_parameter_path(param_name)
        if not os.path.exists(sys_path):
            raise FileNotFoundError(sys_path)

        with open(sys_path, "w") as write_file:
            try:
                write_file.write(str(value))
            except Exception as ex:
                print("e")

    def _read_param(self, param_name: str):
        if param_name not in {BinSearchModule.MODULE_PARAM_CMD, BinSearchModule.MODULE_PARAM_CMD_STATUS,
                              BinSearchModule.MODULE_PARAM_CMD_RESULT}:
            raise NameError(param_name)

        sys_path = self._get_parameter_path(param_name)
        if not os.path.exists(sys_path):
            raise FileNotFoundError(sys_path)

        with open(sys_path, "br") as read_file:
            result = read_file.readline()

        value = result.decode("utf-8").strip()
        return int(value)
