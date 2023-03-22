from binascii import crc32

from core import utils, croto
from core import const
from core.entities import Packet, QQStruct


def pack_0828(stru: QQStruct):
    packet = Packet(
        cmd="08 28",
        uin=stru.uin,
        tea_key=stru.pckey_for_0828_send
    )
    packet.version.write(const.BodyVersion).write_hex("00 30 00 3A 00 38")
    packet.version.write(stru.token_0038_from_0836)

    def tlv_007(ns: utils.Stream):
        ns.write_tlv("00 07", stru.token_0088_from_0836)
    packet.body.write_func(tlv_007)

    def tlv_00c(ns: utils.Stream):
        ns.write_hex("00 02 00 00 00 00 00 00 00 00 00 00")
        ns.write(stru.server_ip)
        ns.write_int16(stru.addr[1])
        ns.write_hex("00 00 00 00")

        ns.write_tlv("00 0C", ns.read_all())
    packet.body.write_func(tlv_00c)

    def tlv_015(ns: utils.Stream):
        computer_id = croto.md5(f"{stru.uin}ComputerID".encode())
        computer_id2 = croto.md5(f"{stru.uin}ComputerIDEx".encode())

        ns.write_hex("00 00 01")

        ns.write_int32(crc32(computer_id2))
        ns.write_int16(16)
        ns.write(computer_id2)
        ns.write_byte(2)

        ns.write_int32(crc32(computer_id))
        ns.write_int16(16)
        ns.write(computer_id)

        ns.write_tlv("00 15", ns.read_all())
    packet.body.write_func(tlv_015)

    def tlv_036(ns: utils.Stream):
        ns.write_hex("00 02")
        ns.write_hex("00 01")
        ns.write(bytes(14))

        ns.write_tlv("00 36", ns.read_all())
    packet.body.write_func(tlv_036)

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

    def tlv_01f(ns: utils.Stream):
        ns.write_hex("00 01")
        ns.write(const.DeviceID)

        ns.write_tlv("00 1F", ns.read_all())
    packet.body.write_func(tlv_01f)

    def tlv_105(ns: utils.Stream):
        ns.write_int16(1)
        ns.write_hex("01 02")

        ns.write_int16(20)
        ns.write_hex("01 01")
        ns.write_int16(16)
        ns.write(utils.rand_bytes(16))

        ns.write_int16(20)
        ns.write_hex("01 02")
        ns.write_int16(16)
        ns.write(utils.rand_bytes(16))

        ns.write_tlv("01 05", ns.read_all())
    packet.body.write_func(tlv_105)

    def tlv_10b(ns: utils.Stream):
        ns.write_hex("00 02")
        ns.write(utils.rand_bytes(16))  # ClientMD5 服务端不作校验
        ns.write(utils.rand_bytes(1))  # QDFlag 服务端不作校验
        ns.write_hex("10 00 00 00 00 00 00 00 02")

        # QDDATA 服务端不作校验

        ns.write_hex("00 63")
        ns.write_hex("3E 00 63 02")
        ns.write(const.DWQDVersion)
        ns.write_hex("00 04 00")
        ns.write(utils.rand_bytes(2))
        ns.write_hex("00 00 00 00")
        ns.write(utils.rand_bytes(16))

        ns.write_hex("01 00")
        ns.write_hex("00 00 00 00")
        ns.write_hex("00 00")
        ns.write_hex("00 00 00 00 00 00 00 00")

        ns.write_hex("00 00 00 01")
        ns.write_hex("00 00 00 01")
        ns.write_hex("00 00 00 01")
        ns.write_hex("00 00 00 01")
        ns.write_hex("00 FE 26 81 75 EC 2A 34 EF")

        ns.write_hex("02 3E 50 39 6D B1 AF CC 9F EA 54 E1")
        ns.write_hex("70 CC 6C 9E 4E 63 8B 51 EC 7C 84 5C")

        ns.write_hex("68")
        ns.write_hex("00 00 00 00")

        ns.write_tlv("01 0B", ns.read_all())
    packet.body.write_func(tlv_10b)

    def tlv_20d(ns: utils.Stream):
        ns.write_hex("00 01")
        ns.write(stru.local_ip)

        ns.write_tlv("02 0D", ns.read_all())
    packet.body.write_func(tlv_20d)

    return packet
