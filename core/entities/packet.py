from dataclasses import dataclass
from typing import Any, List, Callable, Coroutine

from core import croto
from core.const import Header, Tail
from core.utils import Stream, rand_bytes


@dataclass
class Packet:
    header: str = Header

    cmd: str = ""

    sequence: bytes = rand_bytes(2)

    uin: int = 0

    version: Stream = Stream()

    body: Stream = Stream()

    tail: str = Tail

    tea_key: bytes = b''

    def encode(self):
        stream = Stream()

        stream.write_hex(self.header)

        stream.write_hex(self.cmd)
        stream.write(self.sequence)
        stream.write_int32(self.uin)

        stream.write_stream(self.version)
        if self.tea_key == b'':
            stream.write_stream(self.body)
        else:
            data = self.body.read_all()
            stream.write(croto.tea_encrypt(data, self.tea_key))

        stream.write_hex(self.tail)

        return stream.read_all()

    def from_raw(raw_data: bytes, tea_key: bytes):
        stream = Stream(raw_data)
        stream.del_left(3).del_right(1)

        packet = Packet(
            cmd=stream.read_hex(2),
            sequence=stream.read(2),
            uin=stream.read_int32(),
            tea_key=tea_key
        )

        stream.del_left(3)
        if packet.tea_key == b'':
            packet.body = stream
        else:
            data = croto.tea_decrypt(stream._raw, tea_key)
            packet.body = Stream(data)

        return packet


@dataclass
class PacketHandler:
    temp: bool

    check: Callable[[Packet], bool]

    handle: Callable[[Packet], Coroutine[Any, Any, None]]


class PacketManger(List[PacketHandler]):
    def __repr__(self) -> str:
        return "PacketManger{\n%s\n}" % ("\n\n".join(["\t" + str(phr) for phr in self]))

    def append(self, phr: PacketHandler) -> None:
        if not isinstance(phr, PacketHandler):
            raise ValueError("PacketManger 添加的元素不是 PacketHandler 类型")

        if not phr in self:
            super().append(phr)

        return self

    def pop(self, phr: PacketHandler):
        if phr in self:
            super().pop(self.index(phr))

        return self

    async def exec_all(self, packet: Packet):
        for phr in self:
            if not phr.check(packet):
                continue

            if phr.temp:
                self.pop(phr)
            await phr.handle(packet)
