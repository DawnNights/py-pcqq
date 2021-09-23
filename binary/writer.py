from .protobuf import varInt

class Writer:
    def __init__(self):
        self.__body = bytes()

    def ReadLen(self) -> int:
        return len(self.__body)

    def ReadAll(self) -> bytes:
        body = self.__body
        self.__body = bytes()
        return body

    def WriteByte(self, b: int):
        self.__body += b.to_bytes(1, 'big')

    def WriteBytes(self, bin: bytes):
        self.__body += bin

    def WriteHex(self, hex: str):
        hexa = hex.replace(' ', '')
        size = len(hexa) // 2
        self.__body += int(hexa, 16).to_bytes(size, 'big')

    def WriteInt(self, num: int):
        self.__body += num.to_bytes(4, 'big')

    def WriteShort(self, num: int):
        self.__body += num.to_bytes(2, 'big')

    def WriteArray(self, *args: int):
        self.__body += bytes(args)
    
    def WriteVarInt(self, num:int):
        self.__body += varInt(num)