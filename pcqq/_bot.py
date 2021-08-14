import re
import os
import time
import asyncio
import threading
import logging as log
from pcqq.package import *
from ._msg import *
from ._client import QQClient
from ._struct import QQStruct

log.basicConfig(level=log.DEBUG, format="[pcqq] time=\"%(asctime)s\" level=%(levelname)s msg=\"%(message)s\"")


class Plugin:
    def __init__(self, bot, msg):
        self.Bot = bot
        self.Msg = msg
        self.Args = None

    def match(self):
        '''判断接收消息是否被匹配'''
        return self.on_full_match("hello")
    
    def handle(self):
        '''当消息匹配时所触发的事件'''
        self.send_msg("hello world")

    def on_full_match(self, keyword="") -> bool:
        '''当接收到的消息是keyword时满足匹配'''
        return self.Msg.MsgText == keyword

    def on_reg_match(self, pattern="") -> bool:
        '''当接收的消息满足pattern表达式时触发匹配，并将匹配结果存入self.Args'''
        self.Args = re.findall(pattern, self.Msg.MsgText)
        if self.Args != []:
            return True
        return False

    def send_msg(self, msgText: str):
        if self.Msg.MsgType == "friend":
            self.Bot.SendUserMsg(self.Msg.FromQQ, msgText)
        elif self.Msg.MsgType == "group":
            self.Bot.SendGroupMsg(self.Msg.FromGroup, msgText)

class QQBot:
    def __init__(self):
        self.QQ = QQStruct()
        self.QQ.RandHead16 = utils.GetRandomBin(16)
        self.QQ.ShareKey = utils.Hex2Bin("FD 0B 79 78 31 E6 88 54 FC FA EA 84 52 9C 7D 0B")
        self.QQ.PublicKey = utils.Hex2Bin("03 94 3D CB E9 12 38 61 EC F7 AD BD E3 36 91 91 07 01 50 BE 50 39 1C D3 32")

        self.Client = QQClient()
        self._GetQrCode()

        log.info(f"账号{self.QQ.LongQQ}登录成功")
        log.info(f"欢迎登录，尊敬的用户【{self.QQ.NickName}】")

        h = threading.Thread(target=self._Heart)
        h.start()

    def ListenMsg(self):
        '''监听消息'''
        async def listen(self:QQBot):
            msg = Message()
            src = self.Client.Recv()
            if src[5:7] == USERMESSAGE:  # 好友消息
                if UnPack_00CE(self.QQ, src, msg):
                    log.info(f"收到用户({msg.FromQQ})消息: {msg.MsgText}")
                    self.Client.Send(Pack_00CE(self.QQ, msg.HeadBody, src[7:9]))
                    self.Client.Send(Pack_0319(self.QQ, msg))
            elif src[5:7] == GROUPMESSAGE:  # 群消息
                if UnPack_0017(self.QQ, src, msg):
                    log.info(f"收到群({msg.FromGroup})消息 {msg.NickName}: {msg.MsgText}")
                    self.Client.Send(Pack_0017(self.QQ, msg.HeadBody, src[7:9]))
                    self.Client.Send(Pack_0002_receipt(self.QQ, msg))
            if msg.MsgText != "":
                for plugin in Plugin.__subclasses__():
                    demo = plugin(self, msg)
                    if demo.match():
                        demo.handle()

        loop = asyncio.get_event_loop()
        while True:
            try:
                loop.run_until_complete(listen(self))
            except:
                pass    # 只要我忽略所有异常，程序就不会报错(～￣▽￣)～

    def SendGroupMsg(self, groupID:int, msgText:str):
        '''
        发送群消息
        :param groupID: 群号
        :param msgText: 发送文本
        '''
        self.Client.Send(Pack_0002(self.QQ, groupID, msgText))
        if self.Client.Recv() != b"":
            log.info(f'{self.QQ.NickName}: "{msgText}" -> GroupID: {groupID}')
        else:
            log.warning(f"向群{groupID}发送消息失败")

    def SendUserMsg(self, userID:int, msgText:str):
        '''
        发送用户消息
        :param userID: 用户账号
        :param msgText: 发送文本
        '''
        self.Client.Send(Pack_00CD(self.QQ, userID, msgText))
        if self.Client.Recv() != b"":
            log.info(f'{self.QQ.NickName}: "{msgText}" -> UserID: {userID}')
        else:
            log.warning(f"向用户{userID}发送消息失败")

    def _Heart(self):
        '''每隔60秒发送一次心跳包'''
        self.Client.Send(Pack_0058(self.QQ))
        h = threading.Timer(60.0, self._Heart)
        h.start()

    def _GetQrCode(self):
        '''获取登录二维码并等待扫码'''

        # 获取登录二维码
        self.Client.Send(Pack_0825(self.QQ))
        UnPack_0825(self.QQ, self.Client.Recv())

        # 解析登录二维码
        self.Client.Send(Pack_0818(self.QQ))
        QrCodeID, QrCodeImg = UnPack_0818(self.QQ, self.Client.Recv())

        # 保存登录二维码至savePath
        savePath = os.getcwd() + "\\QrCode.jpg"
        while True:
            try:
                with open(savePath, "wb") as f:
                    f.write(QrCodeImg)
                break
            except:
                continue
        log.info("登录二维码获取成功，已保存至"+savePath)
        os.startfile(savePath)

        # 等待扫码登录
        stateID = -1
        for x in range(60):
            self.Client.Send(Pack_0819(self.QQ, QrCodeID))
            stateID = UnPack_0819(self.QQ, self.Client.Recv())
            log.debug("二维码状态: " + {0: "授权成功", 1: "扫码成功", 2: "未扫码", 3: "空数据包"}.get(stateID))
            if stateID == 0:
                self.Client.Send(Pack_0825(self.QQ, True))
                UnPack_0825(self.QQ, self.Client.Recv())
                log.debug(f"地址重定向为{self.QQ.ConnectSeverIpText}")
                try:
                    self.Client.Send(Pack_0836(self.QQ))
                    UnPack_0836(self.QQ, self.Client.Recv())
                except:
                    input("登录失败，可能是您的设备开启了登录保护\n请在手机QQ的设置-账号安全-登录设备管理中关闭[登录保护]\n")
                    exit()

                self.Client.Send(Pack_0828(self.QQ))
                UnPack_0828(self.QQ, self.Client.Recv())

                self.Client.Send(Pack_00EC(self.QQ, 1))  # 置登录状态为上线

                self.Client.Send(Pack_001D(self.QQ))
                UnPack_001D(self.QQ, self.Client.Recv())
                break
            elif stateID == 1:
                log.info(f"当前扫码账号为: {self.QQ.LongQQ}，请确认登录")
            time.sleep(1)

        if stateID != 0:
            input("扫码登录超时，请重新运行程序！\n")
            exit()