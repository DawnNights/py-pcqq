import pcqq.binary as binary
import pcqq.utils as utils
import pcqq.utils.log as log

from .api import GetNickName
from .const import ALLFACE, ALLEVENT


class Event:
    def __init__(self, bin: bytes):
        self.Time = 0  # 事件发生的时间戳
        self.EventType = ''  # 事件类型

        self.GroupID = 0  # 消息来源群号
        self.UserID = 0  # 发送者QQ号
        self.TargetID = 0  # 执行者QQ号
        self.SelfID = 0  # 机器人QQ号

        self.MessageID = 0  # 消息ID
        self.MessageText = ''  # 消息转义文本

        # 解析消息数据

        reader = binary.Reader(bin)
        self.EventType = ALLEVENT.get(bin[18:20], None)

        if self.EventType == "group":
            reader.ReadBytes(4)
            self.SelfID = reader.ReadInt()  # 自身账号

            reader.ReadBytes(12)
            reader.ReadBytes(reader.ReadInt())
            self.GroupID = reader.ReadInt()  # 消息来源群号

            reader.ReadByte()
            self.UserID = reader.ReadInt()  # 消息来源账号
            self.MessageID = reader.ReadInt()
            self.Time = reader.ReadInt()

            reader.ReadBytes(8)
            reader.ReadBytes(16)

            ParseMsgContent(reader.ReadAll(), self)
            if self.UserID != self.SelfID:
                log.Println(
                    f'收到群聊({self.GroupID})消息 {GetNickName(self.UserID)}: {self.MessageText}'
                )
        elif self.EventType == "private":
            self.UserID = reader.ReadInt()
            self.SelfID = reader.ReadInt()

            reader.ReadBytes(12)
            reader.ReadBytes(reader.ReadInt() + 26)
            reader.ReadBytes(2)

            self.MessageID = reader.ReadShort()
            self.Time = reader.ReadInt()

            reader.ReadBytes(6)
            reader.ReadBytes(4)
            reader.ReadBytes(9)

            ParseMsgContent(reader.ReadAll(), self)
            log.Println(
                f'收到私聊({self.UserID})消息 {GetNickName(self.UserID)}: {self.MessageText}'
            )
        elif self.EventType == "group_increase":

            self.GroupID = utils.GidToGroup(reader.ReadInt())
            self.SelfID = reader.ReadInt()  # 自身账号

            reader.ReadBytes(12)
            reader.ReadBytes(reader.ReadInt() + 5)

            self.UserID = reader.ReadInt()
            sign = reader.ReadByte()
            self.TargetID = reader.ReadInt()

            if sign == 0x02:  # 管理员审核
                log.Println(
                    f"收到群事件: 管理员({self.TargetID})同意申请者({self.UserID})加入群({self.GroupID})"
                )
            elif sign == 0x03:  # 群员邀请无需审核
                log.Println(
                    f"收到群事件: 群员({self.TargetID})成功邀请({self.UserID})加入群({self.GroupID})"
                )
            else:
                log.Println(
                    f"收到群事件: ({self.TargetID})同意申请者({self.UserID})加入群({self.GroupID})"
                )
        elif self.EventType == 'group_reduce':
            self.GroupID = utils.GidToGroup(reader.ReadInt())
            self.SelfID = reader.ReadInt()  # 自身账号

            reader.ReadBytes(12)
            reader.ReadBytes(reader.ReadInt() + 5)

            self.UserID = reader.ReadInt()
            sign = reader.ReadByte()
            self.TargetID = reader.ReadInt()

            if sign == 1:  # 群解散
                log.Println(f"收到群事件: 群主({self.TargetID})解散了群({self.GroupID})")
            elif sign == 2:  # 主动退出
                log.Println(f"收到群事件: 群员({self.UserID})退出了群({self.GroupID})")
            elif sign == 3:  # 被踢出
                log.Println(
                    f"收到群事件: 群员({self.UserID})被管理员({self.TargetID})踢出了群({self.GroupID})"
                )


def ParseMsgContent(bin: bytes, event):
    reader = binary.Reader(bin)

    reader.ReadBytes(16)
    reader.ReadBytes(reader.ReadShort())
    reader.ReadShort()

    while reader.ReadLen() > 0:
        Type = reader.ReadByte()  # 消息类型
        msgread = binary.Reader(reader.ReadBytes(reader.ReadShort()))  # 消息数据

        if Type == 0x01:  # 文本
            msgread.ReadByte()
            text = msgread.ReadBytes(msgread.ReadShort()).decode()
            if msgread.ReadLen() == 0:
                event.MessageText += text
            elif text[0] == "@":  # At
                msgread.ReadBytes(10)
                event.MessageText += f"[PQ:at,qq={msgread.ReadInt()}]"
        elif Type == 0x02:  # 表情
            msgread.ReadBytes(3)
            faceid = msgread.ReadByte()
            event.MessageText += f"[PQ:face,id={faceid},name={ALLFACE.get(faceid,'未知')}]"
        elif Type == 0x03:  # 图片
            msgread.ReadByte()
            md5Value = msgread.ReadBytes(msgread.ReadShort()).decode().upper()
            event.MessageText += f"[PQ:image,url=https://gchat.qpic.cn/gchatpic_new/0/0-0-{md5Value[:-4]}/0?term=3]"
        elif Type == 0x06:  # 图片
            msgread.ReadByte()
            md5Value = msgread.ReadBytes(msgread.ReadShort()).decode().upper()
            event.MessageText += f"[PQ:image,url=https://gchat.qpic.cn/gchatpic_new/0/0-0-{md5Value[:-4]}/0?term=3]"