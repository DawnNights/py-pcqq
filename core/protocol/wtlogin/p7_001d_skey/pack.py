from core import const
from core.entities import Packet, QQStruct


def pack_001d(stru: QQStruct):
    packet = Packet(
        cmd="00 1D",
        uin=stru.uin,
        tea_key=stru.session_key
    )
    packet.version.write(const.BodyVersion)
    
    packet.body.write_byte(51)
    packet.body.write_int16(6)   # 域名数量
    packet.body.write_token(b't.qq.com')
    packet.body.write_token(b'qun.qq.com')
    packet.body.write_token(b'qzone.qq.com')
    packet.body.write_token(b'jubao.qq.com')
    packet.body.write_token(b'ke.qq.com')
    packet.body.write_token(b'tenpay.com')

    return packet