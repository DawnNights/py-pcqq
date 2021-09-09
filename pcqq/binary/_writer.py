class Writer:
    def __init__(self):
        self._src = b''

    def ReadAll(self)->bytes:
        temp = self._src
        self._src = b''
        return temp

    def WriteBytes(self, bin:bytes):
        self._src +=  bin

    def WriteHex(self, hexStr:str):
        for v in hexStr.split(" "):
            self._src += int(v, 16).to_bytes(1, "big")
        
    def WriteShort(self, num:int):
        self._src += num.to_bytes(2,"big")

    def WriteInt(self, num:int):
        self._src += num.to_bytes(4,"big")

    def WriteByte(self, byte:int):
        self._src += byte.to_bytes(1,"big")

    def WriteArray(self, *args:int):
        for arg in args:
            self._src += arg.to_bytes(1, "big")

    def WriteVarInt(self, num:int):
        n = 0
        buf = [None for x in range(5)]
        while num > 127:
            buf[n] = 0x80 | num&0x7F
            num = num >> 7
            n += 1
        buf[n] = num
        self._src = self._src + b''.join([x.to_bytes(1,"big") for x in buf if x != None])