import os
import pcqq.log as log
import pcqq.const as const

import pcqq.utils as utils
import pcqq.binary as binary

from .client import QQClient

from .__qqtlv import TLV_0112_SigIP2, TLV_030F_ComputerName, TLV_0005_Uin, TLV_0303_UnknownTag, TLV_0015_ComputerGuid, \
    TLV_001A_GTKeyTGTGTCryptedData, TLV_0018_Ping, TLV_0019_Ping, TLV_0114_DHParams, TLV_0103_SID, TLV_0312_Misc_Flag, \
    TLV_0508_UnknownTag, TLV_0313_GUID_Ex, TLV_0102_Official, TLV_0309_Ping_Strategy, TLV_0036_LoginReason, TLV_0007_TGT, \
    TLV_000C_PingRedirect, TLV_001F_DeviceID, TLV_0105_m_vec0x12c, TLV_010B_QDLoginFlag, TLV_002D_LocalIP, TLV_0006_TGTGT

System = __import__('platform').system()
LocalIp = b''
ConnectTime = b''

RedirectionTimes = 0  # 重定向次数
RedirectionHistory = ''  # 重定向历史

PcKeyFor0819 = bytes()
PcQrcodeToken = bytes()
PcToken0038From0818 = bytes()

PcToken0038From0825 = b''  # 0038令牌
PcToken0038From0836 = b''  # 0038令牌
PcToken0088From0836 = b''  # 0088令牌

PcKeyTGT = utils.GetRandomBin(16)  # TGT密匙
PcKeyTGTGT = b''  # TGTGT密匙

PcKeyFor0828Send = b''  # 0828协议包send密匙
PcKeyFor0828Recv = b''  # 0828协议包recv密匙


def Handle_0825_Packet(QQ: QQClient, logging: bool):
    global RedirectionTimes, RedirectionHistory, PcToken0038From0825, LocalIp, ConnectTime

    # 发送0825协议包探寻服务器
    writer = binary.Writer()

    writer.WriteBytes(TLV_0018_Ping(QQ.BinQQ, RedirectionTimes))
    if logging:
        writer.WriteBytes(
            TLV_0309_Ping_Strategy(QQ.ServerIP, RedirectionHistory,
                                   RedirectionTimes))
        writer.WriteBytes(TLV_0036_LoginReason())
    else:
        writer.WriteHex('00 04 00 0C 00 00 00 08 71 72 5F 6C 6F 67 69 6E')
        writer.WriteBytes(
            TLV_0309_Ping_Strategy(QQ.ServerIP, RedirectionHistory,
                                   RedirectionTimes))
    writer.WriteBytes(TLV_0114_DHParams())

    QQ.Send(
        QQ.Pack(
            '08 25',
            const.STRUCT_VERSION,
            const.RANDKEY,
            binary.TeaEncrypt(writer.ReadAll(), const.RANDKEY),
        ))

    # 解析0825响应包获取重定向信息
    reader = binary.Reader(binary.TeaDecrypt(QQ.Recv()[16:-1], const.RANDKEY))
    sign = reader.ReadByte()

    reader.ReadBytes(2)
    PcToken0038From0825 = reader.ReadBytes(reader.ReadShort())

    reader.ReadBytes(6)
    ConnectTime = reader.ReadBytes(4)
    LocalIp = reader.ReadBytes(4)

    reader.ReadBytes(2)
    if sign == 0xfe:
        reader.ReadBytes(18)
        QQ.ServerIP = reader.ReadBytes(4)
        RedirectionTimes += 1
        RedirectionHistory += hex(int.from_bytes(QQ.ServerIP, 'big'))[2:]
    elif sign == 0x00:
        reader.ReadBytes(6)
        QQ.ServerIP = reader.ReadBytes(4)
        RedirectionHistory = ''


def Handle_0818_Packet(QQ: QQClient):
    global PcKeyFor0819, PcToken0038From0818, PcQrcodeToken

    # 发送0818协议包请求登录二维码
    writer = binary.Writer()
    writer.WriteHex(
        '00 19 00 10 00 01 00 00 04 4C 00 00 00 01 00 00 15 51 00 00 01 14 00 1D 01 02'
    )
    writer.WriteShort(len(const.PUBLICKEY))
    writer.WriteBytes(const.PUBLICKEY)
    writer.WriteHex(
        '03 05 00 1E 00 00 00 00 00 00 00 05 00 00 00 04 00 00 00 00 00 00 00 48 00 00 00 02 00 00 00 02 00 00'
    )
    QQ.Send(
        QQ.Pack(
            '08 18',
            const.STRUCT_VERSION,
            const.RANDKEY,
            binary.TeaEncrypt(writer.ReadAll(), const.RANDKEY),
        ))

    # 解析0818响应包获取二维码数据
    reader = binary.Reader(binary.TeaDecrypt(QQ.Recv()[16:-1], const.SHAREKEY))
    if reader.ReadByte() != 0x00:
        log.Panicln('获取登录二维码失败')

    reader.ReadBytes(6)
    PcKeyFor0819 = reader.ReadBytes(16)

    reader.ReadBytes(4)
    PcToken0038From0818 = reader.ReadBytes(reader.ReadShort())

    reader.ReadBytes(4)
    PcQrcodeToken = reader.ReadBytes(reader.ReadShort())

    reader.ReadBytes(4)

    path = os.path.join(os.getcwd(), 'QrCode.jpg')
    with open(path, 'wb') as f:
        f.write(reader.ReadBytes(reader.ReadShort()))

    if System == 'Windows':
        log.Println('登录二维码获取成功，已保存至' + path)
        os.startfile('QrCode.jpg')
    elif System == 'Linux':
        log.Println('登录二维码获取成功，已保存至' + path)
        try:
            utils.DrawQrCode(path)
        except:
            log.Panicln('打印登录二维码失败，请安装pillow库或自行打开本地图片扫码')
    else:
        log.Println(f'登录二维码获取成功，已保存至{path}下，请自行扫码登录')


def Handle_0819_Packet(QQ: QQClient):
    global PcKeyFor0819, PcToken0038From0818, PcQrcodeToken, PcKeyTGT

    # 发送0819协议包获取扫码状态
    writer = binary.Writer()
    writer.WriteBytes(TLV_0019_Ping())
    writer.WriteBytes(TLV_0114_DHParams())
    writer.WriteHex('03 01 00 22')
    writer.WriteShort(len(PcQrcodeToken))
    writer.WriteBytes(PcQrcodeToken)

    QQ.Send(
        QQ.Pack('08 19', const.STRUCT_VERSION + utils.HexToBin('00 30 00 3A'),
                len(PcToken0038From0818).to_bytes(2, 'big'),
                PcToken0038From0818,
                binary.TeaEncrypt(writer.ReadAll(), PcKeyFor0819)))

    # 解析0819响应包获取二维码状态
    body = QQ.Recv()
    reader = binary.Reader(binary.TeaDecrypt(body[16:-1], PcKeyFor0819))
    state = reader.ReadByte()

    if QQ.LongQQ == 0 and state == 0x01:
        QQ.LongQQ = int.from_bytes(body[9:13], byteorder='big', signed=False)
        log.Println(f'账号 {QQ.LongQQ} 已扫码，请在手机上确认登录')
    elif state == 0x00:
        QQ.BinQQ = QQ.LongQQ.to_bytes(4, 'big')

        reader.ReadBytes(2)
        QQ.PassWord = reader.ReadBytes(reader.ReadShort())

        reader.ReadBytes(2)
        PcKeyTGT = reader.ReadBytes(reader.ReadShort())

        os.remove('QrCode.jpg')
        log.Println(f'账号 {QQ.LongQQ} 已确认登录，尝试登录中...')
        return True

    return False


def Handle_0836_Packet(QQ: QQClient):
    global PcToken0038From0825, PcToken0038From0836, PcToken0088From0836, \
        RedirectionTimes, PcKeyFor0828Send, PcKeyFor0828Recv, PcKeyTGT, PcKeyTGTGT

    # 发送0836协议包进行登录验证
    writer = binary.Writer()
    writer.WriteBytes(TLV_0112_SigIP2(PcToken0038From0825))
    writer.WriteBytes(TLV_030F_ComputerName('DawnNights-PCQQ'))
    writer.WriteBytes(TLV_0005_Uin(QQ.BinQQ))

    if QQ.IsScanCode:
        writer.WriteBytes(TLV_0303_UnknownTag(QQ.PassWord))
    else:
        writer.WriteBytes(
            TLV_0006_TGTGT(
                BinQQ=QQ.BinQQ,
                TGTGTKey=PcKeyTGT,
                Md5Once=QQ.PassWord,
                Md5Twice=utils.HashMD5(QQ.PassWord + bytes(4) + QQ.BinQQ),
                ConnTime=ConnectTime,
                LocalIP=LocalIp,
                ComputerID=utils.HashMD5(f'{QQ.LongQQ}ComputerID'.encode()),
                TGTGT=PcKeyTGTGT))

    writer.WriteBytes(TLV_0015_ComputerGuid())
    writer.WriteBytes(TLV_001A_GTKeyTGTGTCryptedData(PcKeyTGT))
    writer.WriteBytes(TLV_0018_Ping(QQ.BinQQ, RedirectionTimes))

    writer.WriteBytes(TLV_0103_SID())

    writer.WriteBytes(TLV_0312_Misc_Flag())
    writer.WriteBytes(TLV_0508_UnknownTag())
    writer.WriteBytes(TLV_0313_GUID_Ex())
    writer.WriteBytes(TLV_0102_Official(PcToken0038From0825))

    QQ.Send(
        QQ.Pack('08 36', const.STRUCT_VERSION + utils.HexToBin('00 01 01 02'),
                len(const.PUBLICKEY).to_bytes(2, 'big'), const.PUBLICKEY,
                utils.HexToBin('00 00 00 10'), const.RANDKEY,
                binary.TeaEncrypt(writer.ReadAll(), const.SHAREKEY)))

    # 判断是否成功接包
    body = QQ.Recv()
    if body == b'':
        log.Fatalln(
            '登录验证失败，可能是您的设备开启了登录保护，请在手机QQ的[设置]->[账号安全]->[登录设备管理]中关闭[登录保护]选项')

    # 解析0836响应包获取验证状态

    try:
        body = binary.TeaDecrypt(body[16:-1], const.SHAREKEY)
        body = binary.TeaDecrypt(body, PcKeyTGT)

        reader = binary.Reader(body)
        sign = reader.ReadByte()
    except:
        log.Fatalln('登录失败，请尝试使用扫码登录')

    if sign == 0x00:
        for _ in range(5):
            reader.ReadByte()

            tlvID = reader.ReadByte()
            tlvLen = reader.ReadShort()

            if tlvID == 9:
                reader.ReadBytes(2)
                PcKeyFor0828Send = reader.ReadBytes(16)

                PcToken0038From0836 = reader.ReadBytes(reader.ReadShort())

                reader.ReadBytes(reader.ReadShort())
                reader.ReadBytes(2)
            elif tlvID == 8:
                reader.ReadBytes(8)
                QQ.NickName = reader.ReadBytes(reader.ReadByte()).decode()
            elif tlvID == 7:
                reader.ReadBytes(26)
                PcKeyFor0828Recv = reader.ReadBytes(16)

                PcToken0088From0836 = reader.ReadBytes(reader.ReadShort())
                reader.ReadBytes(tlvLen - 180)
            else:
                reader.ReadBytes(tlvLen)
    elif sign == 0x01:
        reader.ReadBytes(2)
        PcKeyTGT = reader.ReadBytes(reader.ReadShort())

        reader.ReadBytes(2)
        PcKeyTGTGT = reader.ReadBytes(reader.ReadShort())
        PcKeyTGTGT = binary.TeaDecrypt(
            PcKeyTGTGT, utils.HashMD5(QQ.PassWord + bytes(4) + QQ.BinQQ))

        Handle_0836_Packet(QQ=QQ)

    else:
        log.Fatalln(f'登录失败，错误码{hex(sign)}，请尝试使用扫码登录')


def Handle_0828_Packet(QQ: QQClient):
    global PcToken0038From0836, PcToken0088From0836, PcKeyFor0828Send, PcKeyFor0828Recv, RedirectionTimes

    # 发送0828协议包申请SessionKey
    writer = binary.Writer()

    writer.WriteBytes(TLV_0007_TGT(PcToken0088From0836))
    writer.WriteBytes(TLV_000C_PingRedirect(QQ.ServerIP))
    writer.WriteBytes(TLV_0015_ComputerGuid())
    writer.WriteBytes(TLV_0036_LoginReason())
    writer.WriteBytes(TLV_0018_Ping(QQ.BinQQ, RedirectionTimes))
    writer.WriteBytes(TLV_001F_DeviceID())
    writer.WriteBytes(TLV_0105_m_vec0x12c())
    writer.WriteBytes(TLV_010B_QDLoginFlag())
    writer.WriteBytes(TLV_002D_LocalIP())

    QQ.Send(
        QQ.Pack(
            '08 28',
            const.BODY_VERSION + utils.HexToBin('00 30 00 3A 00 38'),
            PcToken0038From0836,
            binary.TeaEncrypt(writer.ReadAll(), PcKeyFor0828Send),
        ))

    # 解析0828响应包获取SessionKey
    reader = binary.Reader(
        binary.TeaDecrypt(QQ.Recv()[16:-1], PcKeyFor0828Recv))
    reader.ReadBytes(63)
    QQ.SessionKey = reader.ReadBytes(16)


def ReadToken(QQ: QQClient):
    '''读取登录Token'''
    global PcToken0038From0836, PcToken0088From0836, PcKeyFor0828Send, PcKeyFor0828Recv
    with open('session.token', 'rb') as f:
        PcToken0038From0836, PcToken0088From0836, \
            PcKeyFor0828Send, PcKeyFor0828Recv, \
            QQ.BinQQ, QQ.ServerIP, QQ.NickName = f.read().split(b'DawnNights')
    log.Println('Succeeded to read Token File: "session.token"')


def SaveToken(QQ: QQClient):
    '''存储登录Token'''
    global PcToken0038From0836, PcToken0088From0836, PcKeyFor0828Send, PcKeyFor0828Recv
    with open('session.token', 'wb') as f:
        f.write(b'DawnNights'.join([
            PcToken0038From0836, PcToken0088From0836, PcKeyFor0828Send,
            PcKeyFor0828Recv, QQ.BinQQ, QQ.ServerIP,
            QQ.NickName.encode()
        ]))
    log.Println('Succeeded to write Token File: "session.token"')
