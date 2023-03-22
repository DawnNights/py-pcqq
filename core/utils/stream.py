import re


class Stream:
    def __init__(self, raw=bytes(0)):
        self._raw = raw

    def __str__(self):
        if self._raw == None:
            self._raw = b''
        
        str = re.findall(".{2}", self._raw.hex().upper())
        return f"Stream({' '.join(str)})"

    def __repr__(self):
        if self._raw == None:
            self._raw = b''
        return f"Stream(Size: {len(self._raw)})"

    def write(self, bin: bytes):
        self._raw += bin
        return self

    def write_int16(self, num: int):
        return self.write(num.to_bytes(2, 'big'))

    def write_int32(self, num: int):
        return self.write(num.to_bytes(4, 'big'))

    def write_varint(self, num: int):
        val = bytearray()
        while num > 127:
            val.append(0x80 | num & 0x7F)
            num = num >> 7
        val.append(num)
        return self.write(bytes(val))

    def write_pbint(self, num: int, mark: int):
        mark = 8 * mark
        self.write_varint(mark)
        self.write_varint(num)

    def write_pbdata(self, data: bytes, mark: int):
        mark = 2 + 8 * mark
        self.write_varint(mark)
        self.write_byte(len(data))
        self.write(data)

    def write_pbhex(self, hex: str, mark: int):
        return self.write_pbdata(bytes.fromhex(hex), mark)

    def write_byte(self, byte: int):
        return self.write(byte.to_bytes(1, 'big'))

    def write_list(self, num_list: list):
        return self.write(bytes(num_list))

    def write_hex(self, hex: str):
        return self.write(bytes.fromhex(hex))

    def write_token(self, token: bytes):
        return self.write_int16(len(token)).write(token)

    def write_tlv(self, cmd: str, bin: bytes):
        return self.write_hex(cmd).write_token(bin)

    def write_stream(self, new_stream):
        return self.write(new_stream.read_all())

    def write_func(self, func):
        new_stream = Stream(b'')
        func(new_stream)
        return self.write_stream(new_stream)

    def del_left(self, length: int):
        self._raw = self._raw[length:]
        return self

    def del_right(self, length: int):
        self._raw = self._raw[:-length]
        return self

    def read(self, size: int):
        bin = self._raw[0:size]
        self._raw = self._raw[size:]
        return bin

    def read_all(self):
        return self.read(len(self._raw))

    def read_byte(self):
        return self.read(1)[0]

    def read_int16(self):
        return int.from_bytes(self.read(2), 'big')

    def read_int32(self):
        return int.from_bytes(self.read(4), 'big')

    def read_hex(self, size: int):
        string = self.read(size).hex().upper()
        return " ".join(re.findall(".{2}", string))

    def read_token(self, keep_size=False):
        size = self.read_int16()
        data = self.read(size)
        return size.to_bytes(2, 'big') + data if keep_size else data