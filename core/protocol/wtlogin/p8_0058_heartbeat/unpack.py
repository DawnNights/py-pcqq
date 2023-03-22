from logger import logger
from core.entities import Packet, PacketHandler, QQStruct


def check_0058(packet: Packet):
    return packet.cmd == "00 58"


async def handle_0058(packet: Packet):
    sign = packet.body.read_byte()

    if sign == 0x00:
        # logger.info("心跳正常")
        pass
    elif sign == 0x01:
        logger.error("当前客户端掉线, 请刷新在线状态")
    elif sign == 0x17:
        logger.error("当前客户端掉线, 请重新登录")


def unpack_0058(stru: QQStruct):
    return PacketHandler(
        temp=False,
        check=check_0058,
        handle=handle_0058
    )
