import pcqq.log as log
import pcqq.utils as utils
import pcqq.binary as binary


class QQClient:
    def __init__(self):
        self.__socket__ = utils.TCPSocket()

        for host in ['tcpconn.tencent.com','tcpconn2.tencent.com','tcpconn3.tencent.com','tcpconn4.tencent.com']:
            if not self.__socket__.Connect(host, 443):
                log.Panicln(f'尝试连接到 {self.__socket__.addr[0]} 失败')
                continue
            break
        
        self.ServerIP = bytes(
            [int(v) for v in self.__socket__.addr[0].split('.')])

        self.BinQQ = bytes(4)
        self.LongQQ = 0
        self.PassWord = bytes()

        self.NickName = str()
        self.SessionKey = bytes()
        self.IsScanCode = True

    def Send(self, body: bytes):
        self.__socket__.Send(body=body)

    def Recv(self) -> bytes:
        return self.__socket__.Recv()

    def Pack(self, cmd: str, version: bytes, *bodys: bytes):
        writer = binary.Writer()
        writer.WriteHex("02 36 39")

        writer.WriteHex(cmd)
        writer.WriteBytes(utils.GetRandomBin(2))
        writer.WriteBytes(self.BinQQ)
        writer.WriteBytes(version)

        bin = b''.join(bodys)
        if self.SessionKey:
            bin = binary.TeaEncrypt(bin, self.SessionKey)
        writer.WriteBytes(bin)

        writer.WriteHex("03")
        return writer.ReadAll()