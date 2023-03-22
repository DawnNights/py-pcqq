import socket
import asyncio


class AsyncTCPSocket:
    def __init__(self, host, port, loop):
        self.host = host
        self.port = port
        self.loop = loop
        self.lock = asyncio.Lock(loop=loop)

    async def init(self):
        reader, writer = await asyncio.open_connection(
            host=self.host,
            port=self.port,
            loop=self.loop
        )

        self.reader = reader
        self.writer = writer

    def send(self, data: bytes):
        size = len(data) + 2
        self.writer.write(size.to_bytes(2, "big") + data)

    async def recv(self):
        async with self.lock:
            temp = await self.reader.read(2)
            size = int.from_bytes(temp, "big")

            data = await self.reader.read(size)
        return data


class UDPSocket:
    def __init__(self, host: str, port: int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(60)

        self.host = socket.gethostbyname(host)
        self.port = port

    def send(self, data: bytes):
        return self.sock.sendto(data, (self.host, self.port))

    def recv(self):
        data, _ = self.sock.recvfrom(1024 * 10)
        return data
