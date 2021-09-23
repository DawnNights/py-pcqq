import time
import queue
import threading

import pcqq.utils as utils
import pcqq.utils.log as log
import pcqq.binary as binary
import pcqq.client as client

from .api import GetNickName
from .const import BODY_VERSION, FUNC_VERSION, TAIL
from .event import Event
from .message import MessageSegment


class QQDriver:
    def __init__(self, qq_client: client.QQClient, *adminList: int) -> None:
        self._Caller_ = qq_client
        self.AdminList = adminList

        self._WaitDict_ = {}
        self.Channle = queue.Queue()

        threading.Thread(target=self.__HeartBeat__).start()
        threading.Thread(target=self.__ListenEvent__).start()

    def __HeartBeat__(self):
        '''与服务端保持心跳连接(40s)'''
        self._Caller_.Send(
            self._Caller_.Pack('00 58', BODY_VERSION, b'\x00\x01\x00\x01'))
        threading.Timer(40.0, self.__HeartBeat__).start()

    def __ListenEvent__(self):
        '''循环监听事件'''
        writer = binary.Writer()

        while True:
            try:
                src = self._Caller_.Recv()
                bin = binary.TeaDecrypt(src[16:-1], self._Caller_.SessionKey)
                self._Caller_.Send(
                    src[2:13] + BODY_VERSION +
                    binary.TeaEncrypt(bin[0:16], self._Caller_.SessionKey) +
                    TAIL)  # 初步回执
            except:
                continue

            event = Event(bin)
            if not event.EventType:
                continue

            if event.EventType == "group" or event.EventType == "group_increase":

                writer.WriteByte(41)
                writer.WriteInt(utils.GroupToGid(event.GroupID))
                writer.WriteByte(2)
                writer.WriteInt(event.MessageID)

                self._Caller_.Send(
                    self._Caller_.Pack("00 02", BODY_VERSION,
                                       writer.ReadAll()))

            elif event.EventType == "private":

                writer.WriteHex("08 01")
                writer.WriteHex("12 03 98 01 00")
                writer.WriteHex("0A 0E 08")
                writer.WriteVarInt(event.UserID)
                writer.WriteHex("10")
                writer.WriteVarInt(event.Time)
                writer.WriteHex("20 00")
                body = writer.ReadAll()

                writer.WriteHex("00 00 00 07")
                writer.WriteInt(len(body) - 7)
                writer.WriteBytes(body)

                self._Caller_.Send(
                    self._Caller_.Pack("03 19", FUNC_VERSION,
                                       writer.ReadAll()))

            if (event.GroupID, event.UserID) in self._WaitDict_.keys():
                self._WaitDict_[(event.GroupID,
                                   event.UserID)] = event.MessageText
                continue

            self.Channle.put(event)

    def Api_GetNickName(self, userID: int):
        '''取用户名称'''
        return GetNickName(userID)

    def Api_ExitLogin(self):
        '''退出登录'''
        self._Caller_.Send(self._Caller_.Pack('00 62', BODY_VERSION,
                                              bytes(16)))

    def Api_SendPrivateMsg(self, userID: int, msgBody: MessageSegment):
        '''发送私聊消息'''
        writer = binary.Writer()
        timeStamp = int(time.time())

        writer.WriteBytes(self._Caller_.BinQQ)
        writer.WriteInt(userID)
        writer.WriteHex('00 00 00 08 00 01 00 04 00 00 00 00 36 39')
        writer.WriteBytes(self._Caller_.BinQQ)
        writer.WriteInt(userID)
        writer.WriteBytes(utils.HashMD5(timeStamp.to_bytes(4, 'big')))
        writer.WriteHex('00 0B 4A B6')
        writer.WriteBytes(timeStamp.to_bytes(4, 'big'))
        writer.WriteHex(
            '02 55 00 00 00 00 01 00 00 00 01 4D 53 47 00 00 00 00 00')
        writer.WriteBytes(timeStamp.to_bytes(4, 'big'))
        writer.WriteBytes(timeStamp.to_bytes(4, 'little'))
        writer.WriteHex(
            '00 00 00 00 09 00 86 00 00 06 E5 AE 8B E4 BD 93 00 00')
        writer.WriteBytes(msgBody.ReadAll())

        self._Caller_.Send(
            self._Caller_.Pack('00 CD', BODY_VERSION, writer.ReadAll()))

        if self._Caller_.Recv() != b'':
            log.Println(f"发送私聊({userID})消息: {msgBody.source}")
        else:
            log.Panicln(f"发送私聊({userID})消息失败")

    def Api_SendGroupMsg(self, groupID: int, msgBody: MessageSegment) -> bool:
        '''发送群聊消息'''
        writer = binary.Writer()
        timeStamp = int(time.time())

        writer.WriteHex(
            '00 01 01 00 00 00 00 00 00 00 4D 53 47 00 00 00 00 00')
        writer.WriteBytes(timeStamp.to_bytes(4, 'big'))
        writer.WriteBytes(timeStamp.to_bytes(4, 'little'))
        writer.WriteHex(
            '00 00 00 00 09 00 86 00 00 06 E5 AE 8B E4 BD 93 00 00')
        writer.WriteBytes(msgBody.ReadAll())
        body = writer.ReadAll()

        writer.WriteHex('2A')
        writer.WriteInt(groupID)
        writer.WriteShort(len(body))
        writer.WriteBytes(body)

        self._Caller_.Send(
            self._Caller_.Pack('00 02', BODY_VERSION, writer.ReadAll()))

        if self._Caller_.Recv() != b'':
            log.Println(f"发送群聊({groupID})消息: {msgBody.source}")
        else:
            log.Panicln(f"发送私聊({groupID})消息失败")