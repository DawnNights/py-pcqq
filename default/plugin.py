import traceback

from asyncio import Queue
from dataclasses import dataclass
from typing import Any, List, Union, Iterable, Callable, Coroutine

from logger import logger
from core.protocol import pcapi, webapi
from core.client import QQClient
from core.entities import (
    MessageEvent,
    NoticeEvent,
    Message,
    TextNode
)


@dataclass
class Session:
    driver: QQClient
    message: str
    event: Union[MessageEvent, NoticeEvent]
    matched: Union[str, list]

    async def aget(self, prompt: str):
        await self.send_msg(prompt)
        chan = Queue(maxsize=1, loop=self.driver.loop)

        @on_event(check_session(self), temp=True, block=True)
        async def wait_input(session: Session):
            await chan.put(session.message)

        return await chan.get()

    async def send_msg(self, text: str):
        if self.event.group_id != 0:
            await self.send_group_msg(self.event.group_id, text)
        elif self.event.user_id != 0:
            await self.send_private_msg(self.event.user_id, text)

    async def send_group_msg(self, group_id: int, text: str):
        node = TextNode(text)
        pcapi.send_group_msg(self.driver, group_id, Message().add(node))

        group = await webapi.get_group(self.driver, group_id)
        logger.info(f"发送群聊 {group.name}({group_id}) 消息 -> {text}")

    async def send_private_msg(self, user_id: int, text: str):
        node = TextNode(text)
        pcapi.send_private_msg(self.driver, user_id, Message().add(node))

        user = await webapi.get_user(self.driver, user_id)
        logger.info(f"发送私聊 {user.name}({user_id}) 消息 -> {text}")

    async def set_group_card(self, group_id: int, user_id: int, new_card: str):
        await webapi.set_group_card(
            self.driver.stru,
            group_id,
            user_id,
            new_card
        )


Rule = Callable[[Session], Coroutine[Any, Any, bool]]


@dataclass
class Plugin:
    rules: Iterable[Rule]
    temp: bool
    block: bool
    priority: int
    handle: Callable[[Session], Coroutine[Any, Any, None]]

    async def exec(self, session: Session):
        for rule in self.rules:
            if await rule(session):
                continue
            return None
        await self.handle(session)


class PluginManager(List[Plugin]):
    def append(self, plugin: Plugin):
        if not isinstance(plugin, Plugin):
            raise ValueError("PluginManager 添加的元素不是 Plugin 类型")

        if not plugin in self:
            super().append(plugin)

        return self

    def pop(self, plugin: Plugin):
        if plugin in self:
            super().pop(self.index(plugin))

        return self

    async def exec_all(self, session: Session):
        try:
            for plugin in self:
                await plugin.exec(session)
                if plugin.temp:
                    self.pop(plugin)
                if plugin.block:
                    continue
        except:
            traceback.print_exc()

# =============== Buttlin Rule ===============


async def only_message(session: Session):
    return isinstance(session.event, MessageEvent)


async def only_notice(session: Session):
    return isinstance(session.event, NoticeEvent)


async def only_private(session: Session):
    event = session.event
    return event.group_id == 0 and event.user_id != 0


async def only_group(session: Session):
    return session.event.group_id != 0


def check_user(*user_ids: int):
    async def new_rule(session: Session):
        return session.event.user_id in user_ids
    return new_rule


def check_session(session: Session):
    async def new_rule(next_session: Session):
        event = session.event
        next_event = next_session.event

        if event.user_id != next_event.user_id:
            return False

        if event.group_id != next_event.group_id:
            return False

        return True

    return new_rule

# =============== Buttlin Plugin Registrar ===============


default_manager = PluginManager()


def on_event(*rules: Rule, temp=False, block=False, priority=10):
    def decorator(handle: Callable[[Session], Coroutine[Any, Any, None]]):
        default_manager.append(Plugin(
            rules=rules,
            temp=temp,
            block=block,
            priority=priority,
            handle=handle
        ))

    return decorator


def on_message(*rules: Rule, temp=False, block=False, priority=10):
    return on_event(
        only_message,
        *rules,
        temp=temp,
        block=block,
        priority=priority
    )


def on_command(cmd: str, *rules: Rule, temp=False, block=False, priority=10):
    async def cmd_rule(session: Session):
        text = session.message
        if text.startswith(cmd):
            session.matched = text.replace(cmd, "", 1).strip()
            return True
        return False

    return on_event(
        cmd_rule,
        *rules,
        temp=temp,
        block=block,
        priority=priority
    )
