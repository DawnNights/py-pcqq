class Reader:
    def __init__(self, bin: bytes):
        self.__body = bin

    def ReadLen(self) -> int:
        return len(self.__body)

    def ReadAll(self) -> bytes:
        body = self.__body
        self.__body = bytes()
        return body

    def ReadByte(self) -> int:
        b = self.__body[0]
        self.__body = self.__body[1:]
        return b

    def ReadBytes(self, len: int) -> bytes:
        body = self.__body[0:len]
        self.__body = self.__body[len:]
        return body

    def ReadInt(self) -> int:
        body = self.__body[0:4]
        self.__body = self.__body[4:]
        return int.from_bytes(body, 'big')

    def ReadShort(self) -> int:
        body = self.__body[0:2]
        self.__body = self.__body[2:]
        return int.from_bytes(body, 'big')
