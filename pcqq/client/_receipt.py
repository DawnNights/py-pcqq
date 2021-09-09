import pcqq.utils as utils
import pcqq.binary as binary


def GroupReceipt(QQ, msgBody, Type):
    '''群消息回执'''
    writer = binary.Writer()

    if Type == 0:   # 群消息回执
        writer.WriteByte(41)
        writer.WriteInt(utils.GroupToGid(msgBody.FromGroup))
        writer.WriteByte(2)
        writer.WriteInt(msgBody.MsgID)
    else:   # 讨论组消息回执
        writer.WriteArray(62, 1, 0, 0, 0, 0)
        writer.WriteInt(msgBody.FromGroup)
        writer.WriteInt(msgBody.MsgID)
    
    QQ.Send(QQ.Pack(
        cmd="00 02",
        body=writer.ReadAll()
    ))

def PrivateReceipt(QQ, msgBody):
    '''私聊消息回执'''
    writer = binary.Writer()

    writer.WriteHex("08 01")
    writer.WriteHex("12 03 98 01 00")
    writer.WriteHex("0A 0E 08")

    writer.WriteVarInt(msgBody.FromQQ)
    writer.WriteHex("10")
    writer.WriteVarInt(msgBody.MsgTime)
    writer.WriteHex("20 00")
    body = writer.ReadAll()

    writer.WriteHex("00 00 00 07")
    writer.WriteInt(len(body)-7)
    writer.WriteBytes(body)

    QQ.Send(QQ.Pack(
        cmd="08 19",
        body=writer.ReadAll(),
    ))