from ._util import Hex2Bin

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

    def GetAll(self,command="") -> bytes:
        '''取所有数据'''
        if command != "":
            pass
        return self._src