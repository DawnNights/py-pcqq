from time import time

from core import const, utils, croto
from core.client import QQClient
from core.entities import Packet, Message

def send_group_msg(cli: QQClient, group_id:int, message: Message):
    packet = Packet(
        cmd="00 02",
        uin=cli.stru.uin,
        tea_key=cli.stru.session_key
    )
    packet.version.write(const.BodyVersion)
    
    body = message.encode()
    timestamp = int(time()).to_bytes(4, 'big')
    
    packet.body.write_hex("00 01 01 00 00 00 00 00 00 00")
    packet.body.write_hex("4D 53 47 00 00 00 00 00")
    
    packet.body.write(timestamp)
    packet.body.write(utils.rand_bytes(4))
    
    packet.body.write_hex("00 00 00 00 09 00 86 00 00")
    packet.body.write_hex("06 E5 AE 8B E4 BD 93 00 00")
    packet.body.write(body)
    body = packet.body.read_all()

    packet.body.write_hex("2A")
    packet.body.write_int32(croto.gid_from_group(group_id))
    packet.body.write_int16(len(body))
    packet.body.write(body)
    cli.send(packet)

def send_private_msg(cli: QQClient, user_id:int, message: Message):
    packet = Packet(
        cmd="00 CD",
        uin=cli.stru.uin,
        tea_key=cli.stru.session_key
    )
    packet.version.write_hex("03 00 00 00 01 01 01 00 00 6A 9C 75 37 7D 94")
    
    msg_data = message.encode()
    timestamp = int(time()).to_bytes(4, "big")

    packet.body.write_int32(cli.stru.uin)
    packet.body.write_int32(user_id)
    
    packet.body.write_hex("00 00 00 08 00 01 00 04 00 00 00 00")
    packet.body.write(const.VMainVer)
    
    packet.body.write_int32(cli.stru.uin)
    packet.body.write_int32(user_id)
    packet.body.write(croto.md5(user_id.to_bytes(4, "big") + cli.stru.session_key))
    
    packet.body.write_hex("00 0B")
    packet.body.write(utils.rand_bytes(2))
    packet.body.write(timestamp)
    
    packet.body.write_hex("00 00 00 00 00 00 01 00 00 00 01 4D 53 47 00 00 00 00 00")
    packet.body.write(timestamp)
    packet.body.write(utils.rand_bytes(4))
    packet.body.write_hex("00 00 00 00 09 00 86 00 00 0C E5 BE AE E8 BD AF E9 9B 85 E9 BB 91 00 00")
    packet.body.write(msg_data)
    cli.send(packet)