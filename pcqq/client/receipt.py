import pcqq.network as net
import pcqq.utils as utils
import pcqq.const as const
import pcqq.binary as binary


def user_receipt(user_id: int, timestamp: int):
    writer = binary.Writer()
    writer.write_hex("08 01")
    writer.write_hex("12 03 98 01 00")
    writer.write_hex("0A 0E 08")
    writer.write_varint(user_id)
    writer.write_hex("10")
    writer.write_varint(timestamp)
    writer.write_hex("20 00")
    data = writer.clear()

    writer.__init__()
    writer.write_hex("00 00 00 07")
    writer.write_int32(len(data)-7)
    writer.write(data)

    net.send_packet(
        "03 19",
        const.FUNC_VERSION,
        writer.clear()
    )


def group_receipt(group_id: int, msg_id: int):
    writer = binary.Writer()

    writer.write_byte(41)
    writer.write_int32(utils.gid_from_group(group_id))
    writer.write_byte(2)
    writer.write_int32(msg_id)

    net.send_packet(
        "00 02",
        const.BODY_VERSION,
        writer.clear()
    )

