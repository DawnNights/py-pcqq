import asyncio
from time import sleep
from .utils import util
from .unpack import QQ_UnPack

class PCQQ(QQ_UnPack):
    def Init(self):
        '''连接服务端'''
        self.Client.Connect()

    def GetQrCode(self):
        '''获取登录二维码并等待登录'''
        self.Client.Send(self.pack_0825(1))
        self.unpack_0825(self.Client.Receive())

        self.Client.Send(self.pack_0818())
        codeId,codeImg = self.unpack_0818(self.Client.Receive())	# 解析二维码

        with open("QrCode.jpg","wb") as f:
            f.write(codeImg)
            print("ID:", codeId, "的二维码已保存至本地\n")

        for i in range(60): # 监听扫码状态
            self.Client.Send(self.pack_0819(codeId, False))
            stateId = self.unpack_0819(self.Client.Receive())

            if stateId == 0 :
                self.Client.Send(self.pack_0825(1))
                self.unpack_0825(self.Client.Receive())

                self.Client.Send(self.pack_0836())
                self.unpack_0836(self.Client.Receive())

                self.Client.Send(self.pack_0828())
                self.unpack_0828(self.Client.Receive())

                self.Client.Send(self.pack_00EC(1)) # 置登录状态为上线

                self.Client.Send(self.pack_001D())
                self.unpack_001D(self.Client.Receive())

                print("NickName:", self.QQ.NickName)
                print("UserQQ:", self.QQ.LongQQ)
                print("Sessionkey:", util.Bin2HexTo(self.QQ.SessionKey))
                print("Clientkey:", util.Bin2HexTo(self.QQ.ClientKey))
                print("************欢迎登录************")
                return

            sleep(1)

    def ListenMsg(self, handle=None):
        '''
        监听消息
        :param handle: 消息处理函数
        '''
        async def listen(self):
            src = self.Client.Receive()
            try:
                if src[5:7] == b'\x00\x17':  # 群消息
                    key = []
                    fromGroup, msgText = self.unpack_0017(src, key)
                    self.Client.Send(self.pack_0017(key[0], src[7:9]))
                    if msgText != "" and handle != None:
                        self.SendGroupMsg(fromGroup, handle(msgText))
                elif src[5:7] == b'\x00\xce':  # 好友消息
                    key = []
                    recvTime, fromQQ, msgText = self.unpack_00CE(src, key)
                    self.Client.Send(self.pack_00CE(key[0], src[7:9]))
                    if msgText != "" and handle != None:
                        self.SendUserMsg(fromQQ, handle(msgText))
            except:
                # 忽略所有发生的异常保持程序的运行
                pass

        loop = asyncio.get_event_loop()
        while True:
            loop.run_until_complete(listen(self))

    def SendGroupMsg(self, groupId:int, content:str):
        '''
        发送群消息
        :param groupId: 发送群号
        :param content: 发送内容
        '''
        self.Client.Send(self.pack_0002(groupId,content))
        if self.Client.Receive() != b'':
            print(self.QQ.NickName+":",content,"-> GroupID:",groupId)
        else:
            print("Warn: 群消息发送失败")

    def SendUserMsg(self, userId:int, content:str):
        '''
        发送私聊消息
        :param userId: 发送账号
        :param content: 发送内容
        '''
        self.Client.Send(self.pack_00CD(userId, content))
        if self.Client.Receive() != b'':
            print(self.QQ.NickName + ":", content, "-> UserID:", userId)
        else:
            print("Warn: 好友消息发送失败")