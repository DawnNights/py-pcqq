from core import const
from core.entities import Packet, QQStruct


def pack_0058(stru: QQStruct):
    packet = Packet(
        cmd="00 58",
        uin=stru.uin,
        tea_key=stru.session_key
    )

    packet.version.write(const.BodyVersion)
    packet.body.write_hex("00 01 00 01")

    return packet
