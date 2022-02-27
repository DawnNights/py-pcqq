import pcqq.utils as utils
import pcqq.binary as binary


def _tlv(cmd: str, bin: bytes) -> bytes:
    writer = binary.Writer()

    writer.write_hex(cmd)
    writer.write_int16(len(bin))
    writer.write(bin)

    return writer.clear()


def tlv112(token: bytes) -> bytes:
    """
    TLV_0112_SigIP2

    :param token: Token 0038 From 0825 Protocol Package

    """
    writer = binary.Writer()

    writer.write(token)

    return _tlv("01 12", writer.clear())


def tlv30f() -> bytes:
    """
    TLV_030F_ComputerName

    :param pc_name: Name of the Login Computer

    """
    writer = binary.Writer()

    writer.write_int16(15)
    writer.write_hex("44 61 77 6E 4E 69 67 68 74 73 2D 50 43 51 51")

    return _tlv("03 0F", writer.clear())


def tlv005(uin: int) -> bytes:
    """
    TLV_0005_Uin

    :param uin: QQ Number

    """
    writer = binary.Writer()

    writer.write_hex("00 02")
    writer.write_int32(uin)

    return _tlv("00 05", writer.clear())

def tlv303(token:bytes)->bytes:
    """
    TLV_0303_UnknownTag

    :param token: PcToken 0060 From 0819 Protocol Package

    """
    writer = binary.Writer()

    writer.write(token)

    return _tlv("03 03", writer.clear())


def tlv006(
    uin: int,
    tgtgt_key: bytes,
    md5_once: bytes,
    md5_twice: bytes,
    login_time: bytes,
    local_ip: bytes,
    computer_id: bytes,
    tgtgt: bytes

) -> bytes:
    """
    TLV_0006_TGTGT

    :param uin: QQ Number

    :param tgtgt_key: TGTGTKey

    :param md5_once: The password MD5 is encrypted once

    :param md5_twice: The password MD5 is encrypted twice

    :param login_time: Time to Login QQ Server 

    :param local_ip: Local IP Address

    :param computer_id: Computer device ID

    :param tgtgt: TGTGT

    """
    writer = binary.Writer()

    if tgtgt:
        writer.write(tgtgt)
    else:
        writer.write(utils.randbytes(4))
        writer.write_hex("00 02")
        writer.write_int32(uin)
        writer.write_hex("00 00 04 4C")
        writer.write_hex("00 00 00 01")
        writer.write_hex("00 00 15 51")
        writer.write_hex("00 00 00")
        writer.write(md5_once)
        writer.write(login_time)
        writer.write_hex("00 00 00 00 00 00 00 00 00 00 00 00 00")
        writer.write(local_ip)
        writer.write_hex("00 00 00 00 00 00 00 00 00 10")
        writer.write(computer_id)
        writer.write(tgtgt_key)

    tea = binary.QQTea(md5_twice)
    return _tlv("00 06", tea.encrypt(writer.clear()))


def tlv015() -> bytes:
    """
    TLV_0015_ComputerGuid

    """
    writer = binary.Writer()

    writer.write_hex("00 01 01 74 83 F2 C3 00 10 14 FE 77 FC")
    writer.write_hex("00 00 00 00 00 00 00 00 00 00 00 00")
    writer.write_hex("02 17 65 6E 9D 00 10 78 8A 33 DD 00 76 A1 78 EB 8E 5B BB FF 17 D0 10")

    return _tlv("00 15", writer.clear())


def tlv01a(tgtkey: bytes) -> bytes:
    """
    TLV_001A_GTKeyTGTGTCryptedData

    :param tgtkey: Tgtkey

    """
    writer = binary.Writer()

    writer.write_hex("00 01 01 74 83 F2 C3 00 10 14 FE 77 FC")
    writer.write_hex("00 00 00 00 00 00 00 00 00 00 00 00")
    writer.write_hex(
        "02 17 65 6E 9D 00 10 78 8A 33 DD 00 76 A1 78 EB 8E 5B BB FF 17 D0 10")
        
    tea = binary.QQTea(tgtkey)
    return _tlv("00 1A", tea.encrypt(writer.clear()))


def tlv018(uin: int, redirect_times: int) -> bytes:
    """
    TLV_0018_Ping

    :param uin: QQ Number

    :param redirect_times: Times of QQ Server redirects

    """
    writer = binary.Writer()

    writer.write_hex("00 01 00 00 04 4C 00 00 00 01 00 00 15 51")
    writer.write_int32(uin)
    writer.write_int16(redirect_times)
    writer.write_hex("00 00")

    return _tlv("00 18", writer.clear())


def tlv019() -> bytes:
    """
    TLV_0019_Ping

    """
    writer = binary.Writer()

    writer.write_hex("00 01")
    writer.write_hex("00 00 04 56")
    writer.write_hex("00 00 00 01")
    writer.write_hex("00 00 16 03")
    writer.write_hex("00 00")

    return _tlv("00 19", writer.clear())


def tlv114() -> bytes:
    """
    TLV_0114_DHParams

    """
    writer = binary.Writer()

    writer.write_hex("01 03")
    writer.write_hex("00 19")
    writer.write_hex("02 F0 3C 70 7B 85 60 78 04 0F 8F 26 3D 43 1F 66 5E F3 6C 5D C0 45 AD 61 A6")

    return _tlv("01 14", writer.clear())


def tlv103() -> bytes:
    """
    TLV_0103_SID

    """
    writer = binary.Writer()

    writer.write_hex("00 01 00 10")
    writer.write(utils.randbytes(16))

    return _tlv("01 03", writer.clear())


def tlv312() -> bytes:
    """
    TLV_0312_Misc_Flag

    """
    writer = binary.Writer()

    writer.write_hex("01 00 00 00 00")

    return _tlv("03 12", writer.clear())


def tlv508() -> bytes:
    """
    TLV_0508_UnknownTag

    """
    writer = binary.Writer()

    writer.write_hex("01 00 00 00 02")

    return _tlv("05 08", writer.clear())


def tlv313() -> bytes:
    """
    TLV_0313_GUID_Ex

    """
    writer = binary.Writer()

    writer.write_hex("01 01 02 00 10 EE 47 7F A4 BC D6 EE 65 02 65 4D E9 43 38 4C 3D 00 00 00 EB")

    return _tlv("03 13", writer.clear())


def tlv102(token: bytes) -> bytes:
    """
    TLV_0102_Official

    : param token: Token 0038 From 0825 Protocol Package

    """
    writer = binary.Writer()

    writer.write_hex("00 01")
    writer.write(utils.randbytes(16))
    writer.write_int16(len(token))
    writer.write(token)
    writer.write_hex("00 14")
    writer.write(utils.randbytes(20))

    return _tlv("01 02", writer.clear())


def tlv309(
    server_ip: bytes,
    redirection_history: bytes,
    redirection_times: int
) -> bytes:
    """
    TLV_0309_Ping_Strategy

    :param server_ip: QQ Server IP Address

    :param redirect_history: History of QQ Server redirects

    :param redirect_times: Times of QQ Server redirects

    """
    writer = binary.Writer()

    writer.write_hex("00 01")
    writer.write(server_ip)

    if redirection_times:
        writer.write_byte(redirection_times)
        writer.write(redirection_history)
    else:
        writer.write_hex("00 02")

    return _tlv("03 09", writer.clear())


def tlv036() -> bytes:
    """
    TLV_0036_LoginReason

    """
    writer = binary.Writer()

    writer.write_hex("00 02")
    writer.write_hex("00 01")
    writer.write_hex("00 00 00 00 00 00 00 00 00 00 00 00 00 00")

    return _tlv("00 36", writer.clear())


def tlv007(token: bytes) -> bytes:
    """
    TLV_0007_TGT

    :param token: PcToken 0088 From 0836 Protocol Package

    """
    writer = binary.Writer()

    writer.write(token)

    return _tlv("00 07", writer.clear())


def tlv00c(server_ip: bytes) -> bytes:
    """
    TLV_000C_PingRedirect

    :param server_ip: QQ Server IP Address

    """
    writer = binary.Writer()

    writer.write_hex("00 02 00 01 00 00 00 00 00 00 00 00")
    writer.write(server_ip)
    writer.write_hex("00 50 00 00 00 00")

    return _tlv("00 0C", writer.clear())


def tlv01f() -> bytes:
    """
    TLV_001F_DeviceID

    """
    writer = binary.Writer()

    writer.write_hex("00 01")
    writer.write(utils.randbytes(32))

    return _tlv("00 1F", writer.clear())


def tlv105() -> bytes:
    """
    TLV_0105_m_vec0x12c

    """
    writer = binary.Writer()

    writer.write_hex("00 01 01 02 00 14 01 01 00 10")
    writer.write(utils.randbytes(16))
    writer.write_hex("00 14 01 02 00 10")
    writer.write(utils.randbytes(16))

    return _tlv("01 05", writer.clear())


def tlv10b() -> bytes:
    """
    TLV_010B_QDLoginFlag

    """
    writer = binary.Writer()

    writer.write_hex("00 02")
    writer.write(utils.randbytes(17))
    writer.write_hex("10 00 00 00 00 00 00 00")
    writer.write_hex("02 00 63 3E 00 63 02 04 00 03 07 00 04 00 49 F5 00 00 00 00 78 8A 33 DD 00 76 A1 78 EB 8E 5B BB FF 17 D0 10")
    writer.write_hex("01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
    writer.write_hex("01 00 00 00")
    writer.write_hex("01 00 00 00")
    writer.write_hex("01 00 00 00")
    writer.write_hex("01 00 FE 26 81 75 EC 2A 34 EF")
    writer.write_hex("02 3E 50 39 6D B1 AF CC 9F EA 54 E1 70 CC 6C 9E 4E 63 8B 51 EC 7C 84 5C 68 00 00 00 00")

    return _tlv("01 0B", writer.clear())


def tlv02d() -> bytes:
    """
    TLV_002D_LocalIP

    """
    writer = binary.Writer()

    writer.write_hex("00 01")
    writer.write_hex("C0 A8 74 83")

    return _tlv("00 2D", writer.clear())
