import os
import time
import asyncio

import pcqq.client as cli
import pcqq.utils as utils
import pcqq.const as const
import pcqq.network as net
import pcqq.logger as logger
import pcqq.binary as binary
import pcqq.plugin as plugin
import pcqq.handle as handle


def unpack(recv_data: bytes) -> tuple:
    reader = binary.Reader(recv_data)
    reader.read(3)  # packet header
    cmd = reader.read_hex(2)

    sequence = reader.read(2)
    reader.read(4)  # qq uin
    reader.read(3)  # unknow
    body = net.tea.decrypt(reader.read()[:-1])

    return cmd, sequence, body


async def session_handler(session: plugin.Session):
    if session.user_id in net.waiter:
        ret = net.waiter.pop(session.user_id)[0]
        ret.send(session.message)
    else:
        for demo in plugin.PluginPool:
            state = await demo(session).start_handle()
            if state and demo.block:
                return  # 截断后续执行


async def main_handle(recv_data: bytes):
    cmd, sequence, body = unpack(recv_data)

    net.send_packet(
        cmd,
        const.BODY_VERSION,
        body[0:16],
        sequence=sequence
    )   # 初步进行回执

    session = plugin.Session()

    sign = body[18:20].hex()
    if sign in const.EVENT_GROUP_MSG:
        handle.group_msg_handle(session, body)
    elif sign == const.EVENT_FRIEND_MSG:
        handle.friend_msg_handle(session, body)
    elif sign == const.EVENT_GROUP_INCREASE:
        handle.group_increase_handle(session, body)
    elif sign == const.EVENT_GROUP_DECREASE:
        handle.group_reduce_handle(session, body)
    elif sign == const.EVENT_SHUTUP_ANONYMOUS:
        handle.other_handle(session, body)
    else:
        return

    await session_handler(session)


def login_for_test(uin: int = 0, password: str = ""):
    """
    仅登录，不处理事件

    :param uin: 用于登录的QQ号(留空则使用扫码登录)

    :param uin: 登录QQ号的密码(留空则使用扫码登录)

    """
    cli.say_hello(False)

    if os.path.exists("session.token"):  # 本地token登录
        try:
            net.load_token()
            cli.say_hello(False)
            cli.open_session()
        except:
            os.remove("session.token")
            logger.fatal("ERROR: 本地Token已失效，请重新登录")

    elif uin and password:     # 账号密码登录
        net.uin = uin
        net.password = utils.hashmd5(password.encode())

        cli.login_validate()
        cli.open_session()
        net.save_token()
    else:   # 扫码登录
        net.is_scancode = True
        cli.apply_qrcode()
        while True:
            if cli.check_scan_state():
                break
            time.sleep(1.0)

        cli.login_validate()
        cli.open_session()
        net.save_token()

    cli.set_online(const.STATE_ONLINE)   # 置状态为上线
    cli.refresh_skey()   # 刷新skey


def run_bot(uin: int = 0, password: str = ""):
    """
    登录并处理事件

    :param uin: 用于登录的QQ号(留空则使用扫码登录)

    :param uin: 登录QQ号的密码(留空则使用扫码登录)

    """
    login_for_test(uin, password)
    net.run_thread(cli.keep_heatbeat)   # 开启心跳线程

    loop = asyncio.get_event_loop()
    net.run_thread(net.cli.listen, loop, main_handle)
    loop.run_forever()
