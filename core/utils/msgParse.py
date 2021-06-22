from .faceParse import FaceToStr
from .packDecrypt import PackDecrypt
def MsgParse(body:bytes, msg:list):
    '''
    QQ消息体解析
    :param body: 消息体字节集
    :param msg:  转消息列表(代替指针)
    :param fromQQ: 发送者QQ
    '''
    unpack = PackDecrypt()
    unpack.SetData(body)

    msgType = unpack.GetByte() # 消息类型
    dataLen = int(unpack.GetShort()) # 数据长度
    pos = unpack.GetPosition()

    while pos+dataLen < len(unpack.GetAll()):
        unpack.GetByte()
        if msgType == 1:    # 纯文本 && 艾特
            length = unpack.GetShort()
            s = unpack.GetBin(length).decode()
            if s[0] == "@" and pos+dataLen-unpack.GetPosition() == 16:
                unpack.GetBin(10)
                msg.append(s)
                # msg.append("[PQ:At=%d]"%(fromQQ))
                unpack.GetInt()
            else:
                msg.append(s)
        elif msgType == 2:  # Emoji(系统表情)
            unpack.GetShort()
            msg.append(FaceToStr(unpack.GetByte()))
        elif msgType == 3:  # 图片
            length = unpack.GetShort()
            picStr = unpack.GetBin(length).decode()
            msg.append("[PQ:image,file="+picStr+"]")

        unpack.GetBin(pos + dataLen - unpack.GetPosition())
        msgType = unpack.GetByte()
        dataLen = unpack.GetShort()
        pos = unpack.GetPosition()