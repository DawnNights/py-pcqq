import zlib
import uuid
import json
import asyncio
from urllib import parse

import pcqq.client as cli
import pcqq.network as net
import pcqq.utils as utils
import pcqq.const as const
import pcqq.binary as binary


def text(text: str) -> bytes:
    writer = binary.Writer()

    data = text.encode()
    data_size = len(data)

    writer.write_byte(0x01)
    writer.write_int16(data_size + 3)
    writer.write_byte(0x01)
    writer.write_int16(data_size)
    writer.write(data)

    return writer.clear()


def face(face_id: int) -> bytes:
    writer = binary.Writer()

    writer.write_byte(0x02)
    writer.write_int16(1 + 3)
    writer.write_byte(0x01)
    writer.write_int16(1)
    writer.write_byte(face_id)

    return writer.clear()


async def at(user_id: int, group_id: int) -> bytes:
    name = "@" + await net.get_user_cache(
        user_id=user_id,
        group_id=group_id
    )

    writer = binary.Writer()
    writer.write_hex("00 01 00 00")
    writer.write_int16(len(name))
    writer.write_hex("00")
    writer.write_int32(user_id)
    writer.write_hex("00 00")
    data = writer.clear()
    name = name.encode()

    writer.__init__()
    writer.write_byte(0x01)
    writer.write_int16(len(name))
    writer.write(name)
    writer.write_byte(0x06)
    writer.write_int16(len(data))
    writer.write(data)
    data = writer.clear()

    writer.__init__()
    writer.write_byte(0x01)
    writer.write_int16(len(data))
    writer.write(data)
    return writer.clear() + text(" ")


def xml(xml_code: str) -> bytes:
    writer = binary.Writer()
    xml_code = xml_code.replace("&", "&amp;")
    xml_code = xml_code.replace("&#44;", ",")
    data = zlib.compress(xml_code.encode(), -1)

    writer.write_byte(0x14)
    writer.write_int16(len(data) + 11)
    writer.write_hex("01")
    writer.write_int16(len(data) + 1)
    writer.write_hex("01")
    writer.write(data)
    writer.write_hex("02 00 04 00 00 00 02")
    return writer.clear()


def music(
    title: str = "",
    content: str = "",
    url: str = "",
    audio: str = "",
    cover: str = ""
) -> bytes:
    xml_code = const.MUSIC_CODE.format(
        title=title,
        content=content,
        url=url,
        audio=audio,
        cover=cover
    )

    return xml(xml_code)

async def qqmusic(keyword: str):
    info = json.loads((await cli.webget(
        url="https://c.y.qq.com/soso/fcgi-bin/client_search_cp?w=" +
            parse.quote(keyword)
    )).content[9:-1])["data"]["song"]["list"][0]

    audio = (await cli.webget(
        url="https://u.y.qq.com/cgi-bin/musicu.fcg?data=" + parse.quote(
            json.dumps(
                {
                    "comm": {"uin": 0, "format": "json", "ct": 24, "cv": 0},
                    "req": {"module": "CDN.SrfCdnDispatchServer", "method": "GetCdnDispatch", "param": {"guid": "3982823384", "calltype": 0, "userip": ""}},
                    "req_0": {"module": "vkey.GetVkeyServer", "method": "CgiGetVkey", "param": {"guid": "3982823384", "songmid": [info["songmid"]], "songtype": [0], "uin": "0", "loginflag": 1, "platform": "20"}}
                }
            ))
    )).json()["req_0"]["data"]["midurlinfo"][0]["purl"]

    html = (await cli.webget(f"https://y.qq.com/n/ryqq/songDetail/{info['songmid']}")).content
    start = html.find(b'photo_new\\u002F')+15
    end = html.find(b"?max_age", start)

    return music(
        title=info["songname"],
        content=info["singer"][0]["name"],
        url=f"https://y.qq.com/n/yqq/song/{info['songmid']}.html",
        audio="http://dl.stream.qqmusic.qq.com/" + audio,
        cover="https://y.qq.com/music/photo_new/" + html[start:end].decode()
    )


class Image:
    def __init__(self, im_data: bytes) -> None:
        self.ukey = None
        self.picid = None
        self.finish = False

        self.data = im_data
        self.size = len(im_data)
        self.hash = utils.hashmd5(im_data)
        self.width, self.height = utils.img_size(im_data)
        self.uuid = "{%s}.jpg" % (str(uuid.UUID(bytes=self.hash)).upper())


async def image_group(group_id: int, image: Image) -> bytes:
    writer = binary.Writer()
    await net.upload_group_image(group_id, image)

    wait_times = 90
    while not image.finish:
        await asyncio.sleep(1)
        wait_times -= 1
        if not wait_times:
            raise Exception(f"获取图片 [PQ:image,file={image.hash.hex().upper()}] 超时")
    


    writer.write_hex("03 00 CB 02")
    writer.write_int16(len(image.uuid))
    writer.write(image.uuid.encode())
    writer.write_hex("04 00 04")

    writer.write_hex("84 74 B1 53 05 00 04 BC")
    writer.write_hex("EB 03 B7 06 00 04 00 00")
    writer.write_hex("00 50 07 00 01 43 08 00")
    writer.write_hex("00 09 00 01 01 0B 00 00")
    writer.write_hex("14 00 04 11 00 00 00 15")
    writer.write_hex("00 04 00 00 00 8B 16 00")
    writer.write_hex("04 00 00 00 81 18 00 04")
    writer.write_hex("00 00 0E D3 FF 00 5C 15")
    writer.write_hex("36 20 39 32 6B 41 31 43")
    writer.write_hex("38 34 37 34 62 31 35 33")
    writer.write_hex("62 63 65 62 30 33 62 37")
    writer.write_hex("20 20 20 20 20 20 35 30")
    writer.write_hex("20 20 20 20 20 20 20 20")
    writer.write_hex("20 20 20 20 20 20 20 20")

    writer.write(image.uuid.encode())
    writer.write_hex("41")
    return writer.clear()


async def image_friend(user_id: int, image: Image) -> bytes:
    writer = binary.Writer()
    await net.upload_friend_image(user_id, image)
    
    wait_times = 90
    while not image.finish:
        await asyncio.sleep(1)
        wait_times -= 1
        if not wait_times:
            raise Exception(f"获取图片 [PQ:image,file={image.hash.hex().upper()}] 超时")

    writer.write_hex("B6 E8 AF AD E4 BD 93 E7 AE 80 00 00 06 01 43 02")
    writer.write_hex("00 1B")
    writer.write((utils.randstr(23) + ".jpg").encode())
    writer.write_hex("03 00 04")
    writer.write_int32(image.size)
    writer.write_hex("04")
    writer.write_int16(len(image.picid))
    writer.write(image.picid)
    writer.write_hex("14 00 04 11 00 00 00 0B 00 00 18")
    writer.write_int16(len(image.picid))
    writer.write(image.picid)
    writer.write_hex("19 00 04 00 00")
    writer.write_int16(image.width)
    writer.write_hex("1A 00 04 00 00")
    writer.write_int16(image.height)
    writer.write_hex("1F 00 04 00")

    writer.write_hex("00 03 E8 1B 00 10")
    writer.write(image.hash)
    writer.write_hex("FF 00 75 16")

    writer.write(b' 117101061CB')
    size = str(image.size).encode()
    if len(size) > 5:
        writer.write(b' ' * 4)
    else:
        writer.write(b' ' * 5)

    writer.write(size)
    writer.write_byte(ord("e"))
    writer.write((image.hash.hex().upper()+".jpg").encode())
    writer.write_byte(ord("x"))
    writer.write(image.picid)
    writer.write_byte(ord("A"))
    return writer.clear()
