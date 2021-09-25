import pcqq.log as log

from typing import List
from re import T, findall
from . import Session, Rule, HandleFunc


class Plugin:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self):
        for rule in self.rules:
            if not rule(self.session):
                return

        self.handle()
        return True


def on_event(*rules: Rule, priority: int = 10, block: bool = False):
    '''
    : param rules: 事件匹配规则集

    : param priority: 插件优先级(数值越小级别越高)

    : param block: 当前插件处理成功后是否阻断后续插件执行
    '''
    def wrapper(func: HandleFunc):
        type(func.__name__, (Plugin, ), {
            'rules': rules,
            'handle': lambda self: func(self.session),
            'priority': priority,
            'block': block
        })
        log.Println(f'Succeeded to import "plugin.{func.__name__}"')

    return wrapper


def on_regex(pattern: str, *rules: Rule, **kwargs):
    '''
    : param pattern: 解析消息文本的正则表达式

    : param rules: 事件匹配规则集

    : param priority: 插件优先级(数值越小级别越高)

    : param block: 当前插件处理成功后是否阻断后续插件执行
    '''
    def regRule(session: Session) -> bool:
        session._matched_ = findall(pattern, session.event.MessageText)
        return bool(session._matched_)

    return on_event(*rules, regRule, **kwargs)


def on_full(keyword: str, *rules: Rule, aliases: List[str] = [], **kwargs):
    '''
    : param keyword: 判断消息文本的关键词

    : param rules: 事件匹配规则集

    : param aliases: 关键词的其它代替词语

    : param priority: 插件优先级(数值越小级别越高)

    : param block: 当前插件处理成功后是否阻断后续插件执行
    '''
    aliases.insert(0, keyword)

    def fullRule(session: Session) -> bool:
        for keyword in aliases:
            if session.event.MessageText == keyword:
                return True

    return on_event(*rules, fullRule, **kwargs)


def on_command(cmd: str, *rules: Rule, aliases: List[str] = [], **kwargs):
    '''
    : param cmd: 判断消息文本的命令词语

    : param rules: 事件匹配规则集

    : param aliases: 命令词语的其它代替词语

    : param priority: 插件优先级(数值越小级别越高)

    : param block: 当前插件处理成功后是否阻断后续插件执行
    '''
    aliases.insert(0, cmd)

    def cmdRule(session: Session) -> bool:
        for cmd in aliases:
            if session.event.MessageText.startswith(cmd):
                idx = session.event.MessageText.find(cmd) + len(cmd)
                session._matched_ = session.event.MessageText[idx:].strip()
                return True

    return on_event(*rules, cmdRule, **kwargs)


def isAdmin(session: Session) -> bool:
    '''判断发送者是否为机器人管理者'''
    return session.event.UserID in session._driver_.AdminList


def isAtMe(session: Session) -> bool:
    '''判断接收消息是否At机器人'''
    return '[PQ:at,qq=%d]' % (
        session.event.SelfID) in session.event.MessageText


def onlyGroup(session: Session) -> bool:
    '''判断接收消息是否为群聊消息'''
    return session.event.GroupID != 0


def onlyPrivate(session: Session) -> bool:
    '''判断接收消息是否为私聊消息'''
    return session.event.GroupID == 0


def checkUser(*userList: int) -> Rule:
    '''判断发送者是否在userList中'''
    def check(session: Session) -> bool:
        return session.event.UserID in userList

    return check


def checkType(*types: str) -> Rule:
    '''判断事件类型是否在types中'''
    def check(session: Session) -> bool:
        return session.event.EventType in types

    return check
