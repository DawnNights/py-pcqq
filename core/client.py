import os
import traceback

from socket import inet_aton
from functools import partial
from asyncio import (
    Queue,
    new_event_loop,
    run_coroutine_threadsafe
)

from core.entities import (
    Packet,
    QQStruct,
    PacketManger,
)

from core import croto, const

from core.utils import (
    UDPSocket,
    rand_udp_host
)


class QQClient:
    def __init__(self, uin: int = 0):
        self.loop = new_event_loop()

        self.sock = UDPSocket(
            host=rand_udp_host(),
            port=const.UDP_PORT,
        )
        self.manage = PacketManger()

        root = os.path.join(os.getcwd(), "data")
        if uin != 0:
            root = os.path.join(root, str(uin))

        if not os.path.exists(root):
            os.makedirs(root)

        self.stru = QQStruct(
            path=root,
            ecdh=croto.ECDH(),
            addr=(self.sock.host, self.sock.port),
            server_ip=inet_aton(self.sock.host)
        )

        self.run_task = self.loop.run_until_complete
        self.add_task = partial(run_coroutine_threadsafe, loop=self.loop)

    def send(self, packet: Packet):
        data = packet.encode()
        self.sock.send(data)

    def recv(self, tea_key: bytes):
        data = self.sock.recv()
        return Packet.from_raw(data, tea_key)

    async def recv_and_exec(self, tea_key: bytes):
        try:
            packet = self.recv(tea_key)
            await self.manage.exec_all(packet)
        except Exception as err:
            print('发生异常: ', traceback.format_exc())