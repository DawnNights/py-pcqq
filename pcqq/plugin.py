import re

import pcqq.client as cli
import pcqq.network as net
import pcqq.logger as logger
import pcqq.message as message
from typing import List, Dict, Callable, Generator


class Session:
    msg_id: int = 0
    timestamp: int = 0

    self_id: int = 0
    user_id: int = 0
    group_id: int = 0
    target_id: int = 0

    matched: str = ""
    message: str = ""
    event_type: str = ""
    msg_group: List[Dict] = []

    def send_msg(self, msg: str, escape: bool = True):
        """
        根据事件来源自动回复

        :param msg: 发送的消息文本或PQ码

        :param escape: 是否解析消息中的PQ码

        """
        if self.group_id:
            self.send_group_msg(self.group_id, msg, escape)
        else:
            self.send_friend_msg(self.user_id, msg, escape)

    def send_friend_msg(self, user_id: int, msg: str, escape: bool = True):
        """
        发送好友消息

        :param user_id: 好友的账号

        :param msg: 发送的消息文本或PQ码

        :param escape: 是否解析消息中的PQ码

        """
        if escape:
            cli.send_friend_msg(user_id, pqcode_escape(msg, self))
        else:
            cli.send_friend_msg(user_id, message.text(msg))

        logger.info(f"发送好友消息: %s -> %s(%d)" % (
            msg, cli.get_user_name(user_id), user_id
        ))

    def send_group_msg(self, group_id: int, msg: str, escape: bool = True):
        """
        发送群消息

        :param group_id: 目标群号

        :param msg: 发送的消息文本或PQ码

        :param escape: 是否解析消息中的PQ码

        """
        if escape:
            cli.send_group_msg(group_id, pqcode_escape(
                msg, self), "[PQ:image" in msg)
        else:
            cli.send_group_msg(group_id, message.text(msg))

        logger.info(f"发送群消息: %s -> %s(%d)" % (
            msg, cli.get_group_name(group_id), group_id
        ))


def pqcode_escape(pqmsg: str, session: Session) -> bytes:
    ret = bytes()
    pqcodes = re.findall(r'\[PQ:\w+?.*?]', pqmsg)

    for code in pqcodes:
        idx = pqmsg.find(code)
        ret += message.text(pqmsg[0:idx])
        pqmsg = pqmsg[idx+len(code):]

        ret += message.pqcode(
            session=session,
            typ=code[4:code.find(",")].lower(),
            params=dict(re.findall(r',([\w\-.]+?)=([^,\]]+)', code))
        )

    return ret + message.text(pqmsg) if pqmsg else ret


class Plugin:
    def __init__(self, session: Session) -> None:
        self.session = session

    async def match(self):
        for rule in self.rules:
            ret = rule(self.session)
            uid = next(ret)

            if uid is False:
                return False
            elif uid is True:
                continue
            elif await net.waiter.wait(uid, ret):
                logger.error(f'等待[{uid}]会话输入 -> 超时......')
                return False
        return True

    async def start_handle(self) -> bool:
        if await self.match():
            self.handle()
            return True
        return False


PluginPool: List[Plugin] = []


def on(*rules: Callable[[Session], Generator], priority: int = 10, block: bool = False):
    """
    基础触发器

    : param rules: 事件匹配规则集

    : param priority: 插件优先级(数值越小级别越高)

    : param block: 当前插件处理成功后是否阻断后续插件执行
    """
    def wrapper(func: Callable[[Session], None]):
        name = func.__name__.title()
        PluginPool.append(type(name, (Plugin, ), {
            'block': block,
            'rules': rules,
            'priority': priority,
            'handle': lambda p: func(p.session)
        }))
        PluginPool.sort(key=lambda p: p.priority)

        logger.info(f'插件[{name}]已导入，当前共计{len(PluginPool)}组插件')
    return wrapper


def on_type(type: str, *rules: Callable[[Session], Generator], **kwargs):
    '''
    事件触发器

    : param keyword: 匹配关键词

    : param rules: 事件匹配规则集

    : param prompt: 发送prompt语句并等待传参

    : param priority: 插件优先级(数值越小级别越高)

    : param block: 当前插件处理成功后是否阻断后续插件执行

    匹配结果保留至session.matched

    '''
    def type_rule(session: Session):
        yield type == session.event_type
    return on(*rules, type_rule, **kwargs)

def on_full(keyword: str, *rules: Callable[[Session], Generator], **kwargs):
    '''
    完全匹配触发器

    : param keyword: 匹配关键词

    : param rules: 事件匹配规则集

    : param priority: 插件优先级(数值越小级别越高)

    : param block: 当前插件处理成功后是否阻断后续插件执行

    匹配结果保留至session.matched

    '''
    def full_rule(session: Session):
        yield keyword == session.message
    return on(*rules, full_rule, **kwargs)


def on_fulls(keywords: List[str], *rules: Callable[[Session], Generator],  **kwargs):
    '''
    完全匹配组触发器

    : param keywords: 匹配关键词组

    : param rules: 事件匹配规则集

    : param priority: 插件优先级(数值越小级别越高)

    : param block: 当前插件处理成功后是否阻断后续插件执行

    匹配结果保留至session.matched

    '''
    def fulls_rule(session: Session):
        yield session.message in keywords
    return on(*rules, fulls_rule, **kwargs)


def on_command(cmd: str, *rules: Callable[[Session], Generator], prompt: str = '',  **kwargs):
    '''
    命令匹配触发器

    : param cmd: 匹配命令

    : param rules: 事件匹配规则集

    : param prompt: 发送prompt语句并等待传参

    : param priority: 插件优先级(数值越小级别越高)

    : param block: 当前插件处理成功后是否阻断后续插件执行

    匹配结果保留至session.matched

    '''
    def cmd_rule(session: Session):
        if session.message.startswith(cmd):
            session.matched = session.message[len(cmd):].strip()

            if not session.matched and prompt:
                session.send_msg(f"[PQ:at,qq={session.user_id}]{prompt}")
                session.matched = yield session.user_id
            yield bool(session.matched)
        yield False
    return on(*rules, cmd_rule, **kwargs)


def on_commands(cmds: List[str], *rules: Callable[[Session], Generator], prompt: str = '',  **kwargs):
    '''
    命令组匹配触发器

    : param cmds: 匹配命令组

    : param rules: 事件匹配规则集

    : param prompt: 发送prompt语句并等待传参

    : param priority: 插件优先级(数值越小级别越高)

    : param block: 当前插件处理成功后是否阻断后续插件执行

    匹配结果保留至session.matched

    '''
    def cmds_rule(session: Session):
        for cmd in cmds:
            if session.message.startswith(cmd):
                session.matched = session.message[len(cmd):].strip()
                if not session.matched and prompt:
                    session.send_msg(f"[PQ:at,qq={session.user_id}]{prompt}")
                    session.matched = yield session.user_id
                yield bool(session.matched)
        yield False
    return on(*rules, cmds_rule, **kwargs)


def on_regex(pattern: str, *rules: Callable[[Session], Generator],  **kwargs):
    '''
    正则匹配触发器

    : param pattern: 正则语句

    : param rules: 事件匹配规则集

    : param priority: 插件优先级(数值越小级别越高)

    : param block: 当前插件处理成功后是否阻断后续插件执行

    匹配结果以list的形式保留至session.matched

    '''
    def reg_rule(session: Session):
        session.matched = re.findall(pattern, session.message)
        yield bool(session.matched)

    return on(*rules, reg_rule, **kwargs)
