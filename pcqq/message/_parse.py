import pcqq.utils as utils
import pcqq.binary as binary
import pcqq.client as client
from ._face import FaceMap

class MsgBody:
    def __init__(self):
        self.Type = ""  # 消息类型
        self.SubType = ""   # 消息子类型

        self.MsgText = ""   # 消息转义文本
        self.MsgTime = 0    # 消息接收时间
        
        self.SendQQ = 0 # 消息执行账号
        self.RecvQQ = 0 # 消息接收账号

        self.FromQQ = 0 # 消息来源账号
        self.FromGroup = 0  # 消息来源群号

        self.MsgID = 0  # 消息ID
        self.MsgSequence = 0  # 消息序号

def MsgParse(body:bytes, msgBody:MsgBody, QQ)->bool:
    reader = binary.Reader(body)

    if body[18:20] == b'\x00\x52':  # 群聊消息
        msgBody.Type = "group"
        reader.ReadBytes(4)
        msgBody.RecvQQ = reader.ReadInt()  # 自身账号

        reader.ReadBytes(12)
        reader.ReadBytes(reader.ReadInt())
        msgBody.FromGroup = reader.ReadInt()   # 消息来源群号

        reader.ReadByte()
        msgBody.FromQQ = reader.ReadInt()  # 消息来源账号
        msgBody.MsgID = reader.ReadInt()
        msgBody.MsgTime = reader.ReadInt()

        reader.ReadBytes(8)
        reader.ReadBytes(16)

        client.GroupReceipt(QQ=QQ, msgBody=msgBody, Type=0)
        if msgBody.FromQQ == msgBody.RecvQQ:
            return False
    elif body[18:20] == b'\x00\xA6':    # 私聊消息
        msgBody.Type = "friend"
        msgBody.FromQQ = reader.ReadInt()
        msgBody.RecvQQ = reader.ReadInt()

        reader.ReadBytes(12)
        reader.ReadBytes(reader.ReadInt()+26)
        reader.ReadBytes(2)

        msgBody.MsgID = reader.ReadShort()
        msgBody.MsgTime = reader.ReadInt()

        reader.ReadBytes(6)
        reader.ReadBytes(4)
        reader.ReadBytes(9)

        client.PrivateReceipt(QQ=QQ, msgBody=msgBody)
    elif body[18:20] == b'\x00\x21':    # 进群事件
        msgBody.Type = "group"
        msgBody.SubType = "increase"
        
        msgBody.FromGroup = utils.GidToGroup(reader.ReadInt())
        msgBody.RecvQQ = reader.ReadInt()  # 自身账号
        
        reader.ReadBytes(12)
        reader.ReadBytes(reader.ReadInt()+5)

        msgBody.FromQQ = reader.ReadInt()
        sign = reader.ReadByte()
        msgBody.SendQQ = reader.ReadInt()

        if sign == 0x02:    # 管理员审核
            msgBody.MsgText = f"管理员({msgBody.SendQQ})同意申请者({msgBody.FromQQ})加入群({msgBody.FromGroup})"
        elif sign == 0x03:  # 群员邀请无需审核
            msgBody.MsgText = f"群员({msgBody.SendQQ})成功邀请({msgBody.FromQQ})加入群({msgBody.FromGroup})"
        else:
            msgBody.MsgText = f"({msgBody.SendQQ})同意申请者({msgBody.FromQQ})加入群({msgBody.FromGroup})"
        
        return True
    else:
        return False
    
    reader.ReadInt()
    
    msgBody.MsgSequence = reader.ReadInt()

    reader.ReadBytes(8)
    reader.ReadBytes(reader.ReadShort())
    reader.ReadShort()

    msgread = binary.Reader()
    while reader.ReadLength() > 0:
        Type = reader.ReadByte()    # 消息类型
        msgread.Update(reader.ReadBytes(reader.ReadShort()))   # 消息数据
        
        if Type == 0x01:    # 文本
            msgread.ReadByte()
            text = msgread.ReadBytes(msgread.ReadShort()).decode()
            if msgread.ReadLength() == 0:
                msgBody.MsgText += text
            elif text[0] == "@":    # At
                msgread.ReadBytes(10)
                msgBody.MsgText += f"[PQ:at,qq={msgread.ReadInt()}]"
        elif Type == 0x02:  # 表情
            msgread.ReadBytes(3)
            faceid = msgread.ReadByte()
            msgBody.MsgText += f"[PQ:face,id={faceid},name={FaceMap.get(faceid,'未知')}]"
        elif Type == 0x03:  # 图片
            msgread.ReadByte()
            md5Value = msgread.ReadBytes(msgread.ReadShort()).decode()
            msgBody.MsgText += f"[PQ:image,url=https://gchat.qpic.cn/gchatpic_new/0/0-0-{md5Value[:-4]}/0?term=3]"
        elif Type == 0x06:  # 图片
            msgread.ReadByte()
            md5Value = msgread.ReadBytes(msgread.ReadShort()).decode()
            msgBody.MsgText += f"[PQ:image,url=https://gchat.qpic.cn/gchatpic_new/0/0-0-{md5Value[:-4]}/0?term=3]"
    return True