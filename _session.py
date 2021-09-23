from time import sleep
from typing import Union, Callable
from pcqq.core import Event, QQDriver, MessageSegment


class Session:
    def __init__(self, driver: QQDriver, event: Event) -> None:
        self._driver_ = driver
        self.event = event
        self._matched_ = None

    def get(self, prompt='') -> Union[list, str, None]:
        '''获取匹配参数，若参数为空且prompt不为空，则发送prompt语句向对方索要参数'''
        if not self._matched_ and prompt:
            if self.event.GroupID:
                prompt = f'[PQ:at,qq={self.event.UserID}]' + prompt

            self.send(prompt)
            self._driver_._WaitDict_[(self.event.GroupID,
                                      self.event.UserID)] = None

            while True:
                self._matched_ = self._driver_._WaitDict_.get(
                    (self.event.GroupID, self.event.UserID))
                if self._matched_:
                    self._driver_._WaitDict_.pop(
                        (self.event.GroupID, self.event.UserID))
                    break
                else:
                    sleep(0.5)

        return self._matched_

    def send(self, message: Union[str, MessageSegment]):
        '''快捷回复消息'''
        if self.event.GroupID == 0:
            return self.send_private_msg(self.event.UserID, message)
        return self.send_group_msg(self.event.GroupID, message)

    def send_group_msg(self, groupID: int, message: Union[str,
                                                          MessageSegment]):
        '''发送群聊消息'''
        if type(message) == str:
            message = MessageSegment(message)

        self._driver_.Api_SendGroupMsg(groupID=groupID, msgBody=message)

    def send_private_msg(self, userID: int, message: Union[str,
                                                           MessageSegment]):
        '''发送私聊消息'''
        if type(message) == str:
            message = MessageSegment(message)

        self._driver_.Api_SendPrivateMsg(userID=userID, msgBody=message)


Rule = Callable[[Session], bool]
HandleFunc = Callable[[Session], None]