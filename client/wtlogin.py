from .__builder import *

def SetOnline(QQ: QQClient):
    writer = binary.Writer()
    writer.WriteHex('01 00')
    writer.WriteHex('0A')  # 0A: 上线
    writer.WriteHex('00 01 00 01 00 04 00 00 00 00')

    QQ.Send(QQ.Pack(
        '00 EC',
        const.BODY_VERSION,
        writer.ReadAll(),
    ))

    log.Println(f'账号 {QQ.LongQQ} 已上线，欢迎用户 {QQ.NickName} 使用本协议库\n')


def LoginByToken(QQ: QQClient):
    Handle_0825_Packet(QQ=QQ, logging=False)
    ReadToken(QQ=QQ)

    QQ.NickName = QQ.NickName.decode()
    QQ.LongQQ = int.from_bytes(QQ.BinQQ, byteorder='big', signed=False)

    try:
        Handle_0825_Packet(QQ=QQ, logging=False)
        Handle_0828_Packet(QQ=QQ)
        SetOnline(QQ=QQ)
    except Exception as err:
        os.remove('session.token')
        log.Fatalln('session.token 已失效，请重新登录获取token')


def LoginByPassword(QQ: QQClient, Uin: int, Password: str):
    QQ.LongQQ = Uin
    QQ.IsScanCode = False
    QQ.BinQQ = Uin.to_bytes(4, 'big')
    QQ.PassWord = utils.HashMD5(Password.encode())

    Handle_0825_Packet(QQ=QQ, logging=False)
    Handle_0836_Packet(QQ=QQ)
    Handle_0828_Packet(QQ=QQ)

    SaveToken(QQ=QQ)
    SetOnline(QQ=QQ)


def LoginByScancode(QQ: QQClient):
    Handle_0825_Packet(QQ=QQ, logging=False)
    Handle_0818_Packet(QQ=QQ)

    from time import sleep
    for _ in range(60):
        adopt = Handle_0819_Packet(QQ=QQ)
        if adopt:
            break
        sleep(1.0)
    if not adopt:
        log.Fatalln("扫码等待超时，请重新运行程序登录")

    Handle_0825_Packet(QQ=QQ, logging=True)
    Handle_0836_Packet(QQ=QQ)
    Handle_0828_Packet(QQ=QQ)

    SaveToken(QQ=QQ)
    SetOnline(QQ=QQ)