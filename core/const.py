__bytes = bytes.fromhex

Header = "02 3B 41"
Tail = "03"

StructVersion = __bytes("03 00 00 00 01 01 01 00 00 6A 9C 00 00 00 00")
BodyVersion = __bytes("02 00 00 00 01 01 01 00 00 6A 9C")
FuncVersion = __bytes("04 00 00 00 01 01 01 00 00 6A 9C 00 00 00 00 00 00 00 00")
VMainVer = __bytes("3B 41")

EcdhVersion = __bytes("01 03")
DWQDVersion = __bytes("04 04 04 00")
SsoVersion = __bytes("00 00 04 61")
ClientVersion = __bytes("00 00 17 41")

RandKey = __bytes("66 D0 9F 63 A2 37 02 27 13 17 3B 1E 01 1C A9 DA")
ServiceId = __bytes("00 00 00 01")
DeviceID = __bytes("EE D2 37 A4 94 D3 7A 04 7D 98 18 E8 EE DF B0 D6 96 B3 A3 1C BB 4F 95 6A 3E 6C EE F5 02 C5 5A 1F")

TCP_PORT = 443
UDP_PORT = 8000
HeartBeatInterval = 30.0

StateOnline = 10   # 上线
StateLeave = 30    # 离开
StateInvisible = 40    # 隐身
StateBusy = 50  # 忙碌
StateCallMe = 60   # Q我吧
StateUndisturb = 70    # 请勿打扰