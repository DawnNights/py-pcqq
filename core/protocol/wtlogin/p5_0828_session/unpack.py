from functools import partial

from logger import logger
from core.utils import Stream
from core.entities import QQStruct, Packet, PacketHandler


def check_0828(packet: Packet):
    return packet.cmd == "08 28"


async def handle_0828(stru: QQStruct, packet: Packet):
    sign = packet.body.read_byte()
    if sign == 0x00:
        #logger.info("会话密匙申请 -> OK")
        pass
    else:
        logger.fatal("会话密匙申请 -> 发生未处理错误")
        exit(1)

    while len(packet.body._raw) > 0:
        cmd = packet.body.read_hex(2)
        ns = Stream(packet.body.read_token())

        if cmd == "01 0C":
            stru.session_key = ns.del_left(2).read(16)


def unpack_0828(stru: QQStruct):
    return PacketHandler(
        temp=True,
        check=check_0828,
        handle=partial(handle_0828, stru)
    )
