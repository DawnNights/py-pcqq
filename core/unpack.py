# 组解密协议包
from .utils import *
from .pack import QQ_PACK
from time import localtime,strftime

class QQ_UnPack(QQ_PACK):
    def unpack_0825(self, src: bytes)->bool:
        tea = qqTea.Tea()
        unpack = packDecrypt.PackDecrypt()

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

    def unpack_0818(self, src: bytes)->tuple:
        '''解析二维码地址'''
        tea = qqTea.Tea()
        unpack = packDecrypt.PackDecrypt()

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



    def unpack_0819(self,src: bytes)->int:
        '''
        取二维码状态
        0 = 授权成功
        1 = 扫码成功
        2 = 未扫码
        3 = 空数据包
        :return: 状态码
        '''

        tea = qqTea.Tea()
        unpack = packDecrypt.PackDecrypt()

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

    def unpack_0836(self, src: bytes)->bool:
        tea = qqTea.Tea()
        unpack = packDecrypt.PackDecrypt()

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
            tlvName = util.Bin2HexTo(unpack.GetBin(2))
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


    def unpack_0828(self, src: bytes):
        '''解析SessionKey'''
        tea = qqTea.Tea()
        unpack = packDecrypt.PackDecrypt()

        unpack.SetData(src)
        unpack.GetBin(16)
        dst = unpack.GetAll()
        dst = dst[0:-1]
        dst = tea.Decrypt(dst,self.QQ.PcKeyFor0828Rev)

        unpack.SetData(dst)
        unpack.GetBin(63)
        self.QQ.SessionKey = unpack.GetBin(16)

    def unpack_001D(self, src: bytes):
        '''解析Clientkey'''
        tea = qqTea.Tea()
        unpack = packDecrypt.PackDecrypt()

        unpack.SetData(src)
        unpack.GetBin(9)

        unpack.GetInt()
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

    def unpack_00CE(self, src: bytes, key: list)->tuple:
        '''
        解析好友消息包
        :param src: 解密包体
        :param key: 传回确认标识体(代替指针)
        :return: (recvTime, fromQQ, msgText)
        '''
        tea = qqTea.Tea()
        unpack = packDecrypt.PackDecrypt()

        unpack.SetData(src)
        unpack.GetBin(16)
        dst = unpack.GetAll()
        dst = dst[0:len(dst) - 1]
        dst = tea.Decrypt(dst,self.QQ.SessionKey)
        if len(dst) == 0:
            print("00CE解包失败")
            return (0,0,"")

        key.append(dst[0:16])
        unpack.SetData(dst)

        fromQQ = unpack.GetInt()  # 来源QQ
        unpack.GetInt()  # 自身QQ
        unpack.GetBin(14)

        length = int(unpack.GetShort())
        unpack.GetBin(length)

        unpack.GetBin(2)  # QQ版本
        unpack.GetInt()  # 来源QQ
        unpack.GetInt()  # 自身QQ

        unpack.GetBin(16)  # 会话令牌
        unpack.GetBin(4)

        receiveTime = unpack.GetInt()  # 接收时间

        try:
            unpack.GetBin(6)  # 头像、字体属性
            unpack.GetBin(5)  # 消息相关信息

            unpack.GetBin(24)
            length = int(unpack.GetShort())
            unpack.GetBin(length)  # 字体名称
            unpack.GetBin(2)

            msg = []
            MsgParse(unpack.GetAll(),msg)
            print("<%s>收到好友(%d)消息: " % (strftime("%Y-%m-%d %H:%M:%S", localtime(receiveTime)),fromQQ) + "".join(msg))
            return (receiveTime,fromQQ,"".join(msg))
        except:
            print("<%s> Warn: 好友(%d)消息解析失败" % (strftime("%Y-%m-%d %H:%M:%S", localtime(receiveTime)),fromQQ))
            return (receiveTime,fromQQ,"")

    def unpack_0017(self,src:bytes,key:list)->tuple:
        '''
        解析群消息包
        :param src: 解密包体
        :param key: 传回确认标识体(代替指针)
        :return: (fromGroup, msgText)
        '''
        tea = qqTea.Tea()
        unpack = packDecrypt.PackDecrypt()

        unpack.SetData(src)
        unpack.GetBin(16)
        dst = unpack.GetAll()
        dst = dst[0:len(dst) - 1]
        dst = tea.Decrypt(dst,self.QQ.SessionKey)
        if len(dst) == 0:
            return (0,"")

        key.append(dst[0:16])
        unpack.SetData(dst)

        fromGroup = unpack.GetInt()  # 接收群号
        selfQQ = unpack.GetInt()  # 自身QQ
        unpack.GetBin(10)
        typeOf = unpack.GetShort()  # 消息类型

        length = unpack.GetInt()
        unpack.GetBin(length)

        if len(unpack.GetAll()) < 5:
            return (fromGroup, "")
        unpack.GetInt()
        flag = unpack.GetByte()

        if typeOf == 82 and flag == 1:  # 群消息
            fromQQ = unpack.GetInt()  # 接收QQ
            if fromQQ == selfQQ:
                return (fromGroup, "")
            unpack.GetInt()  # 消息索引
            receiveTime = unpack.GetInt()  # 接收时间
            unpack.GetBin(24)
            unpack.GetInt()  # 发送时间
            unpack.GetInt()  # 消息ID
            unpack.GetBin(8)

            length = int(unpack.GetShort())
            unpack.GetBin(length)  # 字体
            unpack.GetBin(2)

            # 以下是消息正文
            try:
                data = unpack.GetAll()
                pos = data.find(util.Hex2Bin("4 0 C0 4 0 CA 4 0 F8 4 0"))
                unpack.SetData(data[pos+35:])


                length = unpack.GetShort()
                fromUserName = unpack.GetBin(length).decode()  # 发消息者昵称

                msg = []
                MsgParse(data[0:pos], msg)
                print("<%s>收到群聊(%d)消息 %s[%d]: " % (strftime("%Y-%m-%d %H:%M:%S", localtime(receiveTime)),fromGroup, fromUserName, fromQQ)+"".join(msg))
                return (fromGroup, "".join(msg))
            except Exception as err:
                print("<%s> Warn: 群聊(%d)消息解析失败:" % (strftime("%Y-%m-%d %H:%M:%S", localtime(receiveTime)), fromGroup),err)
        return (fromGroup, "")