import time
import threading
import pcqq.utils.log as log
import pcqq.utils as utils
import pcqq.binary as binary
import pcqq.client as client

class QQClient(utils.TcpSocket):
    def __init__(self):
        super().__init__()

        # 定义QQClient相关属性
        self.BinQQ = b'\x00'*4
        self.LongQQ = 0
        self.PassWord = ""
        self.NickName = ""

        self.TgtKey = b''
        self.SessionKey = b''

        self.LocalIp = b''
        self.SeverIp = b''
        self.ConnectTime = b''
        self.IsScanCode = True

        for host in ["","2","3","4"]:
            if self.Connect(f"tcpconn{host}.tencent.com", 443):
                self.SeverIp = utils.Hex2Bin(utils.IpToHex(self._addr[0]))
                break
        if self.SeverIp == b'':
            log.error("连接服务器失败，请尝试重新运行程序")
        
    
    def Pack(self, cmd:str, body:bytes, version:bytes=client.BodyVersion, sequence:bytes=utils.GetRandomBin(2))->bytes:
        '''
        组装协议包
        :param cmd: 包命令
        :param sequence: 包序
        :param body: 包体
        :param version: 包版本
        '''
        writer = binary.Writer()
        writer.WriteBytes(client.Header)
        writer.WriteHex(cmd)
        writer.WriteBytes(sequence)
        writer.WriteBytes(self.BinQQ)
        writer.WriteBytes(version)
        if self.SessionKey != b'':
            body = binary.TeaEncrypt(body, self.SessionKey)
        writer.WriteBytes(body)
        writer.WriteBytes(client.Tail)
        return writer.ReadAll()

    def HeartBeat(self):
        '''按40秒每次的频率循环发送心跳包'''

        self.Send(self.Pack(
            cmd="00 58",
            body=b'\x00\x01\x00\x01',
        ))
        threading.Timer(40.0, self.HeartBeat).start()

    def ExitLogin(self):
        '''退出机器人的登录'''
        self.Send(self.Pack(
            cmd="00 62",
            body=b'\x00'*16,
        ))

    def SendPrivateMsg(self, userID:int, msgBody:bytes)->bool:
        '''
        发送私聊消息
        :param userID: 私聊用户的账号
        :param msgBody: 发送的消息数据
        '''
        writer = binary.Writer()
        timeStamp = int(time.time())

        writer.WriteBytes(self.BinQQ)
        writer.WriteInt(userID)
        writer.WriteHex("00 00 00 08 00 01 00 04 00 00 00 00 36 39")
        writer.WriteBytes(self.BinQQ)
        writer.WriteInt(userID)
        writer.WriteBytes(utils.HashMD5(timeStamp.to_bytes(4,"big")))
        writer.WriteHex("00 0B 4A B6")
        writer.WriteBytes(timeStamp.to_bytes(4,"big"))
        writer.WriteHex("02 55 00 00 00 00 01 00 00 00 01 4D 53 47 00 00 00 00 00")
        writer.WriteBytes(timeStamp.to_bytes(4,"big"))
        writer.WriteBytes(timeStamp.to_bytes(4,"little"))
        writer.WriteHex("00 00 00 00 09 00 86 00 00 06 E5 AE 8B E4 BD 93 00 00")
        writer.WriteBytes(msgBody)

        self.Send(self.Pack(
            cmd="00 CD",
            body=writer.ReadAll(),
        ))

        return self.Recv() != b''


    def SendGroupMsg(self, groupID:int, msgBody:bytes)->bool:
        '''
        发送群聊消息
        :param groupID: 聊天群的群号
        :param content: 发送的消息数据
        '''
        writer = binary.Writer()
        timeStamp = int(time.time())

        writer.WriteHex("00 01 01 00 00 00 00 00 00 00 4D 53 47 00 00 00 00 00")
        writer.WriteBytes(timeStamp.to_bytes(4,"big"))
        writer.WriteBytes(timeStamp.to_bytes(4,"little"))
        writer.WriteHex("00 00 00 00 09 00 86 00 00 06 E5 AE 8B E4 BD 93 00 00")
        writer.WriteBytes(msgBody)
        body = writer.ReadAll()
        
        writer.WriteHex("2A")
        writer.WriteInt(groupID)
        writer.WriteShort(len(body))
        writer.WriteBytes(body)

        self.Send(self.Pack(
            cmd="00 02",
            body=writer.ReadAll(),
        ))

        return self.Recv() != b''