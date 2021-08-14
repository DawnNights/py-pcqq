import pcqq.utils as utils
tea = utils.Tea()

def Pack_0825(QQ, IsLogin:bool=False)->bytes:
    body = b''
    # tea = utils.Tea()
    pack = utils.PackEncrypt()
    QQ.RandHead16 = utils.GetRandomBin(16)

    if not IsLogin:
        pack.SetHex(
            "00 18 00 16 00 01 00 00 04 4C 00 00 00 01 00 00 15 51 00 00 00 00 00 00 00 00 00 04 00 0C 00 00 00 08 71 72 5F 6C 6F 67 69 6E 03 09 00 08 00 01 00 00 00 00 00 04 01 14 00 1D")
        pack.SetHex("01 02")
        pack.SetShort(len((QQ.PublicKey)))
        pack.SetBin(QQ.PublicKey)
        body = tea.Encrypt(pack.GetAll(), QQ.RandHead16)

        pack.Empty()
        pack.SetHex("02 36 39")
        pack.SetHex("08 25")
        pack.SetBin(utils.GetRandomBin(2))
        pack.SetHex("00 00 00 00 03 00 00 00 01 01 01 00 00 67 B7 00 00 00 00")
        pack.SetBin(QQ.RandHead16)
        pack.SetBin(body)
        pack.SetHex("03")
        body = pack.GetAll()
    else:
        pack.SetHex("00 18 00 16 00 01 00 00 04 4C 00 00 00 01 00 00 15 51")
        pack.SetBin(QQ.BinQQ)
        pack.SetHex("00 00 00 00 03 09 00 08 00 01")
        pack.SetBin(QQ.ConnectSeverIp)
        pack.SetHex("00 01 00 36 00 12 00 02 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 14 00 1D")
        pack.SetHex("01 02")
        pack.SetShort(len(QQ.PublicKey))
        pack.SetBin(QQ.PublicKey)
        body = tea.Encrypt(pack.GetAll(), QQ.RandHead16)

        pack.Empty()
        pack.SetHex("02 36 39")
        pack.SetHex("08 25")
        pack.SetBin(utils.GetRandomBin(2))
        pack.SetBin(QQ.BinQQ)
        pack.SetHex("03 00 00 00 01 01 01 00 00 67 B7 00 00 00 00")
        pack.SetBin(QQ.RandHead16)
        pack.SetBin(body)
        pack.SetHex("03")
        body = pack.GetAll()
    return body


def Pack_0818(QQ) -> bytes:
    '''获取二维码'''
    # tea = utils.Tea()
    pack = utils.PackEncrypt()
    QQ.RandHead16 = utils.GetRandomBin(16)

    pack.Empty()
    pack.SetHex("00 19 00 10 00 01 00 00 04 4C 00 00 00 01 00 00 15 51 00 00 01 14 00 1D")
    pack.SetHex("01 02")
    pack.SetShort(len(QQ.PublicKey))
    pack.SetBin(QQ.PublicKey)
    pack.SetHex("03 05 00 1E 00 00 00 00 00 00 00 05 00 00 00 04 00 00 00 00 00 00 00 48 00 00 00 02 00 00 00 02 00 00")
    body = tea.Encrypt(pack.GetAll(), QQ.RandHead16)

    pack.Empty()
    pack.SetHex("02 36 39")
    pack.SetHex("08 18")
    pack.SetBin(utils.GetRandomBin(2))
    pack.SetHex("00 00 00 00 03 00 00 00 01 01 01 00 00 67 B7 00 00 00 00")
    pack.SetBin(QQ.RandHead16)
    pack.SetBin(body)
    pack.SetHex("03")
    body = pack.GetAll()

    return body


def Pack_0819(QQ, codeId: str, IsLogin: bool = False) -> bytes:
    '''
    检查二维码状态
    :param codeId: 二维码ID
    :param IsLogin: 授权登录(True)/取二维码验证状态(False)
    '''

    # tea = utils.Tea()
    pack = utils.PackEncrypt()
    QQ.RandHead16 = utils.GetRandomBin(16)

    pack.SetHex("00 19 00 10 00 01 00 00 04 4C 00 00 00 01 00 00 15 51 00 00 03 01 00 22")

    pack.SetShort(len(codeId))
    pack.SetStr(codeId)
    if IsLogin:
        pack.SetHex("03 14 00 02 00 00")
    body = tea.Encrypt(pack.GetAll(), QQ.PcKeyFor0819)

    pack.Empty()
    pack.SetHex("02 36 39")
    pack.SetHex("08 19")
    pack.SetBin(utils.GetRandomBin(2))
    pack.SetHex("00 00 00 00 03 00 00 00 01 01 01 00 00 67 B7 00 00 00 00 00 30 00 3A")
    pack.SetShort(len(QQ.PcToken0038From0818))
    pack.SetBin(QQ.PcToken0038From0818)
    pack.SetBin(body)
    pack.SetHex("03")
    body = pack.GetAll()

    return body


def Pack_0836(QQ) -> bytes:
    tlv = utils.Tlv()
    # tea = utils.Tea()
    pack = utils.PackEncrypt()
    QQ.RandHead16 = utils.GetRandomBin(16)

    pack.Empty()
    pack.SetBin(tlv.Tlv112(QQ.PcToken0038From0825))
    pack.SetBin(tlv.Tlv30F("DawnNights-PCQQ"))
    pack.SetBin(tlv.Tlv005(QQ.BinQQ))
    pack.SetBin(tlv.Tlv303(QQ.PcToken0060From0819))
    pack.SetBin(tlv.Tlv015())
    pack.SetBin(tlv.Tlv01A(QQ.PcKeyTgt))

    pack.SetBin(tlv.Tlv018(QQ.BinQQ, QQ.Redirection))
    pack.SetBin(tlv.Tlv103())

    pack.SetBin(tlv.Tlv312())
    pack.SetBin(tlv.Tlv508())
    pack.SetBin(tlv.Tlv313())
    pack.SetBin(tlv.Tlv102(QQ.PcToken0038From0825))
    body = tea.Encrypt(pack.GetAll(), QQ.ShareKey)

    pack.Empty()

    pack.SetHex("02 36 39")
    pack.SetHex("08 36")
    pack.SetBin(utils.GetRandomBin(2))
    pack.SetBin(QQ.BinQQ)

    pack.SetHex("03 00 00 00 01 01 01 00 00 67 B7 00 00 00 00 00 01")
    pack.SetHex("01 02")
    pack.SetShort(len(QQ.PublicKey))
    pack.SetBin(QQ.PublicKey)
    pack.SetHex("00 00 00 10")
    pack.SetBin(QQ.RandHead16)
    pack.SetBin(body)
    pack.SetHex("03")
    body = pack.GetAll()
    return body


def Pack_0828(QQ) -> bytes:
    tlv = utils.Tlv()
    # tea = utils.Tea()
    pack = utils.PackEncrypt()

    pack.Empty()

    pack.SetBin(tlv.Tlv007(QQ.PcToken0088From0836))
    pack.SetBin(tlv.Tlv00C(QQ.ConnectSeverIp))
    pack.SetBin(tlv.Tlv015())
    pack.SetBin(tlv.Tlv036())
    pack.SetBin(tlv.Tlv018(QQ.BinQQ, QQ.Redirection))
    pack.SetBin(tlv.Tlv01F())
    pack.SetBin(tlv.Tlv105())
    pack.SetBin(tlv.Tlv10B())
    pack.SetBin(tlv.Tlv02D())
    body = tea.Encrypt(pack.GetAll(), QQ.PcKeyFor0828Send)

    pack.Empty()
    pack.SetHex("02 36 39")
    pack.SetHex("08 28")
    pack.SetBin(utils.GetRandomBin(2))
    pack.SetBin(QQ.BinQQ)
    pack.SetHex("02 00 00 00 01 01 01 00 00 67 B7 00 30 00 3A")
    pack.SetShort(len(QQ.PcToken0038From0836))
    pack.SetBin(QQ.PcToken0038From0836)
    pack.SetBin(body)
    pack.SetHex("03")
    body = pack.GetAll()
    return body


def Pack_001D(QQ) -> bytes:
    '''更新Clientkey'''
    # tea = utils.Tea()
    pack = utils.PackEncrypt()

    pack.Empty()

    pack.SetHex("11")
    body = tea.Encrypt(pack.GetAll(), QQ.SessionKey)

    pack.Empty()
    pack.SetHex("02 36 39")
    pack.SetHex("00 1D")
    pack.SetBin(utils.GetRandomBin(2))
    pack.SetBin(QQ.BinQQ)
    pack.SetHex("02 00 00 00 01 01 01 00 00 67 B7")
    pack.SetBin(body)
    pack.SetHex("03")
    body = pack.GetAll()
    return body


def Pack_00EC(QQ, state: int) -> bytes:
    '''
    置上线状态
    :param state:
    1 = 在线
    2 = Q我吧
    3 = 离开
    4 = 忙碌
    5 = 请勿打扰
    6 = 隐身
    '''
    # tea = utils.Tea()
    pack = utils.PackEncrypt()
    pack.SetHex("01 00")

    if state == 1:
        pack.SetHex("0A")
    elif state == 2:
        pack.SetHex("3C")
    elif state == 3:
        pack.SetHex("1E")
    elif state == 4:
        pack.SetHex("32")
    elif state == 5:
        pack.SetHex("46")
    elif state == 6:
        pack.SetHex("28")
    else:
        pack.SetHex("0A")

    pack.SetHex("00 01 00 01 00 04 00 00 00 00")
    body = tea.Encrypt(pack.GetAll(), QQ.SessionKey)
    pack.Empty()
    pack.SetHex("02 36 39")
    pack.SetHex("00 EC")
    pack.SetBin(utils.GetRandomBin(2))
    pack.SetBin(QQ.BinQQ)
    pack.SetHex("02 00 00 00 01 01 01 00 00 67 B7")
    pack.SetBin(body)
    pack.SetHex("03")
    body = pack.GetAll()
    return body