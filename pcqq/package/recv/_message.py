import pcqq.utils as utils
tea = utils.Tea()

def UnPack_00CE(QQ, src: bytes, msg)->bool:
    '''
    解析好友消息包
    :param src: 解密包体
    :param msg: Message类
    '''

    msg.MsgType = "friend"
    unpack = utils.PackDecrypt()

    unpack.SetData(src)
    unpack.GetBin(16)
    dst = unpack.GetAll()
    dst = dst[0:len(dst) - 1]
    dst = tea.Decrypt(dst, QQ.SessionKey)
    if len(dst) == 0:
        return False
    msg.HeadBody = dst[0:16]
    unpack.SetData(dst)

    msg.FromQQ = unpack.GetInt()  # 触发者QQ
    msg.RecvQQ = unpack.GetInt()  # 接收者QQ
    unpack.GetBin(14)

    length = int(unpack.GetShort())
    unpack.GetBin(length)

    unpack.GetBin(2)  # QQ版本
    unpack.GetInt()  # 来源QQ
    unpack.GetInt()  # 自身QQ

    unpack.GetBin(16)  # 会话令牌
    unpack.GetBin(4)

    msg.MsgTime = unpack.GetInt()  # 接收时间

    try:
        unpack.GetBin(6)  # 头像、字体属性
        unpack.GetBin(5)  # 消息相关信息

        unpack.GetBin(24)
        length = int(unpack.GetShort())
        unpack.GetBin(length)  # 字体名称
        unpack.GetBin(2)

        msg.Parse(unpack.GetAll())
    except:
        return False
    return True


def UnPack_0017(QQ, src: bytes, msg):
    '''
    解析群消息包
    :param src: 解密包体
    :param msg: Message类
    '''
    msg.MsgType = "group"
    unpack = utils.PackDecrypt()

    unpack.SetData(src)
    unpack.GetBin(16)
    dst = unpack.GetAll()
    dst = dst[0:len(dst) - 1]
    dst = tea.Decrypt(dst, QQ.SessionKey)
    if dst == None or len(dst) == 0:
        return False

    msg.HeadBody = dst[0:16]
    unpack.SetData(dst)

    msg.FromGroup = unpack.GetInt()  # 接收群号
    msg.RecvQQ = unpack.GetInt()  # 自身QQ
    unpack.GetBin(10)
    typeOf = unpack.GetShort()  # 消息类型

    length = unpack.GetInt()
    unpack.GetBin(length)

    if len(unpack.GetAll()) < 5:
        return False
    unpack.GetInt()
    flag = unpack.GetByte()

    if typeOf == 82 and flag == 1:  # 群消息
        msg.FromQQ = unpack.GetInt()  # 接收QQ
        if msg.FromQQ == msg.RecvQQ:
            return False
        unpack.GetInt()  # 消息索引
        msg.MsgTime = unpack.GetInt()  # 接收时间
        unpack.GetBin(24)
        unpack.GetInt()  # 发送时间
        msg.MsgId = unpack.GetInt()  # 消息ID
        unpack.GetBin(8)

        length = int(unpack.GetShort())
        unpack.GetBin(length)  # 字体
        unpack.GetBin(2)

        # 以下是消息正文
        try:
            data = unpack.GetAll()
            pos = data.find(utils.Hex2Bin("4 0 C0 4 0 CA 4 0 F8 4 0"))
            unpack.SetData(data[pos + 35:])

            length = unpack.GetShort()
            msg.NickName = unpack.GetBin(length).decode()  # 发消息者昵称

            msg.Parse(data[0:pos])
        except Exception as err:
            return False
        return True