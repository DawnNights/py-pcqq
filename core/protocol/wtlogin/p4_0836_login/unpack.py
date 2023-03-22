from functools import partial

from core import utils, croto
from logger import logger
from core import const
from core.entities import QQStruct, Packet, PacketHandler


def check_0836(packet: Packet):
    return packet.cmd == "08 36"


async def handle_0836(stru: QQStruct, packet: Packet):
    if packet.body.read_hex(2) != "01 03":
        raise ValueError("08 36 Response Protocol Packet error")

    tk_key = packet.body.read_token()
    twice_key = stru.ecdh.twice(tk_key)
    raw_data = croto.tea_decrypt(packet.body.read_all(), twice_key)

    raw_data = croto.tea_decrypt(raw_data, stru.tgt_key)
    if raw_data == b'':
        raw_data = croto.tea_decrypt(raw_data, const.RandKey)
    stream = utils.Stream(raw_data)

    sign = stream.read_byte()
    if sign == 0x00:
        # logger.info(f"登录状态校验 -> OK")
        pass
    elif sign == 0x01:
        logger.fatal("登录状态校验 -> 需要更新TGTGT或需要二次解密")
        exit(1)
    elif sign == 0x33:
        logger.fatal("登录状态校验 -> 当前上网环境异常")
        exit(1)
    elif sign == 0x34:
        logger.fatal("登录状态校验 -> 需要验证密保或开启了设备锁")
        exit(1)
    else:
        logger.fatal("登录状态校验 -> 发生未处理错误")
        exit(1)

    while len(stream._raw) > 0:
        cmd = stream.read_hex(2)
        ns = utils.Stream(stream.read_token())

        if cmd == "01 09":
            stru.pckey_for_0828_send = ns.del_left(2).read(16)
            stru.token_0038_from_0836 = ns.read_token()

        elif cmd == "01 07":
            ns.read_int16()
            ns.read_token()

            stru.pckey_for_0828_recv = ns.read(16)
            stru.token_0088_from_0836 = ns.read_token()

        elif cmd == "01 08":
            ns.read(8)
            length = ns.read_byte()
            stru.nickname = ns.read(length).decode()


def unpack_0836(stru: QQStruct):
    return PacketHandler(
        temp=True,
        check=check_0836,
        handle=partial(handle_0836, stru)
    )
