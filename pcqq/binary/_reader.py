class Reader:
    def __init__(self, body:bytes=b''):
        self._src = body

    def Update(self, body:bytes):
        self._src = body

    def ReadAll(self, clear:bool=False)->bytes:
        temp = self._src
        if clear:
            self._src = b''
        return temp
    
    def ReadBytes(self,length: int)->bytes:
        temp = self._src[0:length]
        self._src = self._src[length:]
        return temp

    def ReadShort(self)->int:
        num = int.from_bytes(self._src[0:2],byteorder='big',signed=False)
        self._src = self._src[2:]
        return num

    def ReadInt(self)->int:
        num = int.from_bytes(self._src[0:4],byteorder='big',signed=False)
        self._src = self._src[4:]
        return num

    def ReadByte(self)->int:
        b = self._src[0]
        self._src = self._src[1:]
        return b

    def ReadLength(self)->int:
        return len(self._src)