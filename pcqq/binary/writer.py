import io
import pcqq.utils as utils


class Writer:
    def __init__(self) -> None:
        self.raw = io.BytesIO()

    def clear(self) -> bytes:
        data = self.raw.getvalue()
        self.raw.close()
        return data

    def write(self, bin: bytes) -> None:
        self.raw.write(bin)

    def write_int(self, num: int) -> None:
        self.write(utils.int_to_bytes(num))

    def write_int16(self, num: int) -> None:
        self.write(num.to_bytes(2, 'big'))

    def write_int32(self, num: int) -> None:
        self.write(num.to_bytes(4, 'big'))

    def write_hex(self, hex: str) -> None:
        self.write(bytes.fromhex(hex))

    def write_byte(self, byte: int) -> None:
        self.write(byte.to_bytes(1, 'big'))

    def write_varint(self, num: int) -> None:
        while num > 127:
            self.write_byte(0x80 | num & 0x7F)
            num = num >> 7
        self.write_byte(num)