from ._writer import Writer as _Writer
from ._qqtea import TeaEncrypt as _TeaEncrypt
from random import randint as _randint

def _GetRandomBin(length: int)->bytes:
    '''生成指定长度的随机字节集'''
    dst = [_randint(0,255).to_bytes(1,"big") for _ in range(length)]
    return b''.join(dst)

def _TlvPack(TlvCmd: str, TlvBin: bytes) -> bytes:
    writer = _Writer()

    writer.WriteHex(TlvCmd)
    writer.WriteShort(len(TlvBin))
    writer.WriteBytes(TlvBin)

    return writer.ReadAll()

def TLV_0112_SigIP2(Token0038From0825: bytes) -> bytes:
    writer = _Writer()
    writer.WriteBytes(Token0038From0825)
    return _TlvPack("01 12", writer.ReadAll())

def TLV_030F_ComputerName(PcName: str) -> bytes:
    writer = _Writer()
    
    writer.WriteShort(len(PcName))
    writer.WriteBytes(PcName.encode())

    return _TlvPack("03 0F", writer.ReadAll())

def TLV_0005_Uin(BinQQ: bytes) -> bytes:
    writer = _Writer()
    writer.WriteHex("00 02")
    writer.WriteBytes(BinQQ)
    return _TlvPack("00 05", writer.ReadAll())

def TLV_0303_UnknownTag(PcToken0060From0819: bytes) -> bytes:
    writer = _Writer()
    writer.WriteBytes(PcToken0060From0819)
    return _TlvPack("03 03", writer.ReadAll())

def TLV_0015_ComputerGuid() -> bytes:
    writer = _Writer()
    writer.WriteHex("00 01 01 74 83 F2 C3 00 10 14 FE 77 FC 00 00 00 00 00 00 00 00 00 00 00 00 02 17 65 6E 9D 00 10 78 8A 33 DD 00 76 A1 78 EB 8E 5B BB FF 17 D0 10")
    return _TlvPack("00 15", writer.ReadAll())

def TLV_001A_GTKeyTGTGTCryptedData(Tgtkey: bytes) -> bytes:
    writer = _Writer()
    writer.WriteHex("00 01 01 74 83 F2 C3 00 10 14 FE 77 FC 00 00 00 00 00 00 00 00 00 00 00 00 02 17 65 6E 9D 00 10 78 8A 33 DD 00 76 A1 78 EB 8E 5B BB FF 17 D0 10")
    return _TlvPack("00 1A", _TeaEncrypt(writer.ReadAll(),Tgtkey))

def TLV_0018_Ping(BinQQ: bytes, RedirectTimes: int) -> bytes:
    writer = _Writer()
    writer.WriteHex("00 01 00 00 04 4C 00 00 00 01 00 00 15 51")
    writer.WriteBytes(BinQQ)
    writer.WriteBytes(RedirectTimes.to_bytes(2,"big"))
    writer.WriteHex("00 00")
    return _TlvPack("00 18", writer.ReadAll())

def TLV_0019_Ping()->bytes:
    writer = _Writer()
    writer.WriteHex("00 01")
    writer.WriteHex("00 00 04 56")  # sso版本号
    writer.WriteHex("00 00 00 01")  # ServiceId
    writer.WriteHex("00 00 16 03")  # 客户端版本
    writer.WriteHex("00 00")
    return _TlvPack("00 19", writer.ReadAll())

def TLV_0114_DHParams()->bytes:
    writer = _Writer()
    writer.WriteHex("01 03")    # QQ协议包Edch版本
    writer.WriteHex("00 19")
    writer.WriteHex("02 F0 3C 70 7B 85 60 78 04 0F 8F 26 3D 43 1F 66 5E F3 6C 5D C0 45 AD 61 A6")   # PublicKey
    return _TlvPack("01 14", writer.ReadAll())

def TLV_0103_SID() -> bytes:
    writer = _Writer()
    writer.WriteHex("00 01 00 10")
    writer.WriteBytes(_GetRandomBin(16))
    return _TlvPack("01 03", writer.ReadAll())

def TLV_0312_Misc_Flag() -> bytes:
    writer = _Writer()
    writer.WriteHex("01 00 00 00 00")
    return _TlvPack("03 12", writer.ReadAll())

def TLV_0508_UnknownTag() -> bytes:
    writer = _Writer()
    writer.WriteHex("01 00 00 00 02")
    return _TlvPack("05 08", writer.ReadAll())

def TLV_0313_GUID_Ex() -> bytes:
    writer = _Writer()
    writer.WriteHex("01 01 02 00 10 EE 47 7F A4 BC D6 EE 65 02 65 4D E9 43 38 4C 3D 00 00 00 EB")
    return _TlvPack("03 13", writer.ReadAll())

def TLV_0102_Official(Token0038From0825: bytes) -> bytes:
    writer = _Writer()
    writer.WriteHex("00 01")
    writer.WriteBytes(_GetRandomBin(16))
    writer.WriteShort(len(Token0038From0825))
    writer.WriteBytes(Token0038From0825)
    writer.WriteHex("00 14")
    writer.WriteBytes(_GetRandomBin(20))
    return _TlvPack("01 02", writer.ReadAll())

def TLV_0309_Ping_Strategy(ServerIp:bytes, RedirectionHistory:str, RedirectionTimes:int)->bytes:
    writer = _Writer()
    writer.WriteHex("00 01")
    writer.WriteBytes(ServerIp)

    if RedirectionTimes > 0:
        writer.WriteHex(hex(RedirectionTimes)[2:])
        writer.WriteHex(RedirectionHistory)
    else:
        writer.WriteHex("00")

    writer.WriteHex("02")
    return _TlvPack("03 09", writer.ReadAll())

def TLV_0036_LoginReason()->bytes:
    writer = _Writer()
    writer.WriteHex("00 02 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
    return _TlvPack("00 36", writer.ReadAll())

def TLV_0007_TGT(PcToken0088From0836: bytes) -> bytes:
    writer = _Writer()
    writer.WriteBytes(PcToken0088From0836)
    return _TlvPack("00 07", writer.ReadAll())

def TLV_000C_PingRedirect(ServerIp: bytes) -> bytes:
    writer = _Writer()
    writer.WriteHex("00 02 00 01 00 00 00 00 00 00 00 00")
    writer.WriteBytes(ServerIp)
    writer.WriteHex("00 50 00 00 00 00")
    return _TlvPack("00 0C", writer.ReadAll())

def TLV_001F_DeviceID() -> bytes:
    writer = _Writer()
    writer.WriteHex("00 01")
    writer.WriteBytes(_GetRandomBin(32))
    return _TlvPack("00 1F", writer.ReadAll())

def TLV_0105_m_vec0x12c() -> bytes:
    writer = _Writer()
    writer.WriteHex("00 01 01 02 00 14 01 01 00 10")
    writer.WriteBytes(_GetRandomBin(16))
    writer.WriteHex("00 14 01 02 00 10")
    writer.WriteBytes(_GetRandomBin(16))
    return _TlvPack("01 05", writer.ReadAll())

def TLV_010B_QDLoginFlag() -> bytes:
    writer = _Writer()
    writer.WriteHex("00 02")
    writer.WriteBytes(_GetRandomBin(17))
    writer.WriteHex("10 00 00 00 00 00 00 00 02 00 63 3E 00 63 02 04 00 03 07 00 04 00 49 F5 00 00 00 00 78 8A 33 DD 00 76 A1 78 EB 8E 5B BB FF 17 D0 10 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 00 01 00 FE 26 81 75 EC 2A 34 EF 02 3E 50 39 6D B1 AF CC 9F EA 54 E1 70 CC 6C 9E 4E 63 8B 51 EC 7C 84 5C 68 00 00 00 00")
    return _TlvPack("01 0B", writer.ReadAll())

def TLV_002D_LocalIP() -> bytes:
    writer = _Writer()
    writer.WriteHex("00 01")
    writer.WriteHex("C0 A8 74 83")
    return _TlvPack("00 2D", writer.ReadAll())