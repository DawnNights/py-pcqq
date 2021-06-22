from .util import Hex2Bin

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

    def SetStr(self,s: str):
        '''置字符串'''
        self._src = self._src + s.encode()

    def GetAll(self) -> bytes:
        '''取所有数据'''
        return self._src

