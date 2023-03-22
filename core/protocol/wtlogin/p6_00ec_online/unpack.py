from functools import partial

from logger import logger
from core.entities import Packet, PacketHandler, QQStruct


def check_00ec(packet: Packet):
    return packet.cmd == "00 EC"


async def handle_00ec(stru: QQStruct, packet: Packet):
    stru.is_running = True
    
    if stru.password != b'':
        logger.info(f"扫码登录成功, 欢迎尊敬的用户 {stru.nickname}({stru.uin}) 使用本协议库")
    else:
        logger.info(f"Token重登成功, 欢迎尊敬的用户 {stru.nickname}({stru.uin}) 使用本协议库")


def unpack_00ec(stru: QQStruct):
    return PacketHandler(
        temp=True,
        check=check_00ec,
        handle=partial(handle_00ec, stru)
    )
