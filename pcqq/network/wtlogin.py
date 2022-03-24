import os
import asyncio
import platform
import subprocess

import pcqq.client as cli
import pcqq.utils as utils
import pcqq.const as const
import pcqq.logger as logger
import pcqq.binary as binary
#cli = cli.QQClient()


async def ping_server(is_logging: bool):
    """
    0825包 一切的开始  均衡负载

    发这个包就问候服务器 Say Hello 判断是否能链接服务器
    """
    writer = binary.Writer()

    writer.write(binary.tlv018(cli.uin, cli.redirection_times))
    if is_logging:
        writer.write(binary.tlv309(
            cli.server_ip,
            cli.redirection_history,
            cli.redirection_times
        ))
        writer.write(binary.tlv036())
    else:
        writer.write(binary.tlv004())
        writer.write(binary.tlv309(
            cli.server_ip,
            cli.redirection_history,
            cli.redirection_times
        ))
        writer.write(binary.tlv114())

    tea = binary.QQTea(bytes.fromhex(const.RANDKEY))
    await cli.write_packet(
        "08 25",
        const.STRUCT_VERSION,
        bytes.fromhex(const.RANDKEY) +
        tea.encrypt(writer.clear())
    )

    _, _, _, body = await cli.read_packet()
    reader = binary.Reader(tea.decrypt(body))

    sign = reader.read_byte()
    reader.read(2)
    cli.token_0038_from_0825 = reader.read(reader.read_int16())
    reader.read(6)
    cli.login_time = reader.read(4)
    cli.local_ip = reader.read(4)
    reader.read(2)

    if sign == 0xfe:
        reader.read(18)
        cli.server_ip = reader.read(4)
        cli.redirection_times += 1
        cli.redirection_history += cli.server_ip
    elif sign == 0x00:
        reader.read(6)
        cli.server_ip = reader.read(4)
        cli.redirection_history = b''


async def fetch_qrcode():
    """
    0818包 向服务器申请登录二维码

    发这个包就代表需要使用手机扫描二维码登录
    """
    writer = binary.Writer()

    writer.write(binary.tlv019())
    writer.write(binary.tlv114())
    writer.write(binary.tlv305())

    tea = binary.QQTea(bytes.fromhex(const.RANDKEY))
    await cli.write_packet(
        "08 18",
        const.STRUCT_VERSION,
        bytes.fromhex(const.RANDKEY) +
        tea.encrypt(writer.clear())
    )

    _, _, _, body = await cli.read_packet()
    tea.key = bytes.fromhex(const.SHAREKEY)
    reader = binary.Reader(tea.decrypt(body))

    if reader.read_byte() != 0x00:
        logger.fatal("ERROR: 登录二维码获取失败，请尝试重新运行")

    reader.read(6)
    cli.pckey_for_0819 = reader.read(16)
    reader.read(4)
    cli.token_0038_from_0818 = reader.read(reader.read_int16())
    reader.read(4)
    cli.token_by_scancode = reader.read(reader.read_int16())
    reader.read(4)

    path = os.path.join(os.getcwd(), 'QrCode.jpg')
    with open(path, mode="wb") as f:
        f.write(reader.read(reader.read_int16()))
        logger.info('登录二维码获取成功，已保存至' + path)

    system = platform.system()
    try:
        # 用系统默认程序打开图片文件
        if system == "Windows":
            os.startfile(path)
        elif system == "Linux":
            subprocess.call(["xdg-open", path])
        else:
            subprocess.call(["open", path])
    except:
        # 使用pillow库在终端上打印二维码图片
        utils.print_qrcode(path, const.QRCODE_SIZE)


async def check_qrcode():
    """
    0819包 检查当前扫码状态
    """
    writer = binary.Writer()

    writer.write(binary.tlv019())
    writer.write(binary.tlv114())
    writer.write_hex("03 01 00 22")
    writer.write_int16(len(cli.token_by_scancode))
    writer.write(cli.token_by_scancode)

    tea = binary.QQTea(cli.pckey_for_0819)
    await cli.write_packet(
        "08 19",
        const.STRUCT_VERSION + "00 30 00 3A",
        len(cli.token_0038_from_0818).to_bytes(2, 'big') +
        cli.token_0038_from_0818 +
        tea.encrypt(writer.clear())
    )

    _, _, uin, body = await cli.read_packet()
    reader = binary.Reader(tea.decrypt(body))
    state = reader.read_byte()

    if state == 0x01:
        logger.info(f'账号 {uin} 已扫码，请在手机上确认登录')
    elif state == 0x00:
        cli.uin = uin

        reader.read(2)
        cli.password = reader.read(reader.read_int16())
        reader.read(2)
        cli.tgt_key = reader.read(reader.read_int16())

        os.remove('QrCode.jpg')
        logger.info(f'账号 {cli.uin} 已在手机上确认登录，尝试登录中...')
        return True
    return False


async def check_login():
    """
    0836包 登录验证/账密验证
    """
    writer = binary.Writer()

    writer.write(binary.tlv112(cli.token_0038_from_0825))
    writer.write(binary.tlv30f())
    writer.write(binary.tlv005(cli.uin))

    if cli.is_scancode:
        writer.write(binary.tlv303(cli.password))
    else:
        writer.write(binary.tlv006(
            uin=cli.uin,
            tgt_key=cli.tgt_key,
            md5_once=cli.password,
            md5_twice=utils.hashmd5(
                cli.password +
                bytes(4) +
                cli.uin.to_bytes(4, "big")
            ),
            login_time=cli.login_time,
            local_ip=cli.local_ip,
            computer_id=utils.hashmd5(
                f'{cli.uin}ComputerID'.encode()
            ),
            tgtgt=cli.tgtgt_key
        ))

    writer.write(binary.tlv015())
    writer.write(binary.tlv01a(cli.tgt_key))
    writer.write(binary.tlv018(cli.uin, cli.redirection_times))
    writer.write(binary.tlv103())
    writer.write(binary.tlv312())
    writer.write(binary.tlv508())
    writer.write(binary.tlv313())
    writer.write(binary.tlv102(cli.token_0038_from_0825))

    tea = binary.QQTea(bytes.fromhex(const.SHAREKEY))
    await cli.write_packet(
        "08 36",
        const.STRUCT_VERSION + "00 01 01 02",
        len(bytes.fromhex(const.PUBLICKEY)).to_bytes(2, 'big') +
        bytes.fromhex(const.PUBLICKEY) +
        bytes.fromhex("00 00 00 10") +
        bytes.fromhex(const.RANDKEY) +
        tea.encrypt(writer.clear())
    )

    try:
        _, _, _, body = await cli.read_packet()
    except:
        logger.fatal("ERROR: "+", ".join([
            "登录验证失败",
            "可能是您的设备开启了登录保护",
            "请在手机QQ的[设置]->[账号安全]->[登录设备管理]中关闭[登录保护]选项"
        ]))

    try:
        body = tea.decrypt(body)
        tea.key = cli.tgt_key
        reader = binary.Reader(tea.decrypt(body))
    except:
        logger.fatal("ERROR: 登录失败，请尝试重启程序或使用扫码登录")

    sign = reader.read_byte()
    if sign == 0x00:
        for _ in range(5):
            reader.read_byte()

            binary.tlv_id = reader.read_byte()
            binary.tlv_size = reader.read_int16()

            if binary.tlv_id == 9:
                reader.read(2)
                cli.pckey_for_0828_send = reader.read(16)

                cli.token_0038_from_0836 = reader.read(
                    reader.read_int16())

                reader.read(reader.read_int16())
                reader.read(2)
            elif binary.tlv_id == 8:
                reader.read(8)
                cli.nickname = reader.read(reader.read_byte()).decode()
            elif binary.tlv_id == 7:
                reader.read(26)
                cli.pckey_for_0828_recv = reader.read(16)

                cli.token_0088_from_0836 = reader.read(
                    reader.read_int16())
                reader.read(binary.tlv_size - 180)
            else:
                reader.read(binary.tlv_size)
    elif sign == 0x01:
        reader.read(2)
        cli.tgt_key = reader.read(reader.read_int16())
        reader.read(2)
        cli.tgtgt_key = reader.read(reader.read_int16())

        tea.key = utils.hashmd5(
            cli.password +
            bytes(4) +
            cli.uin.to_bytes(4, "big")
        )
        cli.tgtgt_key = tea.decrypt(cli.tgtgt_key)

        return await check_login()
    else:
        logger.fatal(f"ERROR: 登录失败，错误码{hex(sign)}，请尝试重新运行或使用扫码登录")


async def fetch_session():
    """
    0828包 申请SessionKey
    此包代表获取会话密钥来操作协议功能
    """
    writer = binary.Writer()

    writer.write(binary.tlv007(cli.token_0088_from_0836))
    writer.write(binary.tlv00c(cli.server_ip))
    writer.write(binary.tlv015())
    writer.write(binary.tlv036())
    writer.write(binary.tlv018(cli.uin, cli.redirection_times))
    writer.write(binary.tlv01f())
    writer.write(binary.tlv105())
    writer.write(binary.tlv10b())
    writer.write(binary.tlv02d(cli.local_ip))

    tea = binary.QQTea(cli.pckey_for_0828_send)
    await cli.write_packet(
        "08 28",
        const.BODY_VERSION + "00 30 00 3A 00 38",
        cli.token_0038_from_0836 +
        tea.encrypt(writer.clear())
    )

    _, _, _, body = await cli.read_packet()
    tea.key = cli.pckey_for_0828_recv
    reader = binary.Reader(tea.decrypt(body))
    reader.read(63)
    cli.session_key = reader.read(16)
    cli.teaer = binary.QQTea(cli.session_key)


async def set_online(state: int):
    """00EC包 设置QQ状态"""
    writer = binary.Writer()

    writer.write_hex("01 00")
    writer.write_byte(state)
    writer.write_hex("00 01")
    writer.write_hex("00 01")
    writer.write_hex("00 04")
    writer.write_hex("00 00 00 00")

    await cli.write_packet(
        "00 EC",
        const.BODY_VERSION,
        writer.clear()
    )
    await cli.read_packet()
    logger.info(f"账号 {cli.uin} 已上线，欢迎用户 {cli.nickname} 使用本协议库")


async def login_out():
    """0062包 注销当前登录"""
    await cli.write_packet(
        "00 62",
        const.BODY_VERSION,
        bytes(16)
    )
    logger.info(f"账号 {cli.uin} 已退出登录，欢迎用户 {cli.nickname} 下次使用本协议库")


async def heatbeat():
    """0058包 与服务端保持心跳"""
    await cli.write_packet(
        "00 58",
        const.BODY_VERSION,
        bytes.fromhex("00 01 00 01")
    )


async def fetch_skey():
    """001D包 获取网络操作用的skey"""
    writer = binary.Writer()

    writer.write_byte(51)
    writer.write_int16(6)   # 域名数量

    writer.write_int16(8)
    writer.write(b't.qq.com')

    writer.write_int16(10)
    writer.write(b'qun.qq.com')

    writer.write_int16(12)
    writer.write(b'qzone.qq.com')

    writer.write_int16(12)
    writer.write(b'jubao.qq.com')

    writer.write_int16(9)
    writer.write(b'ke.qq.com')

    writer.write_int16(10)
    writer.write(b'tenpay.com')

    await cli.write_packet(
        "00 1D",
        const.BODY_VERSION,
        writer.clear()
    )

    _, _, _, body = await cli.read_packet()
    reader = binary.Reader(body)

    reader.read(2)
    cli.skey = reader.read(reader.read_int16()).decode()
    cli.bkn = utils.gtk_skey(cli.skey)
    cli.cookie = "uin=o%d; skey=%s" % (cli.uin, cli.skey)

async def qrcode_login():
    """通过手机扫码登录QQ"""
    cli.is_scancode = True
    await ping_server(False)  # 请求登录服务器
    await fetch_qrcode()    # 获取登录二维码

    # 循环检测扫码状态
    while not await check_qrcode():
        await asyncio.sleep(1.0)
    
    await check_login() # 验证登录
    await fetch_session()   # 申请会话操作密钥
    await set_online(const.STATE_ONLINE)    # 设置状态为在线
    await fetch_skey()    # 申请网络操作密钥

    cli.save_token(os.path.join(os.getcwd(), "session.token"))

async def password_login(user_id:int, password:str):
    """通过账号密码登录QQ"""
    cli.uin = user_id
    cli.password = utils.hashmd5(password.encode())

    await ping_server(False)  # 请求登录服务器
    await check_login() # 账密登录
    await fetch_session()   # 申请会话操作密钥
    await set_online(const.STATE_ONLINE)    # 设置状态为在线
    await fetch_skey()    # 申请网络操作密钥

    cli.save_token(os.path.join(os.getcwd(), "session.token"))

async def token_login():
    """通过本地token申请重连"""
    await ping_server(False)  # 请求登录服务器

    cli.load_token(os.path.join(os.getcwd(), "session.token"))
    await ping_server(False)  # 重新请求登录服务器
    
    try:
        await fetch_session() # 验证登录
    except:
        os.remove(os.path.join(os.getcwd(), "session.token"))
        logger.fatal("ERROR: 本地Token已失效，请重新登录")
    
    await set_online(const.STATE_ONLINE)    # 设置状态为在线
    await fetch_skey()    # 申请网络操作密钥