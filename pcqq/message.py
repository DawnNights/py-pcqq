import zlib
import uuid
import json
import base64
import urllib.request

import pcqq.client as cli
import pcqq.utils as utils
import pcqq.const as const
import pcqq.binary as binary


def text(text: str):
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


def at(user_id: int, group_id: int) -> bytes:
    if group_id:
        nickname = "@" + cli.get_group_cord(user_id, group_id)
    else:
        nickname = "@" + cli.get_user_name(user_id)

    writer = binary.Writer()
    writer.write_hex("00 01 00 00")
    writer.write_int16(len(nickname))
    writer.write_hex("00")
    writer.write_int32(user_id)
    writer.write_hex("00 00")
    data = writer.clear()
    nickname = nickname.encode()

    writer.__init__()
    writer.write_byte(0x01)
    writer.write_int16(len(nickname))
    writer.write(nickname)
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


def qqmusic(keyword: str):
    keyword = urllib.parse.quote(keyword)
    with urllib.request.urlopen("https://c.y.qq.com/soso/fcgi-bin/client_search_cp?w=" + keyword) as ret:
        info = json.loads(ret.read()[9:-1])["data"]["song"]["list"][0]

    request = urllib.request.Request(
        method="GET",
        url="https://u.y.qq.com/cgi-bin/musicu.fcg?data=" + urllib.parse.quote(
            json.dumps(
                {
                    "comm": {"uin": 0, "format": "json", "ct": 24, "cv": 0},
                    "req": {"module": "CDN.SrfCdnDispatchServer", "method": "GetCdnDispatch", "param": {"guid": "3982823384", "calltype": 0, "userip": ""}},
                    "req_0": {"module": "vkey.GetVkeyServer", "method": "CgiGetVkey", "param": {"guid": "3982823384", "songmid": [info["songmid"]], "songtype": [0], "uin": "0", "loginflag": 1, "platform": "20"}}
                }
            ))
    )
    with urllib.request.urlopen(request) as ret:
        audio = json.loads(ret.read())[
            "req_0"]["data"]["midurlinfo"][0]["purl"]

    with urllib.request.urlopen(f"https://y.qq.com/n/yqq/song/{info['songmid']}.html") as ret:
        html = ret.read().decode()
        start = html.find(r"photo_new\u002F")+15
        end = html.find(r"?max_age", start)

    return music(
        title=info["songname"],
        content=info["singer"][0]["name"],
        url=f"https://y.qq.com/n/yqq/song/{info['songmid']}.html",
        audio="http://dl.stream.qqmusic.qq.com/" + audio,
        cover="https://y.qq.com/music/photo_new/" + html[start:end]
    )


def image_group(group_id: int, im_data: bytes) -> bytes:
    cli.upload_group_image(group_id, im_data)
    writer = binary.Writer()
    im_uuid = uuid.UUID(bytes=utils.hashmd5(im_data))
    im_uuid = "{%s}.jpg" % (str(im_uuid).upper())

    writer.write_hex("03 00 CB 02")
    writer.write_int16(len(im_uuid))
    writer.write(im_uuid.encode())
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

    writer.write(im_uuid.encode())
    writer.write_hex("41")
    return writer.clear()


def image_friend(user_id: int, im_data: bytes) -> bytes:
    pic_id = cli.upload_friend_image(user_id, im_data)
    writer = binary.Writer()
    width, height = utils.img_size_get(im_data)

    writer.write_hex("06 00 F3 02")
    writer.write_hex("00 1B")
    writer.write((utils.randstr(23) + ".jqg").encode())
    writer.write_hex("03 00 04")
    writer.write_int32(len(im_data))
    writer.write_hex("04")
    writer.write_int32(len(pic_id))
    writer.write(pic_id)
    writer.write_hex("14 00 04 11 00 00 00 0B 00 00 18")
    writer.write_int32(len(pic_id))
    writer.write(pic_id)
    writer.write_hex("19 00 04 00 00")
    writer.write_int16(width)
    writer.write_hex("1A 00 04 00 00")
    writer.write_int16(height)
    writer.write_hex("FF 00 63 16")

    size = str(len(im_data)).encode()
    if len(size) > 5:
        writer.write_hex("20 20 39 39 31 30 20 38 38 31 43 42 20 20 20 20")
    else:
        writer.write_hex("20 20 39 39 31 30 20 38 38 31 43 42 20 20 20 20 20")
    writer.write(size)

    writer.write_hex("65")
    writer.write((utils.hashmd5(im_data).hex().upper()+".jpg").encode())
    writer.write_hex("66")
    writer.write(pic_id)
    writer.write_hex("41")
    return writer.clear()


def pqcode(typ: str, params: dict, session) -> bytes:
    if typ == "at" and session.group_id and "qq" in params:
        return at(int(params["qq"]), session.group_id)
    elif typ == "face" and "id" in params:
        return face(int(params["id"]))
    elif typ == "xml" and "data" in params:
        return xml(params["data"])
    elif typ == "music":
        if "keyword" in params:
            return qqmusic(params["keyword"])
        elif len(params) == 5:
            return music(**params)
    elif typ == "image":
        if "url" in params:
            rsp = urllib.request.urlopen(urllib.request.Request(
                method="GET",
                url=params["url"],
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
                    "Host": "i.pixiv.re"
                }
            ))
            im_data = rsp.read()
            rsp.close()

        elif "file" in params:
            file = open(params["file"], "rb")
            im_data = file.read()
            file.close()
        elif "base64" in params:
            im_data = base64.b64decode(params["base64"])

        if session.group_id:
            return image_group(session.group_id, im_data)
        elif session.user_id:
            pass  # 暂时不支持
            # return image_friend(session.user_id, im_data)

    return bytes()
