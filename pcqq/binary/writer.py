import io


def varint(num: int) -> bytes:
    val = bytearray()
    while num > 127:
        val.append(0x80 | num & 0x7F)
        num = num >> 7
    val.append(num)
    return bytes(val)


class Writer:
    def __init__(self) -> None:
        self.raw = io.BytesIO()

    def clear(self) -> bytes:
        data = self.raw.getvalue()
        self.raw.close()
        return data

    def write(self, bin: bytes) -> None:
        self.raw.write(bin)
    
    def write_int16(self, num: int) -> None:
        self.write(num.to_bytes(2, 'big'))

    def write_int32(self, num: int) -> None:
        self.write(num.to_bytes(4, 'big'))

    def write_hex(self, hex: str) -> None:
        self.write(bytes.fromhex(hex))

    def write_byte(self, byte: int) -> None:
        self.write(byte.to_bytes(1, 'big'))

    def write_varint(self, num: int) -> None:
        self.write(varint(num))

    def write_pbint(self, num: int, mark: int, isid: bool = True):
        mark = 8 * mark if isid else mark
        self.write_varint(mark)
        self.write_varint(num)

    def write_pbdata(self, data: bytes, mark: int, isid: bool = True):
        mark = 2 + 8 * mark if isid else mark
        self.write_varint(mark)
        self.write_byte(len(data))
        self.write(data)

    def write_pbhex(self, hex: str, mark: int, isid: bool = True):
        return self.write_pbdata(bytes.fromhex(hex), mark, isid)
