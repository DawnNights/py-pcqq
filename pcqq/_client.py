import socket

class QQClient():
    def __init__(self):
        # self._client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # self._client.settimeout(5.0)
        # domains = "sz.tencent.com|sz2.tencent.com|sz3.tencent.com|sz4.tencent.com|sz5.tencent.com|sz6.tencent.com|sz7.tencent.com|sz8.tencent.com|sz9.tencent.com".split("|")

        self._client = socket.socket()
        # self._client.settimeout(5.0)
        domains = "tcpconn.tencent.com|tcpconn2.tencent.com|tcpconn3.tencent.com|tcpconn4.tencent.com".split("|")

        for name in domains:
            ip = socket.gethostbyname(name)
            try:
                self._client.connect((ip, 443))
                print("服务器可用性测试->", ip, "连接成功")
                break
            except:
                print("服务器可用性测试->", ip, "连接失败")

        self.BinQQ = b''
        self.LongQQ = 0
        self.Utf8QQ = b''
        self.Redirection = 0

        self.Time = b''
        self.NickName = ''

        self.RandHead16 = b''
        self.SessionKey = b''
        self.ClientKey = b''
        self.ShareKey = b''
        self.PublicKey = b''

        self.PcKeyFor0819 = b''
        self.PcKeyTgt = b''
        self.PcKeyFor0828Send = b''
        self.PcKeyFor0828Rev = b''
        self.PcToken0038From0825 = b''
        self.PcToken0038From0818 = b''
        self.PcToken0060From0819 = b''
        self.PcToken0038From0836 = b''
        self.PcToken0088From0836 = b''

        self.LocalPcIp = b''
        self.ConnectSeverIp = b''

    def Send(self, body:bytes):
        length = len(body)+2
        self._client.send(length.to_bytes(2, "big") + body)

    def Recv(self)->bytes:
        return self._client.recv(1024*10)