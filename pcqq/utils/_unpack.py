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