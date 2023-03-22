from core import utils
from core import const
from core.entities import Packet, QQStruct


def pack_0825(stru: QQStruct):
    packet = Packet(
        cmd="08 25",
        uin=stru.uin,
        tea_key=const.RandKey
    )
    packet.version.write(const.StructVersion).write(const.RandKey)

    def tlv_018(ns: utils.Stream):
        ns.write_hex("00 01")
        ns.write(const.SsoVersion)
        ns.write(const.ServiceId)
        ns.write(const.ClientVersion)
        ns.write_int32(stru.uin)
        ns.write_int16(stru.redirection_times)
        ns.write_hex("00 00")

        ns.write_tlv("00 18", ns.read_all())
    packet.body.write_func(tlv_018)

    def tlv_309(ns: utils.Stream):
        ns.write_hex("00 0A 00 04")
        ns.write_hex("00 00 00 00")

        if stru.redirection_times > 0:
            ns.write_byte(stru.redirection_times)
            ns.write_hex("00 04")
            ns.write(stru.redirection_history)
        ns.write_hex("00 04")

        ns.write_tlv("03 09", ns.read_all())
    packet.body.write_func(tlv_309)

    def tlv_036(ns: utils.Stream):
        ns.write_hex("00 02 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00")

        ns.write_tlv("00 36", ns.read_all())
    packet.body.write_func(tlv_036)

    def tlv_114(ns: utils.Stream):
        ns.write(const.EcdhVersion)

        ns.write_token(stru.ecdh.public_key)

        ns.write_tlv("01 14", ns.read_all())
    packet.body.write_func(tlv_114)

    def tlv_511(ns: utils.Stream):
        ns.write_hex("0A 00 00 00 00 01")

        ns.write_tlv("05 11", ns.read_all())
    packet.body.write_func(tlv_511)

    return packet
