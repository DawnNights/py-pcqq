import pcqq.utils as utils
from ._pack import QQPack
from ._msg import Message
from time import localtime,strftime

class QQUnPack(QQPack):
    def _unpack0825(self, src: bytes)->bool:
        tea = utils.Tea()
        unpack = utils.PackDecrypt()

        unpack.SetData(src)
        unpack.GetBin(16)
        dst = unpack.GetAll()
        dst = dst[0:-1]
        dst = tea.Decrypt(dst,self.QQ.RandHead16)

        unpack.SetData(dst)
        Type = int(unpack.GetByte())
        unpack.GetShort()
        length = unpack.GetShort()
        self.QQ.PcToken0038From0825 = unpack.GetBin(length)
        unpack.GetBin(6)
        unpack.GetBin(4)
        self.QQ.LocalPcIp = unpack.GetBin(4)
        unpack.GetShort()

        if Type == 254: #需要重定向服务器
            unpack.GetBin(18)
            self.QQ.ConnectSeverIp = unpack.GetBin(4)
            print(
                "重定向地址: %d.%d.%d.%d\n"%(
                    self.QQ.ConnectSeverIp[0],
                    self.QQ.ConnectSeverIp[1],
                    self.QQ.ConnectSeverIp[2],
                    self.QQ.ConnectSeverIp[3]
                )
            )
            return True
        else:
            unpack.GetBin(6)
            self.QQ.ConnectSeverIp = unpack.GetBin(4)
            return False

    def _unpack0818(self, src: bytes)->tuple:
        '''解析二维码地址'''
        tea = utils.Tea()
        unpack = utils.PackDecrypt()

        unpack.SetData(src)
        unpack.GetBin(16)
        dst = unpack.GetAll()
        dst = dst[0:-1]
        dst = tea.Decrypt(dst,self.QQ.ShareKey)

        unpack.SetData(dst)
        unpack.GetBin(7)
        self.QQ.PcKeyFor0819 = unpack.GetBin(16)
        unpack.GetBin(4)
        length = int(unpack.GetShort())

        self.QQ.PcToken0038From0818 = unpack.GetBin(length)
        unpack.GetBin(4)
        length = unpack.GetShort()
        codeId = unpack.GetBin(length).decode()

        unpack.GetBin(4)
        length = unpack.GetShort()
        codeImg = unpack.GetBin(length)

        return (codeId,codeImg)



    def _unpack0819(self,src: bytes)->int:
        '''
        取二维码状态
        0 = 授权成功
        1 = 扫码成功
        2 = 未扫码
        3 = 空数据包
        :return: 状态码
        '''

        tea = utils.Tea()
        unpack = utils.PackDecrypt()

        unpack.SetData(src)
        unpack.GetBin(16)
        dst = unpack.GetAll()
        dst = dst[0:-1]
        dst = tea.Decrypt(dst,self.QQ.PcKeyFor0819)

        unpack.SetData(dst)
        stateId = unpack.GetByte()

        print("二维码状态:", {0: "授权成功", 1: "扫码成功", 2: "未扫码", 3: "空数据包"}[stateId])

        if stateId == 1:
            self.QQ.BinQQ = src[9:13]
            self.QQ.LongQQ = int.from_bytes(self.QQ.BinQQ,byteorder='big',signed=False)
            self.QQ.Utf8QQ = str(self.QQ.LongQQ).encode()
            print("当前扫码账号:", self.QQ.LongQQ)
        print("")

        if stateId == 0 and len(dst) > 1:
            unpack.GetShort()
            length = unpack.GetShort()
            self.QQ.PcToken0060From0819 = unpack.GetBin(int(length))
            unpack.GetShort()
            length = unpack.GetShort()
            self.QQ.PcKeyTgt = unpack.GetBin(int(length))
        return stateId

    def _unpack0836(self, src: bytes)->bool:
        tea = utils.Tea()
        unpack = utils.PackDecrypt()

        unpack.SetData(src)
        unpack.GetBin(16)
        dst = unpack.GetAll()
        dst = dst[0:-1]

        if len(dst) >= 100:
            dst = tea.Decrypt(tea.Decrypt(dst,self.QQ.ShareKey),self.QQ.PcKeyTgt)
        if len(dst) == 0:
            return False

        unpack.SetData(dst)
        Type = int(unpack.GetByte())

        if Type != 0:
            print("08 36 返回数据TYPE出错", Type)
            return False

        for i in range(5):
            tlvName = utils.Bin2HexTo(unpack.GetBin(2))
            tlvLength = int(unpack.GetShort())

            if tlvName == "1 9":
                unpack.GetShort()
                self.QQ.PcKeyFor0828Send = unpack.GetBin(16)

                length = int(unpack.GetShort())
                self.QQ.PcToken0038From0836 = unpack.GetBin(length)
                length = int(unpack.GetShort())
                unpack.GetBin(length)
                unpack.GetShort()
            elif tlvName == "1 7":
                unpack.GetBin(26)
                self.QQ.PcKeyFor0828Rev = unpack.GetBin(16)
                length = int(unpack.GetShort())
                self.QQ.PcToken0088From0836 = unpack.GetBin(length)
                length = tlvLength - 180
                unpack.GetBin(length)
            elif tlvName == "1 8":
                unpack.GetBin(8)
                length = int(unpack.GetByte())
                self.QQ.NickName = unpack.GetBin(length).decode()
            else:
                unpack.GetBin(tlvLength)


        if len(self.QQ.PcToken0088From0836) != 136 or len(self.QQ.PcKeyFor0828Send) != 16 or len(self.QQ.PcToken0038From0836) != 56:
            return False
        else:
            return True


    def _unpack0828(self, src: bytes):
        '''解析SessionKey'''
        tea = utils.Tea()
        unpack = utils.PackDecrypt()

        unpack.SetData(src)
        unpack.GetBin(16)
        dst = unpack.GetAll()
        dst = dst[0:-1]
        dst = tea.Decrypt(dst,self.QQ.PcKeyFor0828Rev)

        unpack.SetData(dst)
        unpack.GetBin(63)
        self.QQ.SessionKey = unpack.GetBin(16)

    def _unpack001D(self, src: bytes):
        '''解析Clientkey'''
        tea = utils.Tea()
        unpack = utils.PackDecrypt()

        unpack.SetData(src)
        unpack.GetBin(9)

        print("账号",unpack.GetInt())
        unpack.GetBin(3)

        data = unpack.GetAll()
        data = data[0:-1]
        data = tea.Decrypt(data,self.QQ.SessionKey)

        unpack.SetData(data)
        unpack.GetBin(2)

        self.QQ.ClientKey = unpack.GetAll()

        if len(self.QQ.ClientKey) != 32:
            self.QQ.ClientKey = b''
            return

    def _unpack00CE(self, src: bytes, key: list)->Message:
        '''
        解析好友消息包
        :param src: 解密包体
        :param key: 传回确认标识体(代替指针)
        :return: (recvTime, fromQQ, msgText)
        '''
        msg = Message()
        msg.MsgType = "friend"
        tea = utils.Tea()
        unpack = utils.PackDecrypt()

        unpack.SetData(src)
        unpack.GetBin(16)
        dst = unpack.GetAll()
        dst = dst[0:len(dst) - 1]
        dst = tea.Decrypt(dst,self.QQ.SessionKey)
        if len(dst) == 0:
            print("好友消息解析失败")
            return msg
        key.append(dst[0:16])
        unpack.SetData(dst)

        msg.FromQQ = unpack.GetInt()  # 触发者QQ
        msg.RecvQQ = unpack.GetInt()  # 接收者QQ
        unpack.GetBin(14)

        length = int(unpack.GetShort())
        unpack.GetBin(length)

        unpack.GetBin(2)  # QQ版本
        unpack.GetInt()  # 来源QQ
        unpack.GetInt()  # 自身QQ

        unpack.GetBin(16)  # 会话令牌
        unpack.GetBin(4)

        msg.MsgTime = unpack.GetInt()  # 接收时间

        try:
            unpack.GetBin(6)  # 头像、字体属性
            unpack.GetBin(5)  # 消息相关信息

            unpack.GetBin(24)
            length = int(unpack.GetShort())
            unpack.GetBin(length)  # 字体名称
            unpack.GetBin(2)

            msg.Parse(unpack.GetAll())
            
            print("<%s>收到好友(%d)消息: " % (strftime("%Y-%m-%d %H:%M:%S", localtime(msg.MsgTime)),msg.FromQQ) + msg.MsgText)
        except Exception as err:
            print(err)
            print("<%s> Warn: 好友(%d)消息解析失败" % (strftime("%Y-%m-%d %H:%M:%S", localtime(msg.MsgTime)),msg.FromQQ))
        
        return msg


    def _unpack0017(self,src:bytes,key:list)->Message:
        '''
        解析群消息包
        :param src: 解密包体
        :param key: 传回确认标识体(代替指针)
        :return: (fromGroup, msgText)
        '''
        msg = Message()
        msg.MsgType = "group"
        tea = utils.Tea()
        unpack = utils.PackDecrypt()

        unpack.SetData(src)
        unpack.GetBin(16)
        dst = unpack.GetAll()
        dst = dst[0:len(dst) - 1]
        dst = tea.Decrypt(dst,self.QQ.SessionKey)
        if len(dst) == 0:
            return msg

        key.append(dst[0:16])
        unpack.SetData(dst)

        msg.FromGroup = unpack.GetInt()  # 接收群号
        msg.RecvQQ = unpack.GetInt()  # 自身QQ
        unpack.GetBin(10)
        typeOf = unpack.GetShort()  # 消息类型

        length = unpack.GetInt()
        unpack.GetBin(length)

        if len(unpack.GetAll()) < 5:
            return msg
        unpack.GetInt()
        flag = unpack.GetByte()

        if typeOf == 82 and flag == 1:  # 群消息
            msg.FromQQ = unpack.GetInt()  # 接收QQ
            if msg.FromQQ == msg.RecvQQ:
                return msg
            unpack.GetInt()  # 消息索引
            msg.MsgTime = unpack.GetInt()  # 接收时间
            unpack.GetBin(24)
            unpack.GetInt()  # 发送时间
            msg.MsgId = unpack.GetInt()  # 消息ID
            unpack.GetBin(8)

            length = int(unpack.GetShort())
            unpack.GetBin(length)  # 字体
            unpack.GetBin(2)

            # 以下是消息正文
            try:
                data = unpack.GetAll()
                pos = data.find(utils.Hex2Bin("4 0 C0 4 0 CA 4 0 F8 4 0"))
                unpack.SetData(data[pos+35:])

                length = unpack.GetShort()
                fromUserName = unpack.GetBin(length).decode()  # 发消息者昵称

                msg.Parse(data[0:pos])
                print("<%s>收到群聊(%d)消息 %s[%d]: " % (strftime("%Y-%m-%d %H:%M:%S", localtime(msg.MsgTime)),msg.FromGroup, fromUserName, msg.FromQQ)+msg.MsgText)
            except Exception as err:
                print("<%s> Warn: 群聊(%d)消息解析失败:" % (strftime("%Y-%m-%d %H:%M:%S", localtime(msg.MsgTime)), msg.FromGroup))

            return msg