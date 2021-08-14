import pcqq.utils as utils
tea = utils.Tea()

def UnPack_0825(QQ, src: bytes)->bool:
    # tea = utils.Tea()
    unpack = utils.PackDecrypt()

    unpack.SetData(src)
    unpack.GetBin(16)
    dst = unpack.GetAll()
    dst = dst[0:-1]
    dst = tea.Decrypt(dst,QQ.RandHead16)

    unpack.SetData(dst)
    Type = int(unpack.GetByte())
    unpack.GetShort()
    length = unpack.GetShort()
    QQ.PcToken0038From0825 = unpack.GetBin(length)
    unpack.GetBin(6)
    unpack.GetBin(4)
    QQ.LocalPcIp = unpack.GetBin(4)
    unpack.GetShort()

    if Type == 254: #需要重定向服务器
        unpack.GetBin(18)
        QQ.ConnectSeverIp = unpack.GetBin(4)
        QQ.ConnectSeverIpText = "重定向地址: %d.%d.%d.%d\n"%(
            QQ.ConnectSeverIp[0],
            QQ.ConnectSeverIp[1],
            QQ.ConnectSeverIp[2],
            QQ.ConnectSeverIp[3]
        )

        return True
    else:
        unpack.GetBin(6)
        QQ.ConnectSeverIp = unpack.GetBin(4)
        return False

def UnPack_0818(QQ, src: bytes)->tuple:
    '''解析二维码地址'''
    # tea = utils.Tea()
    unpack = utils.PackDecrypt()

    unpack.SetData(src)
    unpack.GetBin(16)
    dst = unpack.GetAll()
    dst = dst[0:-1]
    dst = tea.Decrypt(dst,QQ.ShareKey)

    unpack.SetData(dst)
    unpack.GetBin(7)
    QQ.PcKeyFor0819 = unpack.GetBin(16)
    unpack.GetBin(4)
    length = int(unpack.GetShort())

    QQ.PcToken0038From0818 = unpack.GetBin(length)
    unpack.GetBin(4)
    length = unpack.GetShort()
    codeId = unpack.GetBin(length).decode()

    unpack.GetBin(4)
    length = unpack.GetShort()
    codeImg = unpack.GetBin(length)

    return (codeId,codeImg)

def UnPack_0819(QQ,src: bytes)->int:
    '''
    取二维码状态
    0 = 授权成功
    1 = 扫码成功
    2 = 未扫码
    3 = 空数据包
    :return: 状态码
    '''

    # tea = utils.Tea()
    unpack = utils.PackDecrypt()

    unpack.SetData(src)
    unpack.GetBin(16)
    dst = unpack.GetAll()
    dst = dst[0:-1]
    dst = tea.Decrypt(dst,QQ.PcKeyFor0819)

    unpack.SetData(dst)
    stateId = unpack.GetByte()

    if stateId == 1:
        QQ.BinQQ = src[9:13]
        QQ.LongQQ = int.from_bytes(QQ.BinQQ,byteorder='big',signed=False)
        QQ.Utf8QQ = str(QQ.LongQQ).encode()

    if stateId == 0 and len(dst) > 1:
        unpack.GetShort()
        length = unpack.GetShort()
        QQ.PcToken0060From0819 = unpack.GetBin(int(length))
        unpack.GetShort()
        length = unpack.GetShort()
        QQ.PcKeyTgt = unpack.GetBin(int(length))
    return stateId

def UnPack_0836(QQ, src: bytes)->bool:
    # tea = utils.Tea()
    unpack = utils.PackDecrypt()

    unpack.SetData(src)
    unpack.GetBin(16)
    dst = unpack.GetAll()
    dst = dst[0:-1]

    if len(dst) >= 100:
        dst = tea.Decrypt(tea.Decrypt(dst,QQ.ShareKey),QQ.PcKeyTgt)
    if len(dst) == 0:
        return False

    unpack.SetData(dst)
    Type = int(unpack.GetByte())

    if Type != 0:
        return False

    for i in range(5):
        tlvName = utils.Bin2HexTo(unpack.GetBin(2))
        tlvLength = int(unpack.GetShort())

        if tlvName == "1 9":
            unpack.GetShort()
            QQ.PcKeyFor0828Send = unpack.GetBin(16)

            length = int(unpack.GetShort())
            QQ.PcToken0038From0836 = unpack.GetBin(length)
            length = int(unpack.GetShort())
            unpack.GetBin(length)
            unpack.GetShort()
        elif tlvName == "1 7":
            unpack.GetBin(26)
            QQ.PcKeyFor0828Rev = unpack.GetBin(16)
            length = int(unpack.GetShort())
            QQ.PcToken0088From0836 = unpack.GetBin(length)
            length = tlvLength - 180
            unpack.GetBin(length)
        elif tlvName == "1 8":
            unpack.GetBin(8)
            length = int(unpack.GetByte())
            QQ.NickName = unpack.GetBin(length).decode()
        else:
            unpack.GetBin(tlvLength)

    if len(QQ.PcToken0088From0836) != 136 or len(QQ.PcKeyFor0828Send) != 16 or len(QQ.PcToken0038From0836) != 56:
        return False
    else:
        return True


def UnPack_0828(QQ, src: bytes):
    '''解析SessionKey'''
    # tea = utils.Tea()
    unpack = utils.PackDecrypt()

    unpack.SetData(src)
    unpack.GetBin(16)
    dst = unpack.GetAll()
    dst = dst[0:-1]
    dst = tea.Decrypt(dst,QQ.PcKeyFor0828Rev)

    unpack.SetData(dst)
    unpack.GetBin(63)
    QQ.SessionKey = unpack.GetBin(16)

def UnPack_001D(QQ, src: bytes):
    '''解析Clientkey'''
    # tea = utils.Tea()
    unpack = utils.PackDecrypt()

    unpack.SetData(src)
    unpack.GetBin(9)

    unpack.GetInt()
    unpack.GetBin(3)

    data = unpack.GetAll()
    data = data[0:-1]
    data = tea.Decrypt(data,QQ.SessionKey)

    unpack.SetData(data)
    unpack.GetBin(2)

    QQ.ClientKey = unpack.GetAll()

    if len(QQ.ClientKey) != 32:
        QQ.ClientKey = b''
        return