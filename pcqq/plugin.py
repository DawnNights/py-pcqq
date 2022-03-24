import re
import asyncio
import pcqq.client as cli
import pcqq.logger as logger


class BasePlugin:
    def __init__(self, rules):
        self.rules = rules
        self.temp = ...
        self.block = ...
        self.handle = ...
        self.priority = ...

    def __call__(self, handle):
        self.handle = handle
        return self

    def SetTemp(self, temp: bool):
        self.temp = temp
        return self

    def SetBlock(self, block: bool):
        self.block = block
        return self

    def SetPriority(self, priority=10):
        self.priority = priority
        return self

# Builtin Plugin Rule


async def only_group(session):
    return bool(session.group_id)


async def only_friend(session):
    return not session.group_id and session.user_id


def check_at(user_id):
    async def check_rule(session):
        return {"type": "at", "qq": user_id} in session.raw_message
    return check_rule


def check_type(*type_group):
    async def check_rule(session):
        return session.event_type in type_group
    return check_rule


def check_user(*uid_group):
    async def check_rule(session):
        return session.user_id in uid_group
    return check_rule


def check_group(*gid_group):
    async def check_rule(session):
        return session.group_id in gid_group
    return check_rule


def check_session(session_):
    async def check_rule(session):
        user_eq = session_.user_id == session.user_id
        group_eq = session_.group_id == session.group_id
        time_eq = session_.timestamp < session.timestamp
        return user_eq and group_eq and time_eq
    return check_rule


def must_given(prompt):
    async def wait_rule(session):
        await session.send_msg({"type": "at", "qq": session.user_id}, prompt)

        @on(check_session(session), temp=True, block=True, priority=-float("inf"))
        async def wait_input(next_session):
            session.matched = next_session.message

        wait_times = 60
        while not session.matched and wait_times:
            await asyncio.sleep(0.5)
            wait_times -= 1

        try:
            del cli.plugins[cli.plugins.index(wait_input)]
            logger.error(f"等待会话 {session.user_id} 输入 -> 超时")
        except ValueError:
            logger.info(f"捕获会话 {session.user_id} 输入 -> {session.matched}")

            return bool(session.matched)
    return wait_rule

# Builtin Plugin registrar


def on(*rules, temp=False, block=False, priority=10):
    plugin = BasePlugin(rules)
    plugin.SetTemp(temp)
    plugin.SetBlock(block)
    plugin.SetPriority(priority)

    cli.plugins.append(plugin)
    cli.plugins.sort(key=lambda p: p.priority)
    return plugin


def on_full(key, *rules, **params):
    async def full_rule(session):
        return key == session.message
    return on(*rules, full_rule, **params)


def on_fulls(key_group, *rules, **params):
    async def fulls_rule(session):
        return session.message in key_group
    return on(*rules, fulls_rule, **params)


def on_keyword(key, *rules, **params):
    async def key_rule(session):
        return key in session.message
    return on(*rules, key_rule, **params)


def on_keywords(key_group, *rules, **params):
    async def keys_rule(session):
        for key in key_group:
            if key in session.message:
                return True
        return False
    return on(*rules, keys_rule, **params)


def on_command(cmd, *rules, prompt="", **params):
    async def cmd_rule(session):
        if session.message.startswith(cmd):
            session.matched = session.message[len(cmd):].strip()

        if session.matched == "" and prompt:
            return await must_given(prompt)(session)

        return bool(session.matched)

    return on(*rules, cmd_rule, **params)


def on_commands(cmd_group, *rules, prompt="", **params):
    async def cmds_rule(session):
        if session.matched:
            return True

        for cmd in cmd_group:
            if session.message.startswith(cmd):
                session.matched = session.message[len(cmd):].strip()

            if session.matched == "" and prompt:
                return await must_given(prompt)(session)

        return bool(session.matched)

    return on(*rules, cmds_rule, **params)


def on_regex(pattern, *rules, **params):
    async def reg_rule(session):
        session.matched = re.findall(pattern, session.message)

        return bool(session.matched)
    return on(*rules, reg_rule, **params)
