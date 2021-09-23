import pcqq.utils.log as log

from typing import List
from re import findall
from . import Session, Rule, HandleFunc


class Plugin:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self):
        for rule in self.rules:
            if not rule(self.session):
                return

        self.handle()


def on_event(*rules: Rule):
    def wrapper(func: HandleFunc):
        type(func.__name__, (Plugin, ), {
            'rules': rules,
            'handle': lambda self: func(self.session)
        })
        log.Println(f'Succeeded to import "plugin.{func.__name__}"')

    return wrapper


def on_regex(pattern: str, *rules: Rule):
    def regRule(session: Session) -> Rule:
        session._matched_ = findall(pattern, session.event.MessageText)
        return bool(session._matched_)

    return on_event(*rules, regRule)


def on_full(keyword: str, *rules: Rule):
    def fullRule(session: Session) -> Rule:
        return session.event.MessageText == keyword

    return on_event(*rules, fullRule)


def on_command(cmd: str, *rules: Rule, aliases: List[str] = []):
    aliases.insert(0, cmd)

    def cmdRule(session: Session) -> Rule:
        for cmd in aliases:
            if session.event.MessageText.startswith(cmd):
                idx = session.event.MessageText.find(cmd) + len(cmd)
                session._matched_ = session.event.MessageText[idx:].strip()
                return True

    return on_event(*rules, cmdRule)