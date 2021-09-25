import socket

class TCPSocket(socket.socket):
    def Connect(self, host: str, port: int) -> bool:
        self.settimeout(6.0)
        self.addr = (socket.gethostbyname(host), port)

        try:
            self.connect(self.addr)
            return True
        except:
            return False

    def Send(self, body: bytes):
        head = (len(body) + 2).to_bytes(2, 'big')
        self.send(head + body)

    def Recv(self) -> bytes:
        try:
            return self.recv(1024 * 8)
        except:
            return bytes()