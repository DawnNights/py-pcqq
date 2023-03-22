import os
from functools import partial

from logger import logger
from core.entities import QQStruct, Packet, PacketHandler


def check_0819(packet: Packet):
    return packet.cmd == "08 19"


async def handle_0819(stru: QQStruct, packet: Packet):
    state = packet.body.read_byte()

    if state == 0x01:
        logger.info(f'账号 {packet.uin} 已扫码，请在手机上确认登录')
    elif state == 0x00:
        stru.uin = packet.uin
        stru.password = packet.body.del_left(2).read_token()
        stru.tgt_key = packet.body.del_left(2).read_token()

        path = os.path.join(stru.path, "QrCode.jpg")
        if os.path.exists(path):
            os.remove(path)
        
        logger.info(f'账号 {packet.uin} 已确认登录, 尝试登录中......')


def unpack_0819(stru: QQStruct):
    return PacketHandler(
        temp=True,
        check=check_0819,
        handle=partial(handle_0819, stru)
    )
