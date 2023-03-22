from functools import partial

from logger import logger
from core.utils import QRCode
from core.entities import QQStruct, Packet, PacketHandler


def check_0818(packet: Packet):
    return packet.cmd == "08 18"


async def handle_0818(stru: QQStruct, packet: Packet):
    if packet.body.read_byte() != 0x00:
        logger.fatal("登录二维码获取失败，请尝试重新运行")
        raise RuntimeError("Can't get login qrcode")

    stru.pckey_for_0819 = packet.body.del_left(6).read(16)
    stru.token_0038_from_0818 = packet.body.del_left(4).read_token(True)
    stru.token_by_scancode = packet.body.del_left(4).read_token(True)

    packet.body.del_left(4)
    qrcode = QRCode(stru.path, packet.body.read_token())
    logger.info('登录二维码获取成功，已保存至' + qrcode.path)
    qrcode.auto_show()


def unpack_0818(stru: QQStruct):
    return PacketHandler(
        temp=True,
        check=check_0818,
        handle=partial(handle_0818, stru)
    )
