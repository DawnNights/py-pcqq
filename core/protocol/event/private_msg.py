from typing import Coroutine, Callable
from logger import logger

from core.protocol import webapi
from core.client import QQClient
from core.entities import (
    Packet,
    PacketHandler,
    MessageEvent,
    Message
)

from .msg_receipt import pack_0319_receipt


def handle_private_msg(cli: QQClient, func: Callable[[Message], Coroutine]):
    def check_00ce(packet: Packet):
        if packet.cmd != "00 CE":
            return False

        return packet.body._raw[18:20] == bytes.fromhex("00 A6")

    async def handle_00ce(packet: Packet):
        event = MessageEvent(
            message_type="private",
            sub_type="normal"
        )

        body = packet.body
        event.user_id = body.read_int32()
        event.self_id = body.read_int32()

        body.del_left(12)
        body.del_left(body.read_int32() + 26)

        if body.read_hex(2) == "00 AF":
            pass  # 好友抖动

        event.message_id = body.read_int16()
        event.time = body.read_int32()

        body.del_left(6).del_left(1).del_left(1)
        body.del_left(2).del_left(9)

        send_time = body.read_int32()
        event.message_num = body.read_int32()

        body.del_left(8).read_token()
        body.read_int16()

        event.message = Message.from_raw(body.read_all())
        user = await webapi.get_user(cli, event.user_id)

        cli.send(pack_0319_receipt(cli, event))

        logger.info(
            f"收到私聊 {user.name}({event.user_id}) 消息: {event.message.format()}")
        cli.add_task(func(event))

    return PacketHandler(
        temp=False,
        check=check_00ce,
        handle=handle_00ce
    )
