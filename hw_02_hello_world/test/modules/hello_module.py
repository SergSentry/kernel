import os
import subprocess


class HelloModule:
    MODULE_FILE_NAME = 'hello.ko'
    MODULE_NAME = 'hello'
    MODULE_PARAM_IDX = 'idx'
    MODULE_PARAM_CH_VAL = 'ch_val'
    MODULE_PARAM_MY_STR = 'my_str'
    MODULE_PARAM_MY_STR_MAX_LEN = 16

    def _get_parameter_path(self, name):
        return f'/sys/module/{HelloModule.MODULE_NAME}/parameters/{name}'

    def has_loaded(self) -> bool:
        result = subprocess.run(
            [f"lsmod | awk '/^{HelloModule.MODULE_NAME}[ ]+[0-9]+[ ]+[0-9]+/ {{print $0}}' | tr -s ' '"],
            stdout=subprocess.PIPE, shell=True)
        if result.stderr is not None:
            return False
        params = result.stdout.decode("utf-8").split(" ")
        return HelloModule.MODULE_NAME in params

    def load_default(self, path: str) -> bool:
        module_full_path = os.path.abspath(f"{path}/{HelloModule.MODULE_FILE_NAME}")
        result = subprocess.run([f'insmod {module_full_path}'], stdout=subprocess.PIPE, shell=True)
        return result.stderr is not None

    def load(self, path: str, idx=0, ch_val='', my_str="") -> bool:
        module_full_path = os.path.abspath(f"{path}/{HelloModule.MODULE_FILE_NAME}")
        module_param = f"{HelloModule.MODULE_PARAM_IDX}={idx} {HelloModule.MODULE_PARAM_CH_VAL}={ch_val} {HelloModule.MODULE_PARAM_MY_STR}='{my_str}'"
        result = subprocess.run([f'insmod {module_full_path} {module_param}'], stdout=subprocess.PIPE, shell=True)
        return result.stderr is not None

    def unload(self):
        result = subprocess.run([f'rmmod {HelloModule.MODULE_NAME}'], stdout=subprocess.PIPE, shell=True)
        if result.stderr is not None:
            return False
        response = result.stdout.decode("utf-8").split(" ")
        return HelloModule.MODULE_NAME in response

    def _write_param(self, param_name: str, value):
        if param_name not in {HelloModule.MODULE_PARAM_IDX, HelloModule.MODULE_PARAM_CH_VAL,
                              HelloModule.MODULE_PARAM_MY_STR}:
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
        if param_name not in {HelloModule.MODULE_PARAM_IDX, HelloModule.MODULE_PARAM_CH_VAL,
                              HelloModule.MODULE_PARAM_MY_STR}:
            raise NameError(param_name)

        sys_path = self._get_parameter_path(param_name)
        if not os.path.exists(sys_path):
            raise FileNotFoundError(sys_path)

        with open(sys_path, "br") as read_file:
            result = read_file.readline()

        value = result.decode("utf-8").strip()
        return int(value) if value.isdigit() else value

    def write(self, value: str):
        if len(value) > HelloModule.MODULE_PARAM_MY_STR_MAX_LEN:
            raise ValueError(f"Data value must be less or equal {HelloModule.MODULE_PARAM_MY_STR_MAX_LEN} symbols")

        for i in range(len(value)):
            self._write_param(HelloModule.MODULE_PARAM_IDX, i)
            self._write_param(HelloModule.MODULE_PARAM_CH_VAL, value[i])

    def read(self) -> str:
        return self._read_param(HelloModule.MODULE_PARAM_MY_STR)
