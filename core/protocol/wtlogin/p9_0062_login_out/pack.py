from core import const
from core.entities import Packet, QQStruct


def pack_0062(stru: QQStruct):
    packet = Packet(
        cmd="00 62",
        uin=stru.uin,
        tea_key=stru.session_key
    )
    packet.version.write(const.BodyVersion)

    packet.body.write(bytes(16))
    stru.is_running = False
    return packet
