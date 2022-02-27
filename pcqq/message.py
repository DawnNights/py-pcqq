import re
import zlib

import pcqq.client as cli
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


def pqcode_escape(pqmsg: str, gid: int = 0) -> bytes:
    ret = bytes()
    pqcodes = re.findall(r'\[PQ:\w+?.*?]', pqmsg)

    for code in pqcodes:
        idx = pqmsg.find(code)
        ret += text(pqmsg[0:idx])
        pqmsg = pqmsg[idx+len(code):]

        typ = code[4:code.find(",")].lower()
        param = dict(re.findall(r',([\w\-.]+?)=([^,\]]+)', code))

        if typ == "at" and gid and "qq" in param:
            ret += at(int(param["qq"]), gid)
        elif typ == "face" and "id" in param:
            ret += face(int(param["id"]))
        elif typ == "xml" and "data" in param:
            ret += xml(param["data"])
        elif typ == "music" and len(param) == 5:
            ret += music(**param)

    if pqmsg:
        ret += text(pqmsg)
    return ret


def pqcode_compile(typ: str, **params) -> str:
    params = [f"{key}={params[key]}" for key in params]
    return "[PQ:%s,%s]" % (typ, ",".join(params))
