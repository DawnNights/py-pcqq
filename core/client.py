from socket import socket

class NetClient():
    def __init__(self):
        self.client = socket()

    def Connect(self):
        self.client.connect(("123.151.77.237", 443))

    def Send(self,body:bytes):
        length = len(body)+2
        self.client.send(length.to_bytes(2,"big")+body)

    def Receive(self)->bytes:
        return self.client.recv(20480)