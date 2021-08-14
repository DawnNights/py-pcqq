import time
import pcqq.utils as utils

def Pack_0002(QQ, groupId: int, content: str) -> bytes:
    '''
    构建发送群文本消息包
    :param groupId: 发送群号
    :param content: 消息内容
    '''

    tea = utils.Tea()
    pack = utils.PackEncrypt()
    QQ.Time = int(time.time()).to_bytes(4, "big")
    Msg = content.encode()

    pack.Empty()
    pack.SetHex("00 01 01 00 00 00 00 00 00 00 4D 53 47 00 00 00 00 00")
    pack.SetBin(QQ.Time)
    pack.SetBin(QQ.Time[::-1])
    pack.SetHex("00 00 00 00 09 00 86 00 00 06 E5 AE 8B E4 BD 93 00 00 01")
    pack.SetShort(len(Msg) + 3)
    pack.SetHex("01")
    pack.SetShort(len(Msg))
    pack.SetBin(Msg)
    body = pack.GetAll()

    pack.Empty()
    pack.SetHex("2A")
    pack.SetInt(groupId)
    pack.SetShort(len(body))
    pack.SetBin(body)
    body = tea.Encrypt(pack.GetAll(), QQ.SessionKey)

    pack.Empty()
    pack.SetHex("02 36 39")
    pack.SetHex("00 02")
    pack.SetBin(utils.GetRandomBin(2))
    pack.SetBin(QQ.BinQQ)
    pack.SetHex("02 00 00 00 01 01 01 00 00 67 B7")
    pack.SetBin(body)
    pack.SetHex("03")
    body = pack.GetAll()
    return body


def Pack_00CD(QQ, userId: int, content: str) -> bytes:
    '''
    构建发送好友文本消息包
    :param userId: 发送帐号
    :param content: 消息内容
    '''

    tea = utils.Tea()
    pack = utils.PackEncrypt()
    QQ.Time = int(time.time()).to_bytes(4, "big")
    Msg = content.encode()

    pack.Empty()
    pack.SetBin(QQ.BinQQ)
    pack.SetInt(userId)
    pack.SetHex("00 00 00 08 00 01 00 04 00 00 00 00 36 39")
    pack.SetBin(QQ.BinQQ)
    pack.SetInt(userId)

    pack.SetBin(utils.HashMD5(QQ.Time))

    pack.SetHex("00 0B 4A B6")
    pack.SetBin(QQ.Time)
    pack.SetHex("02 55 00 00 00 00 01 00 00 00 01 4D 53 47 00 00 00 00 00")
    pack.SetBin(QQ.Time)
    pack.SetBin(QQ.Time[::-1])
    pack.SetHex("00 00 00 00 09 00 86 00 00 06 E5 AE 8B E4 BD 93 00 00 01")
    pack.SetShort(len(Msg) + 3)
    pack.SetHex("01")
    pack.SetShort(len(Msg))
    pack.SetBin(Msg)
    body = tea.Encrypt(pack.GetAll(), QQ.SessionKey)

    pack.Empty()
    pack.SetHex("02 36 39")
    pack.SetHex("00 CD")
    pack.SetBin(utils.GetRandomBin(2))
    pack.SetBin(QQ.BinQQ)
    pack.SetHex("02 00 00 00 01 01 01 00 00 67 B7")
    pack.SetBin(body)
    pack.SetHex("03")
    body = pack.GetAll()
    return body


def Pack_0017(QQ, sendBody: bytes, sequence: bytes) -> bytes:
    '''
    确认群消息已读
    :param sendBody: 消息包解密前16位
    '''
    tea = utils.Tea()
    pack = utils.PackEncrypt()

    pack.Empty()
    pack.SetBin(sendBody)
    body = tea.Encrypt(pack.GetAll(), QQ.SessionKey)

    pack.Empty()
    pack.SetHex("02 36 39")
    pack.SetHex("00 17")
    pack.SetBin(sequence)
    pack.SetBin(QQ.BinQQ)
    pack.SetHex("02 00 00 00 01 01 01 00 00 67 B7")
    pack.SetBin(body)

    pack.SetHex("03")
    body = pack.GetAll()
    return body


def Pack_00CE(QQ, sendBody: bytes, sequence: bytes) -> bytes:
    '''
    确认好友消息已读
    :param sendBody: 消息包解密前16位
    '''
    tea = utils.Tea()
    pack = utils.PackEncrypt()

    pack.Empty()
    pack.SetBin(sendBody)
    body = tea.Encrypt(sendBody, QQ.SessionKey)

    pack.Empty()
    pack.SetHex("02 36 39")
    pack.SetHex("00 CE")
    pack.SetBin(sequence)
    pack.SetBin(QQ.BinQQ)
    pack.SetHex("02 00 00 00 01 01 01 00 00 67 B7")
    pack.SetBin(body)

    pack.SetHex("03")
    body = pack.GetAll()
    return body


def Pack_0002_receipt(QQ, msg) -> bytes:
    '''群消息回执包'''
    tea = utils.Tea()
    pack = utils.PackEncrypt()

    pack.Empty()
    pack.SetHex("29")
    pack.SetBin(utils.GroupToGid(msg.FromGroup).to_bytes(4, "big"))
    pack.SetHex("02")
    pack.SetBin(msg.MsgId.to_bytes(4, "big"))
    body = tea.Encrypt(pack.GetAll(), QQ.SessionKey)

    pack.Empty()
    pack.SetHex("02 36 39")
    pack.SetHex("00 02")
    pack.SetBin(utils.GetRandomBin(2))
    pack.SetBin(QQ.BinQQ)
    pack.SetHex("02 00 00 00 01 01 01 00 00 67 B7")
    pack.SetBin(body)
    pack.SetHex("03")

    body = pack.GetAll()
    return body


def Pack_0319(QQ, msg) -> bytes:
    '''好友消息回执包'''
    tea = utils.Tea()
    pack = utils.PackEncrypt()

    pack.Empty()
    pack.SetHex("08 01")
    pack.SetHex("12 03 98 01 00")

    pack.SetHex("0A 0E 08")
    pack.SetVarInt(msg.FromQQ)
    pack.SetHex("10")
    pack.SetVarInt(msg.MsgTime)
    pack.SetHex("20 00")
    body = pack.GetAll()

    pack.Empty()
    pack.SetHex("00 00 00 07")
    pack.SetInt(len(body) - 7)
    pack.SetBin(body)

    body = tea.Encrypt(pack.GetAll(), QQ.SessionKey)

    pack.Empty()
    pack.SetHex("02 36 39")
    pack.SetHex("03 19")
    pack.SetBin(utils.GetRandomBin(2))
    pack.SetBin(QQ.BinQQ)
    pack.SetHex("04 00 00 00 01 01 01 00 00 6A 0F 00 00 00 00 00 00 00 00")

    pack.SetBin(body)
    pack.SetHex("03")
    body = pack.GetAll()
    return body