import socket
import pcqq.utils.log as log

class TcpSocket:
    def __init__(self):
        self._sock = socket.socket()
        self._sock.settimeout(6.0)
    
    def Connect(self, host:str, port:int)->bool:
        self._addr = (socket.gethostbyname(host), port)
        try:
            self._sock.connect(self._addr)
            log.debug(f"正在尝试连接服务器 -> {self._addr[0]} -> 连接成功")
            return True
        except:
            log.debug(f"正在尝试连接服务器 -> {self._addr[0]} -> 连接失败")
            return False
    
    def Send(self, body:bytes):
        self._sock.send((len(body)+2).to_bytes(2, "big") + body)
    
    def Recv(self)->bytes:
        try:
            return self._sock.recv(1024*8)
        except Exception as err:
            # log.warning(err)
            return b''
    
    def Close(self):
        self._sock.close()