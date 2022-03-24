import time

import pcqq.client as cli
import pcqq.utils as utils
import pcqq.const as const
import pcqq.logger as logger
import pcqq.binary as binary
#cli = cli.QQClient()


async def send_friend_msg(user_id: int, msg_data: bytes, has_image: bool = False):
    """
    发送好友消息

    :param user_id: 好友QQ号

    :param msg_data: PCQQ消息协议数据

    """
    writer = binary.Writer()
    time_stamp = int(time.time()).to_bytes(4, 'big')[::-1]

    writer.write_int32(cli.uin)
    writer.write_int32(user_id)
    writer.write_hex("00 00 00 08 00 01 00")
    writer.write_hex("04 00 00 00 00 36 39")
    writer.write_int32(cli.uin)
    writer.write_int32(user_id)

    writer.write(utils.hashmd5(time_stamp))
    writer.write_hex("00 0B 37 96")
    writer.write(time_stamp)
    writer.write_hex("02 55 00 00 00 00 01 00 00 00")
    writer.write_hex("0C 4D 53 47 00 00 00 00 00")
    writer.write(time_stamp)
    writer.write(time_stamp[::-1])

    writer.write_hex("00 00 00 00 09 00 86 00 00")
    if has_image:
        writer.write_hex("12 E6 B1 89 E4 BB AA E8 9D")
    else:
        writer.write_hex("06 E5 AE 8B E4 BD 93 00 00")
    writer.write(msg_data)

    await cli.write_packet(
        "00 CD",
        const.BODY_VERSION,
        writer.clear()
    )


async def send_group_msg(group_id: int, msg_data: bytes, has_image: bool = False):
    """
    发送群消息

    :param group_id: 目标群号

    :param msg_data: PCQQ消息协议数据

    :param has_image: 消息数据中是否含有图片数据

    """
    writer = binary.Writer()
    time_stamp = int(time.time()).to_bytes(4, 'big')

    if has_image:
        writer.write_hex("00 02 01 00 00 00 00 00 00 00")
    else:
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
    writer.write_int32(utils.gid_from_group(group_id))
    writer.write_int16(len(data))
    writer.write(data)

    await cli.write_packet(
        "00 02",
        const.BODY_VERSION,
        writer.clear()
    )


async def friend_receipt(user_id: int, timestamp: int):
    writer = binary.Writer()
    writer.write_hex("08 01")
    writer.write_hex("12 03 98 01 00")
    writer.write_hex("0A 0E 08")
    writer.write_varint(user_id)
    writer.write_hex("10")
    writer.write_varint(timestamp)
    writer.write_hex("20 00")
    data = writer.clear()

    writer.__init__()
    writer.write_hex("00 00 00 07")
    writer.write_int32(len(data)-7)
    writer.write(data)

    await cli.write_packet(
        "03 19",
        const.FUNC_VERSION,
        writer.clear()
    )


async def group_receipt(group_id: int, msg_id: int):
    writer = binary.Writer()

    writer.write_byte(41)
    writer.write_int32(utils.gid_from_group(group_id))
    writer.write_byte(2)
    writer.write_int32(msg_id)

    await cli.write_packet(
        "00 02",
        const.BODY_VERSION,
        writer.clear()
    )


async def upload_group_image(group_id: int, image):
    writer = binary.Writer()

    writer.write_pbint(group_id, 1)
    writer.write_pbint(cli.uin, 2)
    writer.write_pbint(0, 3)
    writer.write_pbdata(image.hash, 4)
    writer.write_pbint(image.size, 5)
    writer.write_pbhex(
        "37 00 4D 00 32 00 25 00 4C 00 31 00 56 00 32 00 7B 00 39 00 30 00 29 00 52 00", 6
    )
    writer.write_pbint(1, 7)
    writer.write_pbint(1, 9)
    writer.write_pbint(image.width, 10)
    writer.write_pbint(image.height, 11)
    writer.write_pbint(4, 12)
    writer.write_pbdata("26656".encode(), 13)
    data = writer.clear()

    writer.__init__()
    writer.write_pbdata(data, 3)
    data = writer.clear()

    writer.__init__()
    writer.write_pbint(1, 19)
    temp = writer.clear()

    writer.__init__()
    writer.write_pbdata(temp, 2)
    temp = writer.clear()

    writer.__init__()
    writer.write_pbint(1, 1)
    writer.write(temp)
    writer.write_pbint(1, 2)
    writer.write(data)
    data = writer.clear()

    writer.__init__()
    writer.write_hex("00 00 00 07 00 00")
    writer.write_int16(len(data))
    writer.write(data)
    writer.write_hex("70 00 78 03 80 01 00")

    sequence = utils.randbytes(2)
    await cli.write_packet(
        "03 88",
        const.FUNC_VERSION,
        writer.clear(),
        sequence=sequence,
    )

    async def callback(body):
        if len(body) < 128:
            logger.info(f"图片获取成功 -> https://gchat.qpic.cn/gchatpic_new/0/0-0-{image.hash.hex().upper()}/0?term=3")
            image.finish = True
            return  # 无需重新上传

        start = body.find(bytes([66, 128, 1])) + 3
        end = body.find(bytes([128, 128, 8])) - 9
        image.ukey = body[start:end].hex().upper()

        await cli.webpost(
            url="http://htdata2.qq.com/cgi-bin/httpconn?" + "&".join([
                "htcmd=0x6ff0071",
                "ver=5515",
                "term=pc",
                f"ukey={image.ukey}",
                f"filesize={image.size}",
                "range=0",
                f"uin={cli.uin}",
                f"groupcode={group_id}"
            ]),
            data=image.data,
            headers={"User-Agent": "QQClient"}
        )
        logger.info(f"图片上传完成 -> https://gchat.qpic.cn/gchatpic_new/0/0-0-{image.hash.hex().upper()}/0?term=3")
        image.finish = True
    cli.waiter[sequence.hex()] = callback


async def upload_friend_image(user_id: int, image) -> bytes:
    writer = binary.Writer()

    writer.write_pbint(cli.uin, 1)
    writer.write_pbint(user_id, 2)
    writer.write_pbint(0, 3)
    writer.write_pbdata(image.hash, 4)
    writer.write_pbint(image.size, 5)
    writer.write_pbhex(
        "45 00 4F 00 59 00 7B 00 56 00 29 00 45 00 56 00 4A 00 4B 00 48 00 48 00 53 00", 6
    )
    writer.write_pbint(1, 7)
    writer.write_pbint(0, 9)
    writer.write_pbint(image.width, 14)
    writer.write_pbint(image.height, 15)
    data = writer.clear()

    writer.__init__()
    writer.write_pbint(1, 19)
    writer.write_hex("98 03 F6 A8 BF A6 04 A0 03 01")
    temp = writer.clear()

    writer.__init__()
    writer.write_pbdata(data, 2)
    data = writer.clear()

    writer.__init__()
    writer.write_pbdata(temp, 2)
    temp = writer.clear()

    writer.__init__()
    writer.write_pbint(1, 1)
    writer.write(temp)
    writer.write_pbint(1, 1)
    writer.write(data)
    data = writer.clear()

    writer.__init__()
    writer.write_hex("00 00 00 11 00 00")
    writer.write_int16(len(data)-17)
    writer.write(data)

    sequence = utils.randbytes(2)
    await cli.write_packet(
        "03 52",
        const.FUNC_VERSION,
        writer.clear(),
        sequence=sequence,
    )

    async def callback(body):
        reader = binary.Reader(body)

        if reader.tell() < 256:
            reader.read(66)
            image.picid = reader.read(55)  # 无需重新上传
            logger.info(f"图片获取成功 -> https://c2cpicdw.qpic.cn/offpic_new/{cli.uin}/{image.picid.decode()}/0")
            image.finish = True
            return

        reader.read(70)
        image.ukey = reader.read(336).hex().upper()
        reader.read(2)
        image.picid = reader.read(55)

        await cli.webpost(
            url="http://htdata2.qq.com/cgi-bin/httpconn?" + "&".join([
                "htcmd=0x6ff0070",
                "ver=5509",
                f"ukey={image.ukey}",
                f"filesize={image.size}",
                "range=0",
                f"uin={cli.uin}"
            ]),
            data=image.data,
            headers={
                "User-Agent": "QQClient",
            }
        )
        logger.info(f"图片上传完成 -> https://c2cpicdw.qpic.cn/offpic_new/{cli.uin}/{image.picid.decode()}/0")
        image.finish = True

    cli.waiter[sequence.hex()] = callback
