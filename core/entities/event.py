from .message import Message

from dataclasses import dataclass


@dataclass
class BaseEvent:
    time: int = 0

    self_id: int = 0

    post_type: str = ""


@dataclass
class MessageEvent(BaseEvent):
    post_type: str = "message"

    message_type: str = ""

    sub_type: str = ""

    message_id: int = 0

    message_num: int = 0

    group_id: int = 0

    user_id: int = 0

    message: Message = None


@dataclass
class NoticeEvent(BaseEvent):
    post_type: str = "notice"

    notice_type: str = ""

    sub_type: str = ""

    group_id: int = 0

    operator_id: int = 0

    user_id: int = 0
