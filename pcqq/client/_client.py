import time
import socket
import threading
import pcqq.log as log
import pcqq.const as const
import pcqq.utils as utils
import pcqq.binary as binary

class QQClient:
    def __init__(self):
        self._sock = socket.socket()
        self._sock.settimeout(6.0)  # 创建套接字，设置6秒超时

        ip = socket.gethostbyname('tcpconn.tencent.com')
        try:
            self._sock.connect((ip, 443))
            self.SeverIp = b''.join([int(i).to_bytes(1, "big") for i in ip.split(".")])
        except Exception as error:
            log.Panicln(error=error)
        
        self.BinQQ = b'\x00'*4
        self.LongQQ = 0
        self.PassWord = ""
        self.NickName = ""

        self.SessionKey = b''
        self.IsScanCode = True
    
    def Send(self, body:bytes):
        self._sock.send((len(body)+2).to_bytes(2, "big") + body)
    
    def Recv(self)->bytes:
        try:
            return self._sock.recv(1024*8)
        except Exception as err:
            return b''

    def Pack(self, cmd:str, body:bytes, version:bytes=const.BodyVersion, sequence:bytes=utils.GetRandomBin(2))->bytes:
        '''
        组装协议包
        :param cmd: 包命令
        :param sequence: 包序
        :param body: 包体
        :param version: 包版本
        '''
        writer = binary.Writer()
        writer.WriteBytes(const.Header)

        writer.WriteHex(cmd)
        writer.WriteBytes(sequence)

        writer.WriteBytes(self.BinQQ)
        writer.WriteBytes(version)
        
        if self.SessionKey != b'':
            body = binary.TeaEncrypt(body, self.SessionKey)
        writer.WriteBytes(body)

        writer.WriteBytes(const.Tail)
        return writer.ReadAll()
    
    def HeartBeat(self):
        '''按40秒每次的频率循环发送心跳包'''
        self.Send(self.Pack(
            cmd="00 58",
            body=b'\x00\x01\x00\x01',
        ))
        threading.Timer(40.0, self.HeartBeat).start()
    
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