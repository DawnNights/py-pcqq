import pcqq.utils as utils
tea = utils.Tea()

def Pack_0058(QQ):
    '''心跳包'''
    # tea = utils.Tea()
    pack = utils.PackEncrypt()

    pack.Empty()
    pack.SetBin(QQ.Utf8QQ)
    body = tea.Encrypt(pack.GetAll(), QQ.SessionKey)

    pack.Empty()
    pack.SetHex("02 36 39")
    pack.SetHex("00 58")
    pack.SetBin(utils.GetRandomBin(2))
    pack.SetBin(QQ.BinQQ)
    pack.SetHex("02 00 00 00 01 01 01 00 00 67 B7")
    pack.SetBin(body)
    pack.SetHex("03")

    body = pack.GetAll()
    return body


def Pack_0062(QQ) -> bytes:
    '''离线包'''
    # tea = utils.Tea()
    pack = utils.PackEncrypt()

    pack.Empty()
    pack.SetHex("02 36 39")
    pack.SetHex("00 62")
    pack.SetBin(utils.GetRandomBin(2))
    pack.SetBin(QQ.BinQQ)
    pack.SetHex("02 00 00 00 01 01 01 00 00 67 B7 00 30 00 3A")
    pack.SetBin(tea.Encrypt(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', QQ.SessionKey))
    pack.SetHex("03")

    body = pack.GetAll()
    return body