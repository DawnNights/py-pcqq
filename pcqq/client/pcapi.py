import time
import urllib

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
    time_stamp = int(time.time()).to_bytes(4, 'big')[::-1]

    writer.write_int32(net.uin)
    writer.write_int32(user_id)
    writer.write_hex("00 00 00 08 00 01 00")
    writer.write_hex("04 00 00 00 00 36 39")
    writer.write_int32(net.uin)
    writer.write_int32(user_id)

    writer.write(utils.hashmd5(time_stamp))
    writer.write_hex("00 0B 37 96")
    writer.write(time_stamp)
    writer.write_hex("02 55 00 00 00 00 01 00 00 00")
    writer.write_hex("0C 4D 53 47 00 00 00 00 00")
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


def send_group_msg(group_id: int, msg_data: bytes, has_image: bool = False):
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

    net.send_packet(
        "00 02",
        const.BODY_VERSION,
        writer.clear()
    )


def upload_group_image(group_id: bytes, im_data: bytes):
    writer = binary.Writer()
    width, height = utils.img_size_get(im_data)

    writer.write_pbint(group_id, 1)
    writer.write_pbint(net.uin, 2)
    writer.write_pbint(0, 3)
    writer.write_pbdata(utils.hashmd5(im_data), 4)
    writer.write_pbint(len(im_data), 5)
    writer.write_pbhex(
        "37 00 4D 00 32 00 25 00 4C 00 31 00 56 00 32 00 7B 00 39 00 30 00 29 00 52 00", 6)
    writer.write_pbint(1, 7)
    writer.write_pbint(1, 9)
    writer.write_pbint(width, 10)
    writer.write_pbint(height, 11)
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

    net.send_packet(
        "03 88",
        const.FUNC_VERSION,
        writer.clear()
    )

    ret = net.tea.decrypt(net.cli.recv()[14:-1])
    if len(ret) < 128:
        return  # 无需重新上传

    start = ret.find(bytes([66, 128, 1])) + 3
    end = ret.find(bytes([128, 128, 8])) - 9
    ukey = ret[start:end].hex().upper()

    request = urllib.request.Request(
        method="POST",
        url=f"http://htdata2.qq.com/cgi-bin/httpconn?htcmd=0x6ff0071&ver=5515&term=pc&ukey={ukey}&filesize={len(im_data)}&range=0&uin={net.uin}&groupcode={group_id}",
        data=im_data,
        headers={
            "User-Agent": "QQClient",
            "Content-Length": len(im_data),
        }
    )
    urllib.request.urlopen(request).close()


def upload_friend_image(user_id: bytes, im_data: bytes) -> bytes:
    writer = binary.Writer()

    writer.write_pbint(net.uin, 1)
    writer.write_pbint(user_id, 2)
    writer.write_pbint(0, 3)
    writer.write_pbdata(utils.hashmd5(im_data), 4)
    writer.write_pbint(len(im_data), 5)
    writer.write_pbhex(
        "44 00 43 00 5F 00 4F 00 52 00 57 00 4C 00 38 00 4A 00 30 00 44 00 4B 00 34 00", 6)
    writer.write_pbint(1, 7)
    width, height = utils.img_size_get(im_data)
    writer.write_pbint(width, 14)
    writer.write_pbint(height, 15)
    data = writer.clear()

    writer.__init__()
    writer.write_pbint(1, 19)
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
    writer.write_hex("00 00 00 07 00 00")
    writer.write_int16(len(data)-7)
    writer.write(data)

    net.send_packet(
        "03 52",
        const.FUNC_VERSION,
        writer.clear()
    )

    reader = binary.Reader(net.tea.decrypt(net.cli.recv()[14:-1]))
    if reader.tell() < 256:
        reader.read(67)
        return  reader.read(55) # 无需重新上传

    reader.read(71)
    ukey = reader.read(336).hex().upper()
    reader.read(2)
    pic_id = reader.read(55)

    request = urllib.request.Request(
        method="POST",
        url=f"http://htdata2.qq.com/cgi-bin/httpconn?htcmd=0x6ff0070&ver=5509&ukey={ukey}&filesize={len(im_data)}&range=0&uin={net.uin}",
        data=im_data,
        headers={
            "User-Agent": "QQClient",
            "Content-Length": len(im_data),
        }
    )
    urllib.request.urlopen(request).close()
    return pic_id

