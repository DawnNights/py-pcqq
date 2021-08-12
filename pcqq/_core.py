import os
import re
import time
import asyncio
import pcqq.utils as utils
from ._unpack import QQUnPack

class Plugin:
    def __init__(self, bot, msg):
        self.Bot = bot
        self.Msg = msg
        self.Args = None

    def on_full_match(self, keyword="") -> bool:
        return self.Msg.MsgText == keyword

    def on_reg_match(self, pattern="") -> bool:
        self.Args = re.findall(pattern, self.Msg.MsgText)
        if self.Args != []:
            return True
        return False
    
    def send_msg(self, msgText:str):
        if self.Msg.MsgType == "friend":
            self.Bot.SendUserMsg(self.Msg.FromQQ, msgText)
        elif self.Msg.MsgType == "group":
            self.Bot.SendGroupMsg(self.Msg.FromGroup, msgText)
    
    def match(self)->bool:
        return self.on_full_match("hello")
    
    def handle(self):
        return self.send_msg("hello world")

class QQBot(QQUnPack):
    def __init__(self, path=""):
        super().__init__()

        # 获取登录二维码
        self.QQ.Send(self._pack0825())
        self._unpack0825(self.QQ.Recv())

        # 解析登录二维码
        self.QQ.Send(self._pack0818())
        codeId,codeImg = self._unpack0818(self.QQ.Recv())
        
        if path == "":
            path = os.getcwd()+"\\QrCode.jpg"
        while True:
            try:
                with open(path, "wb") as f:
                    f.write(codeImg)
                    print("ID:", codeId, "登录二维码获取成功，已保存至", path)
                break
            except:
                continue
        os.startfile(path)
        
        # 等待扫码登录
        for x in range(60):
            self.QQ.Send(self._pack0819(codeId))
            stateId = self._unpack0819(self.QQ.Recv())
            if stateId == 0:
                self.QQ.Send(self._pack0825(1))
                self._unpack0825(self.QQ.Recv())

                try:
                    self.QQ.Send(self._pack0836())
                    self._unpack0836(self.QQ.Recv())
                except:
                    input("登录失败，可能是您的设备开启了登录保护\n请在手机QQ的设置-账号安全-登录设备管理中关闭[登录保护]\n")
                    exit()

                self.QQ.Send(self._pack0828())
                self._unpack0828(self.QQ.Recv())

                self.QQ.Send(self._pack00EC(1)) # 置登录状态为上线

                self.QQ.Send(self._pack001D())
                self._unpack001D(self.QQ.Recv())

                print("NickName:", self.QQ.NickName)
                print("UserQQ:", self.QQ.LongQQ)
                print("Sessionkey:", utils.Bin2HexTo(self.QQ.SessionKey))
                # print("Clientkey:", utils.Bin2HexTo(self.QQ.ClientKey))
                print("************欢迎登录************")
                break
            time.sleep(1)
        
        if stateId != 0:
            input("扫码登录超时，请重新运行程序！\n")
            exit()
        
    def SendGroupMsg(self, groupId:int, content:str):
        '''
        发送群消息
        :param groupId: 发送群号
        :param content: 发送内容
        '''
        self.QQ.Send(self._pack0002(groupId,content))
        if self.QQ.Recv() != b'':
            print(self.QQ.NickName+":",content,"-> GroupID:",groupId)
        else:
            print("Warn: 群消息发送失败")

    def SendUserMsg(self, userId:int, content:str):
        '''
        发送私聊消息
        :param userId: 发送账号
        :param content: 发送内容
        '''
        self.QQ.Send(self._pack00CD(userId, content))
        if self.QQ.Recv() != b'':
            print(self.QQ.NickName + ":", content, "-> UserID:", userId)
        else:
            print("Warn: 好友消息发送失败")
    
    def ListenMsg(self):
        async def listen(self:QQBot):
            key = []
            msg = None
            src = self.QQ.Recv()
            
            if src[5:7] == b'\x00\xce': # 好友消息
                msg = self._unpack00CE(src, key)
                self.QQ.Send(self._pack00CE(key[0], src[7:9]))
                self.QQ.Send(self._pack0319(msg))
            elif src[5:7] == b'\x00\x17':  # 群消息
                msg = self._unpack0017(src, key)
                self.QQ.Send(self._pack0017(key[0], src[7:9]))
                self.QQ.Send(self._pack0002(msg))
            
            if msg != None:
                for plugin in Plugin.__subclasses__():
                    demo = plugin(self, msg)
                    if demo.match():
                        demo.handle()
        
        self._loop = asyncio.get_event_loop()
        while True:
            try:
                # self.QQ.Send(self._pack0058())  # 保持心跳，不要断气
                self._loop.run_until_complete(listen(self))
            except Exception as err:
                # 只要我忽略所有异常，程序就不会报错(～￣▽￣)～
                # print("Error:",err)
                pass