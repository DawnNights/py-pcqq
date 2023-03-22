from time import time
from binascii import crc32

from core import utils, croto
from logger import logger
from core import const
from core.entities import Packet, QQStruct

private_0836key = const.RandKey
bufOfficiaKey = utils.rand_bytes(16)
OfficialData = utils.rand_bytes(56)

def pack_0836(stru: QQStruct):
    packet = Packet(cmd="08 36", tea_key=stru.ecdh.share_key, uin=stru.uin)
    packet.version.write(const.StructVersion).write_hex("00 02")
    packet.version.write(const.EcdhVersion)
    packet.version.write_token(stru.ecdh.public_key).write_hex("00 00")
    packet.version.write_token(private_0836key)

    computer_id = croto.md5(f"{stru.uin}ComputerID".encode())
    computer_id_ex = croto.md5(f"{stru.uin}ComputerIDEx".encode())
    private_bufMacGuid = croto.md5(f"{stru.uin}bufMacGuid".encode())

    def tlv_112(ns: utils.Stream):
        ns.write_tlv("01 12", stru.token_0038_from_0825)
    packet.body.write_func(tlv_112)

    def tlv_30f(ns: utils.Stream):
        ns.write_token(b'PY-PCQQ')
        ns.write_tlv("03 0F", ns.read_all())
    packet.body.write_func(tlv_30f)

    def tlv_005(ns: utils.Stream):
        ns.write_hex("00 02")
        ns.write_int32(stru.uin)

        ns.write_tlv("00 05", ns.read_all())
    packet.body.write_func(tlv_005)

    if stru.is_scancode:
        def tlv_303(ns: utils.Stream):
            ns.write_tlv("03 03", stru.password)
        packet.body.write_func(tlv_303)

        private_bufOfficial = croto.create_official(bufOfficiaKey, OfficialData, stru.password[2:])
    else:
        logger.fatal("账密登录待开发, 请优先使用扫码登录")
        raise RuntimeError("Can't login by password")

    def tlv_015(ns: utils.Stream):
        computer_id2 = computer_id_ex[0:4] + bytes(12)

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

    def tlv_01a(ns: utils.Stream):
        ns.write_func(tlv_015)
        ns.write_tlv("00 1A", croto.tea_encrypt(ns.read_all(), stru.tgt_key))
    packet.body.write_func(tlv_01a)

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

    def tlv_103(ns: utils.Stream):
        ns.write_hex("00 01")
        ns.write_hex("00 10")
        ns.write(private_bufMacGuid)

        ns.write_tlv("01 03", ns.read_all())
    packet.body.write_func(tlv_103)

    def tlv_312(ns: utils.Stream):
        ns.write_tlv("03 12", bytes.fromhex("01 00 00 00 00"))
    packet.body.write_func(tlv_312)

    def tlv_508(ns: utils.Stream):
        ns.write_hex("01 00 00 00")
        ns.write_byte(2)

        ns.write_tlv("05 08", ns.read_all())
    packet.body.write_func(tlv_508)

    def tlv_313(ns: utils.Stream):
        ns.write_hex("01 01 02")
        ns.write_hex("00 10")
        ns.write(private_bufMacGuid)
        ns.write_hex("00 00 00 10")

        ns.write_tlv("03 13", ns.read_all())
    packet.body.write_func(tlv_313)

    def tlv_102(ns: utils.Stream):
        ns.write_hex("00 91")
        ns.write(bufOfficiaKey)

        ns.write_hex("00 38")
        ns.write(OfficialData)

        ns.write_hex("00 14")
        ns.write(private_bufOfficial)
        ns.write_int32(crc32(private_bufOfficial))

        ns.write_tlv("01 02", ns.read_all())
    packet.body.write_func(tlv_102)

    def tlv_501(ns: utils.Stream):
        vFix = bytes([67, 70, 57, 109, 89, 84, 77, 114, 109, 49,
                     75, 85, 48, 109, 121, 101, 54, 52, 80, 118])
        v2 = 872529248  # int((time.time()-psutil.boot_time()) * 1000)

        v13 = bytearray()
        v1 = croto.rand_str2(v13)
        v3 = int(time()).to_bytes(8, 'little') + v1 + computer_id
        v4 = croto.sha1024(v3, bytes(v13))
        tlv0551_key = croto.md5(v4)

        ns.write_int32(stru.uin)
        ns.write(const.SsoVersion)
        ns.write_int32(v2)
        ns.write_hex("00 00 08 36")
        ns.write_token(private_bufMacGuid)
        enc = ns.read_all()

        byte10 = bytearray()
        v23 = croto.sub_16F90(enc, byte10, vFix, v13)

        ns.write(const.SsoVersion)
        ns.write_int32(65536)
        ns.write_byte(109)
        ns.write_int32((1 | ((0 | (0 << 8)) << 8)) << 8)
        ns.write_int32((2 | ((0 | (0 << 8)) << 8)) << 8)
        ns.write_int32((2 | ((0 | (0 << 8)) << 8)) << 8)
        ns.write(bytes(byte10))
        ns.write_int32(v2)
        ns.write_int32(4)
        ns.write_byte(20)
        ns.write(v23)
        ns.write(tlv0551_key)
        ns.write_token(b'5151')

        ns.write_tlv("05 51", ns.read_all())
    packet.body.write_func(tlv_501)

    return packet