import os
import time
import platform
import pcqq.log as log
import pcqq.const as const
import pcqq.utils as utils
import pcqq.binary as binary


RedirectionTimes = 0    # 重定向次数
RedirectionHistory = ""   # 重定向历史
PcToken0038From0825 = b''   # 0038令牌
PcToken0038From0836 = b''   # 0038令牌
PcToken0088From0836 = b''   # 0088令牌
PcKeyFor0828Send = b''  # 0828协议包send令牌
PcKeyFor0828Recv = b''  # 0828协议包recv令牌

def SeekServer(QQ, logging:bool=False):
    '''登录服务器探寻'''
    global RedirectionTimes, RedirectionHistory, PcToken0038From0825

    # 发送0825协议包探寻服务器
    writer = binary.Writer()

    writer.WriteBytes(binary.TLV_0018_Ping(QQ.BinQQ, RedirectionTimes))
    if logging:
        writer.WriteBytes(binary.TLV_0309_Ping_Strategy(QQ.SeverIp, RedirectionHistory, RedirectionTimes))
        writer.WriteBytes(binary.TLV_0036_LoginReason())
    else:
        writer.WriteHex("00 04 00 0C 00 00 00 08 71 72 5F 6C 6F 67 69 6E")
        writer.WriteBytes(binary.TLV_0309_Ping_Strategy(QQ.SeverIp, RedirectionHistory, RedirectionTimes))
    writer.WriteBytes(binary.TLV_0114_DHParams())

    QQ.Send(QQ.Pack(
        cmd="08 25",
        body=const.RandHead16+binary.TeaEncrypt(writer.ReadAll(), const.RandHead16),
        version=const.StructVersion,
    ))

    # 解析0825响应包获取重定向信息
    reader = binary.Reader(binary.TeaDecrypt(QQ.Recv()[16:-1], const.RandHead16))
    sign = reader.ReadByte()

    reader.ReadBytes(2)
    PcToken0038From0825 = reader.ReadBytes(reader.ReadShort())

    reader.ReadBytes(6)
    reader.ReadBytes(4)    # ConnectTime
    reader.ReadBytes(4)    # LocalIp

    reader.ReadBytes(2)
    if sign == 0xfe:
        reader.ReadBytes(18)
        QQ.SeverIp = reader.ReadBytes(4)
        RedirectionTimes += 1
        RedirectionHistory += utils.Bin2HexTo(QQ.SeverIp)
    elif sign == 0x00:
        reader.ReadBytes(6)
        QQ.SeverIp = reader.ReadBytes(4)
        RedirectionHistory = ""

def ApplyScanCode(QQ)->bytes:
    '''申请登录二维码并等待扫码'''

    # 发送0818协议包
    writer = binary.Writer()
    writer.WriteHex("00 19 00 10 00 01 00 00 04 4C 00 00 00 01 00 00 15 51 00 00 01 14 00 1D 01 02")
    writer.WriteShort(len(const.PublicKey))
    writer.WriteBytes(const.PublicKey)
    writer.WriteHex("03 05 00 1E 00 00 00 00 00 00 00 05 00 00 00 04 00 00 00 00 00 00 00 48 00 00 00 02 00 00 00 02 00 00")
    QQ.Send(QQ.Pack(
        cmd="08 18",
        body=const.RandHead16 + binary.TeaEncrypt(writer.ReadAll(), const.RandHead16),
        version=const.StructVersion,
    ))

    # 解析0818响应包
    reader = binary.Reader(binary.TeaDecrypt(QQ.Recv()[16:-1], const.ShareKey))
    if reader.ReadByte() != 0x00:
        log.Panicln("获取登录二维码失败")
    
    reader.ReadBytes(6)
    PcKeyFor0819 = reader.ReadBytes(16)

    reader.ReadBytes(4)
    PcToken0038From0818 = reader.ReadBytes(reader.ReadShort())

    reader.ReadBytes(4)
    PcQrcodeToken = reader.ReadBytes(reader.ReadShort())

    reader.ReadBytes(4)
    with open("QrCode.jpg","wb") as f:
        f.write(reader.ReadBytes(reader.ReadShort()))
    
    if platform.system() == "Windows":
        log.Println("登录二维码获取成功，已保存至"+os.getcwd()+"\\QrCode.jpg")
        os.startfile("QrCode.jpg")
    elif platform.system() == "Linux":
        log.Println("登录二维码获取成功，已保存至"+os.getcwd()+"/QrCode.jpg")
        try:
            utils.Print_QrCode(os.getcwd()+"/QrCode.jpg")
        except:
            log.Fatalln("输出登录二维码失败，请安装pillow库或自行想办法打开本地图片扫码")
    else:
        log.Println("登录二维码获取成功，已保存至程序运行路径下，请自行扫码登录")

    for _ in range(60):
        # 发送0819协议包探寻二维码状态
        writer.WriteBytes(binary.TLV_0019_Ping())
        writer.WriteBytes(binary.TLV_0114_DHParams())
        writer.WriteHex("03 01 00 22")
        writer.WriteShort(len(PcQrcodeToken))
        writer.WriteBytes(PcQrcodeToken)
        body = writer.ReadAll()
        
        writer.WriteBytes(const.Header)
        writer.WriteHex("08 19")
        writer.WriteBytes(utils.GetRandomBin(2))
        writer.WriteHex("00 00 00 00 03 00 00 00 01 01 01 00 00 67 B7 00 00 00 00 00 30 00 3A")
        writer.WriteShort(len(PcToken0038From0818))
        writer.WriteBytes(PcToken0038From0818)
        writer.WriteBytes(binary.TeaEncrypt(body, PcKeyFor0819))
        writer.WriteBytes(const.Tail)

        QQ.Send(writer.ReadAll())

        # 解析0819响应包获取二维码状态
        body = QQ.Recv()
        reader.Update(binary.TeaDecrypt(body[16:-1], PcKeyFor0819))
        state = reader.ReadByte()

        if QQ.LongQQ == 0 and state == 0x01:
            QQ.BinQQ = body[9:13]
            QQ.LongQQ = int.from_bytes(QQ.BinQQ,byteorder='big',signed=False)
            log.Println(f"账号 {QQ.LongQQ} 已扫码，请在手机上确认登录")
        elif state == 0x00:
            
            reader.ReadBytes(2)
            QQ.PassWord = reader.ReadBytes(reader.ReadShort())

            reader.ReadBytes(2)
            QQ.TgtKey = reader.ReadBytes(reader.ReadShort())

            os.remove("QrCode.jpg")
            log.Println(f"账号 {QQ.LongQQ} 已确认登录，正在登录中......")
            return 
        
        time.sleep(1)
    
    os.remove("QrCode.jpg")
    log.Panicln("扫码超时，请重新运行此程序并扫码登录！")

def LoginValidate(QQ):
    '''登录验证'''
    global PcToken0038From0825, PcToken0038From0836, PcToken0088From0836, RedirectionTimes, PcKeyFor0828Send, PcKeyFor0828Recv
    # 发送0836协议包进行登录验证
    writer = binary.Writer()
    
    writer.WriteBytes(binary.TLV_0112_SigIP2(PcToken0038From0825))
    writer.WriteBytes(binary.TLV_030F_ComputerName("DawnNights-PCQQ"))
    writer.WriteBytes(binary.TLV_0005_Uin(QQ.BinQQ))

    if QQ.IsScanCode:
        writer.WriteBytes(binary.TLV_0303_UnknownTag(QQ.PassWord))
    else:
        pass

    writer.WriteBytes(binary.TLV_0015_ComputerGuid())
    writer.WriteBytes(binary.TLV_001A_GTKeyTGTGTCryptedData(QQ.TgtKey))
    writer.WriteBytes(binary.TLV_0018_Ping(QQ.BinQQ, RedirectionTimes))
        
    writer.WriteBytes(binary.TLV_0103_SID())

    writer.WriteBytes(binary.TLV_0312_Misc_Flag())
    writer.WriteBytes(binary.TLV_0508_UnknownTag())
    writer.WriteBytes(binary.TLV_0313_GUID_Ex())
    writer.WriteBytes(binary.TLV_0102_Official(PcToken0038From0825))
    body = binary.TeaEncrypt(writer.ReadAll(), const.ShareKey)

    
    '''
    pack.SetHex("02 36 39")
        pack.SetHex("08 36")
        pack.SetBin(util.GetRandomBin(2))
        pack.SetBin(self.QQ.BinQQ)
        pack.SetHex("03 00 00 00 01 01 01 00 00 67 B7 00 00 00 00 00 01")
        pack.SetHex("01 02")

        pack.SetShort(len(self.QQ.PublicKey))
        pack.SetBin(self.QQ.PublicKey)
        pack.SetHex("00 00 00 10")
        pack.SetBin(self.QQ.RandHead16)
        pack.SetBin(data)
        pack.SetHex("03")
        data = pack.GetAll()
    '''

    QQ.Send(QQ.Pack(
        cmd="08 36",
        body=len(const.PublicKey).to_bytes(2,"big")+const.PublicKey+utils.Hex2Bin("00 00 00 10")+const.RandHead16+body,
        version=const.StructVersion + utils.Hex2Bin("00 01 01 02"),
    ))
    
    # 判断是否成功接包
    body = QQ.Recv()
    if body == b'':
        log.Panicln("登录验证失败，可能是您的设备开启了登录保护，请在手机QQ的[设置]->[账号安全]->[登录设备管理]中关闭[登录保护]选项")

    # 解析0836响应包获取验证状态
    reader = binary.Reader(binary.TeaDecrypt(binary.TeaDecrypt(body[16:-1], const.ShareKey), QQ.TgtKey))
    
    sign = reader.ReadByte()
    if sign == 0x00:
        for _ in range(5):
            tlvName = utils.Bin2HexTo(reader.ReadBytes(2))
            tlvLength = reader.ReadShort()

            if tlvName == "1 9":
                reader.ReadBytes(2)
                PcKeyFor0828Send = reader.ReadBytes(16)

                PcToken0038From0836 = reader.ReadBytes(reader.ReadShort())
                
                reader.ReadBytes(reader.ReadShort())
                reader.ReadBytes(2)
            elif tlvName == "1 8":
                reader.ReadBytes(8)
                QQ.NickName = reader.ReadBytes(reader.ReadByte()).decode()
            elif tlvName == "1 7":
                reader.ReadBytes(26)
                PcKeyFor0828Recv = reader.ReadBytes(16)

                PcToken0088From0836 = reader.ReadBytes(reader.ReadShort())
                reader.ReadBytes(tlvLength-180)
            else:
                reader.ReadBytes(tlvLength)
    elif sign == 0x33:
        log.Panicln(f"账号 {QQ.LongQQ} 冻结或被回收")
    elif sign == 0x34:
        log.Panicln(f"账号 {QQ.LongQQ} 密码校验失败，请重写填写密码")
    elif sign == 0x3F:
        log.Panicln(f"账号 {QQ.LongQQ} 需要验证密保或开启了设备锁，请关闭设备锁或使用扫码登录")
    elif sign == 0x3F:
        log.Panicln(f"账号 {QQ.LongQQ} 登录需要验证码")
    else:
        log.Panicln(f"账号 {QQ.LongQQ} 登录发生未知错误")

def WriteToken(QQ):
    '''保存登录token'''
    global PcToken0038From0836, PcToken0088From0836, PcKeyFor0828Send, PcKeyFor0828Recv
    with open("token.bin", "wb") as f:
        f.write(b'DawnNights'.join([
            PcToken0038From0836, 
            PcToken0088From0836, 
            PcKeyFor0828Send, 
            PcKeyFor0828Recv, 
            QQ.BinQQ, 
            QQ.SeverIp, 
            QQ.NickName.encode()
        ]))

def ReadToken(QQ):
    '''读取登录Token'''
    global PcToken0038From0836, PcToken0088From0836, PcKeyFor0828Send, PcKeyFor0828Recv
    with open("token.bin", "rb") as f:
        bin = f.read()
    PcToken0038From0836, PcToken0088From0836, \
    PcKeyFor0828Send, PcKeyFor0828Recv, \
    QQ.BinQQ, QQ.SeverIp, QQ.NickName = bin.split(b'DawnNights')

    QQ.NickName = QQ.NickName.decode()
    QQ.LongQQ = int.from_bytes(QQ.BinQQ,byteorder='big',signed=False)

def ApplySession(QQ):
    '''申请会话密匙'''
    global PcToken0038From0836, PcToken0088From0836, PcKeyFor0828Send, PcKeyFor0828Recv, RedirectionTimes
    
    # 发送0828协议包申请SessionKey
    writer = binary.Writer()

    writer.WriteBytes(binary.TLV_0007_TGT(PcToken0088From0836))
    writer.WriteBytes(binary.TLV_000C_PingRedirect(QQ.SeverIp))
    writer.WriteBytes(binary.TLV_0015_ComputerGuid())
    writer.WriteBytes(binary.TLV_0036_LoginReason())
    writer.WriteBytes(binary.TLV_0018_Ping(QQ.BinQQ, RedirectionTimes))
    writer.WriteBytes(binary.TLV_001F_DeviceID())
    writer.WriteBytes(binary.TLV_0105_m_vec0x12c())
    writer.WriteBytes(binary.TLV_010B_QDLoginFlag())
    writer.WriteBytes(binary.TLV_002D_LocalIP())

    QQ.Send(QQ.Pack(
        cmd="08 28",
        body=PcToken0038From0836+binary.TeaEncrypt(writer.ReadAll(), PcKeyFor0828Send),
        version=const.BodyVersion+utils.Hex2Bin("00 30 00 3A 00 38"),
    ))
    
    # 解析0828响应包获取SessionKey
    reader = binary.Reader(binary.TeaDecrypt(QQ.Recv()[16:-1], PcKeyFor0828Recv))
    reader.ReadBytes(63)
    QQ.SessionKey = reader.ReadBytes(16)

def SetOnline(QQ)->bool:
    # 发送00EC协议包置上线
    writer = binary.Writer()

    writer.WriteHex("01 00")
    writer.WriteHex("0A")   # 上线
    writer.WriteHex("00 01 00 01 00 04 00 00 00 00")

    QQ.Send(QQ.Pack(
        cmd="00 EC",
        body=writer.ReadAll(),
        version=const.BodyVersion,
    ))

    log.Println(f"账号 {QQ.LongQQ} 登录成功，欢迎尊敬的用户【{QQ.NickName}】使用本协议库")

def LoginByScanCode(QQ):
    '''通过扫码登录'''
    SeekServer(QQ, False)   # 第一次探寻服务器
    if os.path.exists("token.bin"):
        ReadToken(QQ=QQ)    # 置入本地扫码令牌
    else:
        ApplyScanCode(QQ)  # 申请扫码登录
        SeekServer(QQ, True)   # 第二次探寻服务器
        LoginValidate(QQ)  # 验证登录状态
        WriteToken(QQ=QQ)

    ApplySession(QQ)    # 申请操作密匙
    SetOnline(QQ)   # 置上线状态