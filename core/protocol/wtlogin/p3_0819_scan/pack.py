from core import utils
from core import const
from core.entities import Packet, QQStruct


def pack_0819(stru: QQStruct):
    packet = Packet(
        cmd="08 19",
        uin=stru.uin,
        tea_key=stru.pckey_for_0819
    )
    packet.version.write(const.StructVersion)
    packet.version.write_hex("00 30").write_token(stru.token_0038_from_0818)

    def tlv_019(ns: utils.Stream):
        ns.write_hex("00 01")
        ns.write(const.SsoVersion)
        ns.write(const.ServiceId)
        ns.write(const.ClientVersion)
        ns.write_hex("00 00")

        ns.write_tlv("00 19", ns.read_all())
    packet.body.write_func(tlv_019)

    packet.body.write_hex("03 01").write_token(stru.token_by_scancode)
    return packet
