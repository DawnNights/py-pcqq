from functools import partial

from logger import logger
from core.entities import QQStruct, Packet, PacketHandler


def check_0825(packet: Packet):
    return packet.cmd == "08 25"


async def handle_0825(stru: QQStruct, packet: Packet):
    stream = packet.body

    sign = stream.read_byte()
    stream.read(2)
    stru.token_0038_from_0825 = stream.read(stream.read_int16())
    stream.read(6)
    stru.login_time = stream.read(4)
    stru.local_ip = stream.read(4)
    stream.read(2)

    logger.info(f"已选用 {stru.addr[0]} 作为登录服务器")
    if sign == 0xfe:
        stream.read(18)
        stru.server_ip = stream.read(4)
        stru.redirection_times += 1
        stru.redirection_history += stru.server_ip
    elif sign == 0x00:
        stream.read(6)
        stru.server_ip = stream.read(4)
        stru.redirection_history = b''


def unpack_0825(stru: QQStruct):
    return PacketHandler(
        temp=True,
        check=check_0825,
        handle=partial(handle_0825, stru)
    )
