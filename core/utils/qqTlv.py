from .qqTea import Tea
from .util import GetRandomBin
from .packEncrypt import PackEncrypt


class Tlv():
    def TlvPack(self,TlvCmd: str, TlvBin: bytes) -> bytes:
        pack = PackEncrypt()
        pack.Empty()
        pack.SetHex(TlvCmd)
        pack.SetShort(len(TlvBin))
        pack.SetBin(TlvBin)
        data = pack.GetAll()
        return data

    def Tlv112(self,Token0038From0825: bytes) -> bytes:
        pack = PackEncrypt()
        pack.Empty()
        pack.SetBin(Token0038From0825)
        return self.TlvPack("01 12", pack.GetAll())

    def Tlv30F(self,PcName: str) -> bytes:
        pack = PackEncrypt()
        pack.Empty()
        pack.SetShort(len(PcName))
        pack.SetStr(PcName)
        return self.TlvPack("03 0F", pack.GetAll())

    def Tlv005(self,BinQQ: bytes) -> bytes:
        pack = PackEncrypt()
        pack.Empty()
        pack.SetHex("00 02")
        pack.SetBin(BinQQ)
        return self.TlvPack("00 05", pack.GetAll())

    def Tlv303(self,PcToken0060From0819: bytes) -> bytes:
        pack = PackEncrypt()
        pack.Empty()
        pack.SetBin(PcToken0060From0819)
        return self.TlvPack("03 03", pack.GetAll())

    def Tlv015(self) -> bytes:
        pack = PackEncrypt()
        pack.Empty()
        pack.SetHex("00 01 01 74 83 F2 C3 00 10 14 FE 77 FC 00 00 00 00 00 00 00 00 00 00 00 00 02 17 65 6E 9D 00 10 78 8A 33 DD 00 76 A1 78 EB 8E 5B BB FF 17 D0 10")
        return self.TlvPack("00 15", pack.GetAll())

    def Tlv01A(self,Tgtkey: bytes) -> bytes:
        tea = Tea()
        pack = PackEncrypt()
        pack.Empty()
        pack.SetHex("00 01 01 74 83 F2 C3 00 10 14 FE 77 FC 00 00 00 00 00 00 00 00 00 00 00 00 02 17 65 6E 9D 00 10 78 8A 33 DD 00 76 A1 78 EB 8E 5B BB FF 17 D0 10")
        return self.TlvPack("00 1A", tea.Encrypt(pack.GetAll(),Tgtkey))

    def Tlv018(self,BinQQ: bytes) -> bytes:
        pack = PackEncrypt()
        pack.Empty()
        pack.SetHex("00 01 00 00 04 4C 00 00 00 01 00 00 15 51")
        pack.SetBin(BinQQ)
        pack.SetHex("00 00 00 00")
        return self.TlvPack("00 18", pack.GetAll())

    def Tlv103(self) -> bytes:
        pack = PackEncrypt()
        pack.Empty()
        pack.SetHex("00 01 00 10")
        pack.SetBin(GetRandomBin(16))
        return self.TlvPack("01 03", pack.GetAll())

    def Tlv312(self) -> bytes:
        pack = PackEncrypt()
        pack.Empty()
        pack.SetHex("01 00 00 00 00")
        return (self.TlvPack("03 12", pack.GetAll()))

    def Tlv313(self) -> bytes:
        pack = PackEncrypt()
        pack.Empty()
        pack.SetHex("01 01 02 00 10 EE 47 7F A4 BC D6 EE 65 02 65 4D E9 43 38 4C 3D 00 00 00 EB")
        return self.TlvPack("03 13", pack.GetAll())

    def Tlv102(self,Token0038From0825: bytes) -> bytes:
        pack = PackEncrypt()
        pack.Empty()
        pack.SetHex("00 01")
        pack.SetBin(GetRandomBin(16))
        pack.SetShort(len(Token0038From0825))
        pack.SetBin(Token0038From0825)
        pack.SetHex("00 14")
        pack.SetBin(GetRandomBin(20))
        return self.TlvPack("01 02", pack.GetAll())

    def Tlv007(self,PcToken0088From0836: bytes) -> bytes:
        pack = PackEncrypt()
        pack.Empty()
        pack.SetBin(PcToken0088From0836)
        return self.TlvPack("00 07", pack.GetAll())

    def Tlv00C(self,ServerIp: bytes) -> bytes:
        pack = PackEncrypt()
        pack.Empty()
        pack.SetHex("00 02 00 01 00 00 00 00 00 00 00 00")
        pack.SetBin(ServerIp)
        pack.SetHex("00 50 00 00 00 00")
        return self.TlvPack("00 0C", pack.GetAll())

    def Tlv036(self) -> bytes:
        pack = PackEncrypt()
        pack.Empty()
        pack.SetHex("00 02 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
        return self.TlvPack("00 36", pack.GetAll())

    def Tlv01F(self) -> bytes:
        pack = PackEncrypt()
        pack.Empty()
        pack.SetHex("00 01")
        pack.SetBin(GetRandomBin(32))
        return self.TlvPack("00 1F", pack.GetAll())

    def Tlv105(self) -> bytes:
        pack = PackEncrypt()
        pack.Empty()
        pack.SetHex("00 01 01 02 00 14 01 01 00 10")
        pack.SetBin(GetRandomBin(16))
        pack.SetHex("00 14 01 02 00 10")
        pack.SetBin(GetRandomBin(16))
        return self.TlvPack("01 05", pack.GetAll())

    def Tlv10B(self) -> bytes:
        pack = PackEncrypt()
        pack.Empty()
        pack.SetHex("00 02")
        pack.SetBin(GetRandomBin(17))
        pack.SetHex("10 00 00 00 00 00 00 00 02 00 63 3E 00 63 02 04 00 03 07 00 04 00 49 F5 00 00 00 00 78 8A 33 DD 00 76 A1 78 EB 8E 5B BB FF 17 D0 10 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 00 01 00 FE 26 81 75 EC 2A 34 EF 02 3E 50 39 6D B1 AF CC 9F EA 54 E1 70 CC 6C 9E 4E 63 8B 51 EC 7C 84 5C 68 00 00 00 00")
        return self.TlvPack("01 0B", pack.GetAll())

    def Tlv02D(self) -> bytes:
        pack = PackEncrypt()
        pack.Empty()
        pack.SetHex("00 01")
        pack.SetHex("C0 A8 74 83")
        return self.TlvPack("00 2D", pack.GetAll())
