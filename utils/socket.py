import socket

class TCPSocket(socket.socket):
    def __init__(self, host: str, port: int):
        super().__init__()
        self.settimeout(6.0)
        self.addr = (socket.gethostbyname(host), port)
        self.connect(self.addr)

    def Send(self, body: bytes):
        head = (len(body) + 2).to_bytes(2, 'big')
        self.send(head + body)

    def Recv(self) -> bytes:
        try:
            return self.recv(1024 * 8)
        except:
            return bytes()