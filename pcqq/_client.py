import socket

class QQClient:
    def __init__(self):
        # hosts = ['tcpconn.tencent.com', 'tcpconn2.tencent.com', 'tcpconn3.tencent.com', 'tcpconn4.tencent.com']
        host = socket.gethostbyname("tcpconn.tencent.com")
        self._client = socket.socket()
        self._client.settimeout(7.0)
        self._client.connect((host, 443))

    def Send(self, body:bytes):
        length = len(body) + 2
        body = length.to_bytes(2, "big") + body
        self._client.send(body)
    
    def Recv(self)->bytes:
        return self._client.recv(10240)
    
    def Close(self):
        self._client.close()