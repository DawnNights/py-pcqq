from core import const, croto
from core.client import QQClient
from core.entities import (
    Packet,
    PacketHandler,
    MessageEvent,
)


def pack_0002_receipt(cli: QQClient, event: MessageEvent):
    packet = Packet(
        cmd="00 02",
        uin=cli.stru.uin,
        tea_key=cli.stru.session_key
    )

    packet.version.write(const.BodyVersion)
    packet.body.write_byte(41)
    packet.body.write_int32(croto.gid_from_group(event.group_id))
    packet.body.write_byte(2)
    packet.body.write_int32(event.message_id)

    return packet


def pack_0319_receipt(cli: QQClient, event: MessageEvent):
    packet = Packet(
        cmd="03 19",
        uin=cli.stru.uin,
        tea_key=cli.stru.session_key
    )

    packet.version.write(const.FuncVersion)

    packet.body.write_hex("08 01")
    packet.body.write_hex("12 03 98 01 00")
    packet.body.write_hex("0A 0E 08")
    packet.body.write_varint(event.user_id)
    packet.body.write_hex("10")
    packet.body.write_varint(event.time)
    packet.body.write_hex("20 00")
    data = packet.body.read_all()

    packet.body.write_hex("00 00 00 07")
    packet.body.write_int32(len(data)-7)
    packet.body.write(data)

    return packet


def handle_msg_receipt(cli: QQClient):
    def check_0017_00ce(packet: Packet):
        return packet.cmd in ["00 17", "00 CE", "03 55"]

    async def handle_0017_00ce(packet: Packet):
        receipt_packet = Packet(
            cmd=packet.cmd,
            uin=cli.stru.uin,
            sequence=packet.sequence,
            tea_key=cli.stru.session_key
        )

        receipt_packet.version.write(const.BodyVersion)
        receipt_packet.body.write(packet.body._raw[0:16])
        cli.send(receipt_packet)

    return PacketHandler(
        temp=False,
        check=check_0017_00ce,
        handle=handle_0017_00ce
    )
