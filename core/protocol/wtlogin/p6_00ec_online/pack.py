from core import const
from core.entities import Packet, QQStruct


def pack_00ec(stru: QQStruct):
    packet = Packet(
        cmd="00 EC",
        uin=stru.uin,
        tea_key=stru.session_key
    )
    packet.version.write(const.BodyVersion)
    
    packet.body.write_hex("01 00")
    packet.body.write_byte(const.StateOnline) # 上线
    packet.body.write_hex("00 01")
    packet.body.write_hex("00 01")
    packet.body.write_hex("00 04")
    packet.body.write_hex("00 00 00 00")

    return packet