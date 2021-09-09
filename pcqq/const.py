import pcqq.utils as utils

Header = utils.Hex2Bin("02 38 23")  # QQ协议包标准头
Tail = utils.Hex2Bin("03")  # QQ协议包标准尾
EdchVersion = utils.Hex2Bin("01 03") # QQ协议包Edch版本
BodyVersion = utils.Hex2Bin("02 00 00 00 01 01 01 00 00 69 20") # QQ协议包包体版本
StructVersion = utils.Hex2Bin("03 00 00 00 01 01 01 00 00 69 20 00 00 00 00")   # QQ协议包结构版本
FuncVersion = utils.Hex2Bin("04 00 00 00 01 01 01 00 00 69 20 00 00 00 00 00 00 00 00") # QQ协议包功能版本

PublicKey = utils.Hex2Bin("02 F0 3C 70 7B 85 60 78 04 0F 8F 26 3D 43 1F 66 5E F3 6C 5D C0 45 AD 61 A6")
PrivateKey = utils.Hex2Bin("00 00 00 19 00 F2 0C 34 57 44 FE 64 05 70 73 A8 44 95 3F 84 2B D6 43 05 30 F5 C1 94 FD")
ShareKey = utils.Hex2Bin("AA CD 59 5A 01 57 7A 70 E2 00 3E 32 90 60 FD 6E")

RandHead16 = utils.Hex2Bin("B6 9F 79 EC E5 77 47 A6 99 FA A8 3C 56 E5 E8 3E")   # 任意16位字节集