import time

import pcqq.network as net
import pcqq.utils as utils
import pcqq.const as const
import pcqq.binary as binary


def send_friend_msg(user_id: int, msg_data: bytes):
    """
    发送好友消息

    :param user_id: 好友QQ号

    :param msg_data: PCQQ消息协议数据

    """
    writer = binary.Writer()
    time_stamp = int(time.time()).to_bytes(4, 'big')

    writer.write_int32(net.uin)
    writer.write_int32(user_id)
    writer.write_hex("00 00 00 08 00 01 00")
    writer.write_hex("04 00 00 00 00 36 39")
    writer.write_int32(net.uin)
    writer.write_int32(user_id)

    writer.write(utils.hashmd5(time_stamp))
    writer.write_hex("00 0B 4A B6")
    writer.write(time_stamp)
    writer.write_hex("02 55 00 00 00 00 01 00 00 00")
    writer.write_hex("01 4D 53 47 00 00 00 00 00")
    writer.write(time_stamp)
    writer.write(time_stamp[::-1])

    writer.write_hex("00 00 00 00 09 00 86 00 00")
    writer.write_hex("06 E5 AE 8B E4 BD 93 00 00")
    writer.write(msg_data)

    net.send_packet(
        "00 CD",
        const.BODY_VERSION,
        writer.clear()
    )


def send_group_msg(group_id: int, msg_data: bytes):
    """
    发送群消息

    :param group_id: 目标群号

    :param msg_data: PCQQ消息协议数据

    """
    writer = binary.Writer()
    time_stamp = int(time.time()).to_bytes(4, 'big')

    writer.write_hex("00 01 01 00 00 00 00 00 00 00")
    writer.write_hex("4D 53 47 00 00 00 00 00")
    writer.write(time_stamp)
    writer.write(time_stamp[::-1])
    writer.write_hex("00 00 00 00 09 00 86 00 00")
    writer.write_hex("06 E5 AE 8B E4 BD 93 00 00")
    writer.write(msg_data)
    data = writer.clear()

    writer.__init__()
    writer.write_hex("2A")
    writer.write_int32(group_id)
    writer.write_int16(len(data))
    writer.write(data)

    net.send_packet(
        "00 02",
        const.BODY_VERSION,
        writer.clear()
    )