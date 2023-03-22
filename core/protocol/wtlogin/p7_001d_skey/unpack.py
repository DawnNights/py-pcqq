from functools import partial
from core.entities import Packet, PacketHandler, QQStruct


def check_001d(packet: Packet):
    return packet.cmd == "00 1D"


async def handle_001d(stru: QQStruct, packet: Packet):
    packet.body.read(2)
    stru.skey = packet.body.read_token().decode()
    stru.bkn = gtk_skey(stru.skey)
    stru.cookie = "uin=o%d; skey=%s" % (stru.uin, stru.skey)


def unpack_001d(stru: QQStruct):
    return PacketHandler(
        temp=True,
        check=check_001d,
        handle=partial(handle_001d, stru)
    )


def gtk_skey(skey: str) -> int:
    accu = 5381
    for s in skey:
        accu += (accu << 5) + ord(s)
    return accu & 2147483647
