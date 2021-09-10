import pcqq.utils as utils

Header = utils.Hex2Bin("02 36 39")  # QQ协议包标准头
Tail = utils.Hex2Bin("03")  # QQ协议包标准尾

EdchVersion = utils.Hex2Bin("01 03") # QQ协议包Edch版本
BodyVersion = utils.Hex2Bin("02 00 00 00 01 01 01 00 00 67 B7") # QQ协议包包体版本
StructVersion = utils.Hex2Bin("03 00 00 00 01 01 01 00 00 67 B7 00 00 00 00")   # QQ协议包结构版本
FuncVersion = utils.Hex2Bin("04 00 00 00 01 01 01 00 00 6A 0F 00 00 00 00 00 00 00 00") # QQ协议包功能版本

PublicKey = utils.Hex2Bin("03 94 3D CB E9 12 38 61 EC F7 AD BD E3 36 91 91 07 01 50 BE 50 39 1C D3 32")
ShareKey = utils.Hex2Bin("FD 0B 79 78 31 E6 88 54 FC FA EA 84 52 9C 7D 0B")

RandHead16 = utils.Hex2Bin("B6 9F 79 EC E5 77 47 A6 99 FA A8 3C 56 E5 E8 3E")   # 任意16位字节集