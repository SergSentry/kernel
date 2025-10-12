import os

class OsFile:

    def __init__(self, path:str, flags:int=os.O_RDWR):
        self.__path = path
        self.__flags = flags

    def __enter__(self):
        self.__fd = os.open(self.__path, self.__flags)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__close()

    def __close(self):
        os.close(self.__fd)

    def get_descriptor(self):
        return self.__fd

    def write(self, buf:bytes):
        os.write(self.__fd, buf)

    def read(self, length) ->bytes:
        return os.read(self.__fd, length)

    def write_ioctl_int(self, code:int, value:int):
        buffer = struct.pack("i", value)
        ioctl(self.__fd, code, buffer, True)

    def read_ioctl_int(self, code) -> int:
        buffer = bytearray(4)
        result = ioctl(self.__fd, code, buffer, True)
        return struct.unpack("i", buffer)[0]
