from re import S
from ._util import Hex2Bin

class PackDecrypt():
    '''解包'''
    def __init__(self):
        self._src = b''
        self._position = 0

    def SetData(self,src: bytes):
        '''置字节集'''
        self._src = src

    def GetBin(self,length: int)->bytes:
        '''取指定长度字节集'''
        temp = self._src[0:length]
        self._src = self._src[length:]
        self._position += length
        return temp

    def GetShort(self)->int:
        '''取短整数'''
        n = int.from_bytes(self._src[0:2],byteorder='big',signed=False)
        self._src = self._src[2:]
        self._position += 2
        return n

    def GetInt(self)->int:
        '''取整数'''
        n = int.from_bytes(self._src[0:4],byteorder='big',signed=False)
        self._src = self._src[4:]
        self._position += 4
        return n

    def GetByte(self)->int:
        '''取字节'''
        b = self._src[0]
        self._src = self._src[1:]
        self._position += 1
        return b

    def GetAll(self)->bytes:
        '''取所有字节集'''
        return self._src

    def GetPosition(self)->int:
        '''取position'''
        return self._position

class PackEncrypt():
    '''打包'''
    def __init__(self):
        self._src = b''

    def Empty(self):
        '''清空'''
        self._src = b''

    def SetBin(self, data: bytes):
        '''置字节集'''
        self._src = self._src + data

    def SetHex(self, s: str):
        '''置文本十六进制格式'''
        self._src = self._src + Hex2Bin(s)

    def SetShort(self, num: int):
        '''置短整数'''
        self._src = self._src + num.to_bytes(2,"big")

    def SetInt(self, num: int):
        '''置整数'''
        self._src = self._src + num.to_bytes(4,"big")

    def SetVarInt(self, num: int):
        '''置变长整数'''
        n = 0
        buf = [None for x in range(5)]
        while num > 127:
            buf[n] = 0x80 | num&0x7F
            num = num >> 7
            n += 1
        buf[n] = num
        self._src = self._src + b''.join([x.to_bytes(1,"big") for x in buf])

    def SetStr(self,s: str):
        '''置字符串'''
        self._src = self._src + s.encode()

    def GetAll(self) -> bytes:
        '''取所有数据'''
        return self._src