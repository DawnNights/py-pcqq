import nonebot
from .session import Session
from typing import Any, Tuple, Callable, Iterable, Coroutine


class BasePlugin:
    temp: bool
    block: bool
    priority: int

    session: Session
    rules: Tuple[Callable[[Session], Coroutine[Any, Any, bool]]]
    handle: Callable[[Session], Coroutine[Any, Any, None]]

    def __init__(self,
                 rules: Tuple[Callable[[Session], Coroutine[Any, Any, bool]]]
                 ) -> None: ...

    def __call__(self,
                 handle: Callable[[Session], Coroutine[Any, Any, None]]
                 ) -> BasePlugin: ...

    def SetTemp(self, temp: bool) -> BasePlugin:
        """
        设置当前插件是否为临时插件

        临时插件匹配成功一次后会自动删除
        """

    def SetBlock(self, block: bool) -> BasePlugin:
        """
        设置当前插件处理成功后是否阻断后续插件执行
        """

    def SetPriority(self, priority: bool) -> BasePlugin:
        """
        设置当前插件优先级

        优先级默认为 10, priority的数值越小优先级越高
        """

async def only_group(session:Session)->bool:
    """
    判断该会话是否为群事件
    """


async def only_friend(session:Session)->bool:
    """
    判断该会话是否为好友事件
    """


def check_at(user_id:int) -> Callable[[Session], Coroutine[Any, Any, bool]]:
    """
    判断用户是否在此次事件中被 At

    :param user_id: 被判断用户的 QQ 账号
    """


def check_type(*type_group:str) -> Callable[[Session], Coroutine[Any, Any, bool]]:
    """
    判断事件类型

    :param type_group: 用于判断的事件类型组

    群消息 group_msg

    好友消息 friend_msg

    进群事件 group_increase

    退群事件 group_decrease

    禁言事件 group_shutup

    """


def check_user(*uid_group:Tuple[int]) -> Callable[[Session], Coroutine[Any, Any, bool]]:
    """
    判断事件来源的用户

    :param uid_group: 用于判断的账号元组(以可变参传入)
    """


def check_group(*gid_group:Tuple[int]) -> Callable[[Session], Coroutine[Any, Any, bool]]:
    """
    判断事件来源的群

    :param gid_group: 用于判断的群号元组(以可变参传入)
    """

def check_session(session_: Session) -> Callable[[Session], Coroutine[Any, Any, bool]]:
    """
    判断两次 Session 的连续性

    :param session_: 任意一次 Session
    """

def must_given(prompt: str) -> Callable[[Session], Coroutine[Any, Any, bool]]:
    """
    将事件来源 30 秒内的下一次输入当作 session.matched

    :param prompt: 发送给消息来源索要参数的语句
    """

def on(
    *rules: Callable[[Session], Coroutine[Any, Any, bool]],
    temp: bool = False,
    block: bool = False,
    priority: int = 10
) -> BasePlugin:
    """
    元匹配触发器

    :param rules: 匹配规则函数集

    :param temp: 是否为临时插件

    :param block: 执行完成是否阻断后续插件

    :param priority: 插件优先等级
    """


def on_full(
    key: str,
    *rules: Callable[[Session], Coroutine[Any, Any, bool]],
    temp: bool = False,
    block: bool = False,
    priority: int = 10
) -> BasePlugin:
    """
    当消息内容为关键词时满足匹配

    :param key: 关键词

    :param rules: 匹配规则函数集

    :param temp: 是否为临时插件

    :param block: 执行完成是否阻断后续插件

    :param priority: 插件优先等级
    """


def on_fulls(
    key_group: Iterable[str],
    *rules: Callable[[Session], Coroutine[Any, Any, bool]],
    temp: bool = False,
    block: bool = False,
    priority: int = 10
) -> BasePlugin:
    """
    当消息内容是关键词组中任意关键词时满足匹配

    :param key_group: 关键词组

    :param rules: 匹配规则函数集

    :param temp: 是否为临时插件

    :param block: 执行完成是否阻断后续插件

    :param priority: 插件优先等级
    """


def on_keyword(
    key: str,
    *rules: Callable[[Session], Coroutine[Any, Any, bool]],
    temp: bool = False,
    block: bool = False,
    priority: int = 10
) -> BasePlugin:
    """
    当消息内容中含有关键词时满足匹配

    :param key: 关键词

    :param rules: 匹配规则函数集

    :param temp: 是否为临时插件

    :param block: 执行完成是否阻断后续插件

    :param priority: 插件优先等级
    """


def on_keywords(
    key_group: Iterable[str],
    *rules: Callable[[Session], Coroutine[Any, Any, bool]],
    temp: bool = False,
    block: bool = False,
    priority: int = 10
) -> BasePlugin:
    """
    当消息内容中含有关键词组中任意关键词时满足匹配

    :param key_group: 关键词组

    :param rules: 匹配规则函数集

    :param temp: 是否为临时插件

    :param block: 执行完成是否阻断后续插件

    :param priority: 插件优先等级
    """


def on_command(
    cmd: str,
    *rules: Callable[[Session], Coroutine[Any, Any, bool]],
    prompt:str = "",
    temp: bool = False,
    block: bool = False,
    priority: int = 10
) -> BasePlugin:
    """
    当命令词在消息内容首部时满足匹配

    匹配结果保存至 session.match

    :param cmd: 命令词

    :param rules: 匹配规则函数集

    :param temp: 是否为临时插件

    :param block: 执行完成是否阻断后续插件

    :param priority: 插件优先等级

    :param prompt: 若匹配内容为空, 则发送 prompt 语句, 并将对方的下一条消息当作匹配结果
    """

def on_commands(
    cmd_group: Tuple[str],
    *rules: Callable[[Session], Coroutine[Any, Any, bool]],
    prompt:str = "",
    temp: bool = False,
    block: bool = False,
    priority: int = 10
) -> BasePlugin:
    """
    当命令词组内任意目录在消息内容首部时满足匹配

    匹配结果保存至 session.match

    :param cmd_group: 命令词组

    :param rules: 匹配规则函数集

    :param temp: 是否为临时插件

    :param block: 执行完成是否阻断后续插件

    :param priority: 插件优先等级

    :param prompt: 若匹配内容为空, 则发送 prompt 语句, 并将对方的下一条消息当作匹配结果
    """

def on_regex(
    pattern:str,
    *rules: Callable[[Session], Coroutine[Any, Any, bool]],
    temp: bool = False,
    block: bool = False,
    priority: int = 10
) -> BasePlugin:
    """
    当消息内容能被此正则式解析是满足匹配

    匹配结果保存至 session.match

    :param pattern: 正则表达式

    :param rules: 匹配规则函数集

    :param temp: 是否为临时插件

    :param block: 执行完成是否阻断后续插件

    :param priority: 插件优先等级
    """