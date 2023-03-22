from core import utils
from core import const
from core.entities import Packet, QQStruct


def pack_0818(stru: QQStruct):
    packet = Packet(
        cmd="08 18",
        tea_key=const.RandKey
    )
    packet.version.write(const.StructVersion).write(const.RandKey)

    def tlv_019(ns: utils.Stream):
        ns.write_hex("00 01")
        ns.write(const.SsoVersion)
        ns.write(const.ServiceId)
        ns.write(const.ClientVersion)
        ns.write_hex("00 00")

        ns.write_tlv("00 19", ns.read_all())
    packet.body.write_func(tlv_019)

    def tlv_114(ns: utils.Stream):
        ns.write(const.EcdhVersion)
        ns.write_token(stru.ecdh.public_key)

        ns.write_tlv("01 14", ns.read_all())
    packet.body.write_func(tlv_114)

    packet.body.write_hex("03 05 00 1E 00 00 00 00 00 00 00 05 00 00 00 04 00")
    packet.body.write_hex("00 00 00 00 00 00 48 00 00 00 02 00 00 00 02 00 00")
    packet.body.write_hex("00 15 00 30 00 01 01 45 AA 72 E9 00 10")
    packet.body.write_hex("6B 10 A0 47 00 00 00 00 00 00 00 00 00")
    packet.body.write_hex("00 00 00 02 9A 76 CB 8F 00 10 D4 61 6E")
    packet.body.write_hex("EB D5 B6 4E 2C 5B 6C FA C3 E0 FD 53 90")

    return packet
