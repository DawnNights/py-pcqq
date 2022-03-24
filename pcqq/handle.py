import pcqq.network as net
import pcqq.utils as utils
import pcqq.const as const
import pcqq.logger as logger
import pcqq.binary as binary


async def msg_handle(session, reader: binary.Reader):
    reader.read(16)
    reader.read(reader.read_int16())
    reader.read_int16()

    session.raw_message.clear()
    while reader.tell() > 0:
        typ = reader.read_byte()
        msgread = binary.Reader(reader.read(reader.read_int16()))

        if typ == const.MSG_TEXT:
            msgread.read_byte()
            data = msgread.read(msgread.read_int16())

            if msgread.tell():
                msgread.read(10)
                uid = msgread.read_int32()
                session.message += f"[PQ:at,qq={uid}]"
                session.raw_message.append({
                    "type": "at",
                    "qq": uid
                })
            else:
                text = data.decode()
                session.message += text
                session.raw_message.append(text)

        elif typ == const.MSG_FACE:
            msgread.read(3)
            face_id = msgread.read_byte()
            session.message += f"[PQ:face,id={face_id}]"
            session.raw_message.append({
                "type": "face",
                "id": face_id
            })

        elif typ in (const.MSG_IMAGE_GROUP, const.MSG_IMAGE_FRIEND):
            msgread.read_byte()
            id = msgread.read(msgread.read_int16()).decode().upper()
            id = id[:-4].replace("-", "").replace("{", "").replace("}", "")
            session.message += f"[PQ:image,file={id}]"
            session.raw_message.append({
                "type": "image",
                "url": f"https://gchat.qpic.cn/gchatpic_new/0/0-0-{id}/0?term=3"
            })


async def group_msg_handle(session, body: bytes):
    reader = binary.Reader(body)
    session.event_type = "group_msg"

    reader.read(4)
    session.self_id = reader.read_int32()

    reader.read(12)
    reader.read(reader.read_int32())
    session.group_id = reader.read_int32()

    reader.read_byte()
    session.user_id = reader.read_int32()
    session.msg_id = reader.read_int32()
    session.timestamp = reader.read_int32()

    reader.read(8)
    reader.read(16)
    await msg_handle(session, reader)

    if session.user_id != session.self_id:
        logger.info(f"收到群聊 %s(%d) 消息 %s(%d): %s" % (
            await net.get_group_cache(session.group_id),
            session.group_id,
            await net.get_user_cache(session.user_id, session.group_id),
            session.user_id,
            session.message
        ))
    await net.group_receipt(session.group_id, session.msg_id)


async def friend_msg_handle(session, body: bytes):
    reader = binary.Reader(body)
    session.event_type = "friend_msg"

    session.user_id = reader.read_int32()
    session.self_id = reader.read_int32()

    reader.read(12)
    reader.read(reader.read_int32())
    reader.read(26 + 2)

    session.msg_id = reader.read_int16()
    session.timestamp = reader.read_int32()

    reader.read(6 + 4 + 9)
    await msg_handle(session, reader)

    logger.info(f"收到好友消息 %s(%d): %s" % (
        await net.get_user_cache(session.user_id),
        session.user_id, session.message
    ))
    await net.friend_receipt(session.user_id, session.timestamp)


async def group_increase_handle(session, body: bytes):
    reader = binary.Reader(body)
    session.event_type = "group_increase"

    session.group_id = utils.group_from_gid(reader.read_int32())
    session.self_id = reader.read_int32()

    reader.read(12)
    reader.read(reader.read_int32() + 5)
    session.target_id = reader.read_int32()
    sign = reader.read_byte()
    session.user_id = reader.read_int32()

    if sign == 0x03:
        logger.info("收到群 %s(%d) 事件: %s(%d) 邀请 %s(%d) 加入群聊" % (
            await net.get_group_cache(session.group_id), session.group_id,
            await net.get_user_cache(
                session.user_id,
                session.group_id
            ), session.user_id,
            await net.get_user_cache(session.target_id), session.target_id
        ))

    else:
        logger.info("收到群 %s(%d) 事件: %s(%d) 同意 %s(%d) 加入群聊" % (
            await net.get_group_cache(session.group_id), session.group_id,
            await net.get_user_cache(
                session.user_id,
                session.group_id
            ), session.user_id,

            await net.get_user_cache(session.target_id), session.target_id
        ))


async def group_decrease_handle(session, body: bytes):
    reader = binary.Reader(body)
    session.event_type = "group_decrease"

    session.group_id = utils.group_from_gid(reader.read_int32())
    session.self_id = reader.read_int32()

    reader.read(12)
    reader.read(reader.read_int32() + 5)
    session.target_id = reader.read_int32()
    sign = reader.read_byte()
    session.user_id = reader.read_int32()

    if sign == 0x01:
        logger.info("收到群 %s(%d) 事件: 群主 %s(%d) 解散了该群" % (
            await net.get_group_cache(session.group_id), session.group_id,

            await net.get_user_cache(
                session.user_id,
                session.group_id
            ), session.user_id,
        ))
    elif sign == 0x02:
        logger.info("收到群 %s(%d) 事件: %s(%d) 退出了群聊" % (
            await net.get_group_cache(session.group_id), session.group_id,

            await net.get_user_cache(
                session.target_id,
                session.group_id
            ), session.target_id
        ))
    elif sign == 0x03:
        logger.info("收到群 %s(%d) 事件: %s(%d) 将 %s(%d) 踢出了群聊" % (
            await net.get_group_cache(session.group_id), session.group_id,

            await net.get_user_cache(
                session.user_id,
                session.group_id
            ), session.user_id,

            await net.get_user_cache(
                session.target_id,
                session.group_id
            ), session.target_id
        ))


async def shutup_handle(session, reader: binary.Reader):
    session.event_type = "group_shutup"

    reader.read(1)
    session.user_id = reader.read_int32()
    session.timestamp = reader.read_int32()

    reader.read(2)
    session.target_id = reader.read_int32()
    time = reader.read_int32()

    if session.target_id:
        if time:
            logger.info("收到群 %s(%d) 事件: %s(%d) 将 %s(%d) 禁言，预计 %s 禁言结束" % (
                await net.get_group_cache(session.group_id), session.group_id,

                await net.get_user_cache(
                    session.user_id,
                    session.group_id
                ), session.user_id,

                await net.get_user_cache(
                    session.target_id,
                    session.group_id
                ), session.target_id,

                utils.time_lapse(time)
            ))
        else:
            logger.info("收到群 %s(%d) 事件: %s(%d) 将 %s(%d) 解除禁言" % (
                await net.get_group_cache(session.group_id), session.group_id,

                await net.get_user_cache(
                    session.user_id,
                    session.group_id
                ), session.user_id,

                await net.get_user_cache(
                    session.target_id,
                    session.group_id
                ), session.target_id,
            ))
    else:
        if time:
            logger.info("收到群 %s(%d) 事件: %s(%d) 开启了全体禁言" % (
                await net.get_group_cache(session.group_id), session.group_id,

                await net.get_user_cache(
                    session.user_id,
                    session.group_id
                ), session.user_id,
            ))
        else:
            logger.info("收到群 %s(%d) 事件: %s(%d) 解除了全体禁言" % (
                await net.get_group_cache(session.group_id), session.group_id,

                await net.get_user_cache(
                    session.user_id,
                    session.group_id
                ), session.user_id,
            ))


async def anonymous_handle(session, reader: binary.Reader):
    session.event_type = "group_anonymous"
    pass


async def other_handle(session, body: bytes):
    reader = binary.Reader(body)
    session.group_id = utils.group_from_gid(reader.read_int32())
    session.self_id = reader.read_int32()

    reader.read(12)
    reader.read(reader.read_int32() + 4)
    sign = reader.read_byte()

    if sign == 0x0c:
        await shutup_handle(session, reader)
    elif sign == 0x0e:
        await anonymous_handle(session, reader)
