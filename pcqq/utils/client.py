import random
import socket
import asyncio


def get_tcp_host() -> str:
    domain = random.choice([
        "tcpconn.tencent.com",
        "tcpconn2.tencent.com",
        "tcpconn3.tencent.com",
        "tcpconn4.tencent.com"
    ])
    return socket.gethostbyname(domain)


def get_udp_host() -> str:
    domain = random.choice([
        "sz.tencent.com",
        "sz2.tencent.com",
        "sz3.tencent.com",
        "sz4.tencent.com",
        "sz5.tencent.com",
        "sz6.tencent.com",
        "sz7.tencent.com",
        "sz8.tencent.com",
        "sz9.tencent.com",
    ])
    return socket.gethostbyname(domain)


class Client:
    kind: str = ""
    host: str = ""
    inet: bytes = b""
    sock: socket.socket = None

    def send(self, data: bytes) -> None:
        pass

    def recv(self) -> bytes:
        pass

    def listen(self, main_loop, handler) -> None:
        pass


class UDPClient(Client):
    def __init__(self) -> None:
        self.kind = "UDP"
        self.host = get_udp_host()
        self.inet = socket.inet_aton(self.host)
        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
            socket.IPPROTO_UDP
        )
        # self.sock.settimeout(6.0)

    def send(self, data: bytes) -> None:
        self.sock.sendto(data, (self.host, 8000))

    def recv(self) -> bytes:
        data, _ = self.sock.recvfrom(1024 * 30)
        return data

    def listen(self, main_loop, handler) -> None:
        while True:
            asyncio.run_coroutine_threadsafe(
                loop=main_loop,
                coro=handler(self.recv())
            )


class TCPClient(Client):
    def __init__(self) -> None:
        self.kind = "TCP"
        self.host = get_tcp_host()
        self.inet = socket.inet_aton(self.host)
        self.sock = socket.socket()
        # self.sock.settimeout(6.0)
        self.sock.connect((self.host, 443))

    def send(self, data: bytes) -> None:
        head = (len(data) + 2).to_bytes(2, "big")
        self.sock.send(head + data)

    def recv(self) -> bytes:
        return self.sock.recv(1024 * 30)[2:]

    def listen(self, main_loop, handler) -> None:
        while True:
            asyncio.run_coroutine_threadsafe(
                loop=main_loop,
                coro=handler(self.recv())
            )
