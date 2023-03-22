from typing import Coroutine, Callable
from logger import logger

from core.protocol import webapi
from core.client import QQClient
from core.entities import (
    Packet,
    PacketHandler,
    MessageEvent,
    Message,
)

from .msg_receipt import pack_0002_receipt

def handle_group_msg(cli: QQClient, func: Callable[[Message], Coroutine]):
    def check_0017(packet: Packet):
        if packet.cmd != "00 17":
            return False
        
        return packet.body._raw[18:20] == bytes.fromhex("00 52")

    async def handle_0017(packet: Packet):
        event = MessageEvent(
            message_type="group",
            sub_type="normal"
        )

        body = packet.body
        guid = body.read_int32()
        event.self_id = body.read_int32()

        body.del_left(12)
        body.read(body.read_int32())

        event.group_id = body.read_int32()
        event.user_id = body.del_left(1).read_int32()

        event.message_id = body.read_int32()
        event.time = body.read_int32()

        body.del_left(8)
        body.del_left(1).del_left(1).del_left(2)
        body.del_left(12)

        send_time = body.read_int32()
        event.message_num = body.read_int32()

        body.del_left(8).read_token()
        body.del_left(2)
        event.raw_message = body._raw

        event.message = Message.from_raw(body.read_all())
        
        group = await webapi.get_group(cli, event.group_id)
        member = group.members[str(event.user_id)]
        cli.send(pack_0002_receipt(cli, event))
        
        logger.info(f"收到群聊 {group.name}({event.group_id})内 {member.card}({event.user_id})消息: {event.message.format()}")
        cli.add_task(func(event))

    return PacketHandler(
        temp=False,
        check=check_0017,
        handle=handle_0017
    )
