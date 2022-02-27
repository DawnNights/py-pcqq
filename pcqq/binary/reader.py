import io
import re


class Reader:
    def __init__(self, initial_bytes: bytes = b'') -> None:
        self.raw = io.BytesIO(initial_bytes)

    def tell(self) -> int:
        return len(self.raw.getvalue()) - self.raw.tell()

    def read(self, size: int = -1) -> bytes:
        return self.raw.read(size)

    def read_hex(self, size: int = -1) -> str:
        hex = self.read(size).hex()
        return " ".join(re.findall('.{2}', hex.upper()))

    def read_int16(self) -> int:
        return int.from_bytes(self.read(2), 'big')

    def read_int32(self) -> int:
        return int.from_bytes(self.read(4), 'big')

    def read_byte(self) -> int:
        return self.read(1)[0]
