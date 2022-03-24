import os
import asyncio

import pcqq.handle as hd
import pcqq.client as cli
import pcqq.const as const
import pcqq.network as net
import pcqq.session as ses
import pcqq.logger as logger
# cli = cli.QQClient()


async def exec_rules(rules, session):
    # 判断是否执行插件
    for rule in rules:
        if not await rule(session):
            return False
    return True


async def plugin_handle(body):
    session = ses.Session()
    typ = body[18:20].hex().upper()
    if typ == const.EVENT_GROUP_MSG:
        await hd.group_msg_handle(session, body)
    elif typ == const.EVENT_FRIEND_MSG:
        await hd.friend_msg_handle(session, body)
    elif typ == const.EVENT_GROUP_INCREASE:
        await hd.group_increase_handle(session, body)
    elif typ == const.EVENT_GROUP_DECREASE:
        await hd.group_decrease_handle(session, body)
    elif typ == const.EVENT_OTHRE:
        await hd.other_handle(session, body)
    else:
        return

    if session.user_id == session.self_id and session.event_type == "group_msg":
        return  # 忽略自身群消息

    for plugin in cli.plugins:

        # 判断是否位临时插件
        if plugin.temp:
            del cli.plugins[cli.plugins.index(plugin)]

        # 判断是否执行插件
        if await exec_rules(plugin.rules, session):
            try:
                await plugin.handle(session)
            except Exception as err:
                logger.error(f"插件 {plugin.handle.__name__} 运行时发生异常 -> {err}")

        # 判断是否阻断后续插件执行
        if plugin.block:
            break

async def event_handle(cmd:str, sequence:bytes, body:bytes):
    await cli.write_packet(
        cmd,
        const.BODY_VERSION,
        body[0:16],
        sequence=sequence
    )   # 初步进行回执

    if cmd == "03 52":
        """私聊图片上传响应"""
        callback = cli.waiter.pop(sequence.hex())
        await callback(body)
    elif cmd == "03 88":
        """群聊图片上传响应"""
        callback = cli.waiter.pop(sequence.hex())
        await callback(body)
    else:
        await plugin_handle(body)

async def main_handle():
    while True:
        try:
            cmd, sequence, _, body = await cli.read_packet()
        except:
            continue
        cli.run_future(event_handle(cmd, sequence, body))

async def keep_heatbeat():
    while True:
        cli.run_future(net.heatbeat())
        await asyncio.sleep(40.0)


def only_login(uin: int = 0, password: str = ""):
    """
    仅登录, 不处理事件

    :param uin: 用于登录的QQ号(留空则使用扫码登录)

    :param password: 登录QQ号的密码(留空则使用扫码登录)

    """
    cli.run(cli.client.init())

    if os.path.exists("session.token"):
        cli.run(net.token_login())
    elif uin and password:
        cli.run(net.password_login(uin, password))
    else:
        cli.run(net.qrcode_login())


def run_bot(uin: int = 0, password: str = ""):
    """
    登录机器人,并开始处理事件

    :param uin: 用于登录的QQ号(留空则使用扫码登录)

    :param password: 登录QQ号的密码(留空则使用扫码登录)

    """
    only_login(uin, password)
    cli.run_future(keep_heatbeat())

    cli.run_future(main_handle())
    logger.info(f"已导入 {len(cli.plugins)} 组插件，开始处理事件.....")
    cli.client.loop.run_forever()
