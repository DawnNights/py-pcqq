import os
import time
import platform
import subprocess

import pcqq.network as net
import pcqq.utils as utils
import pcqq.const as const
import pcqq.logger as logger
import pcqq.binary as binary


def say_hello(is_logging: bool):
    # 0825包 一切的开始  均衡负载
    # 发这个包就问候服务器 Say Hello 判断是否能链接服务器
    writer = binary.Writer()

    writer.write(binary.tlv018(net.uin, net.redirection_times))
    if is_logging:
        writer.write(binary.tlv309(
            net.server_ip,
            net.redirection_history,
            net.redirection_times
        ))
        writer.write(binary.tlv036())
    else:
        writer.write_hex("00 04 00 0C 00 00 00 08 71 72 5F 6C 6F 67 69 6E")
        writer.write(binary.tlv309(
            net.server_ip,
            net.redirection_history,
            net.redirection_times
        ))
        writer.write(binary.tlv114())

    tea = binary.QQTea(bytes.fromhex(const.RANDKEY))
    net.send_packet(
        "08 25",
        const.STRUCT_VERSION,
        bytes.fromhex(const.RANDKEY),
        tea.encrypt(writer.clear())
    )

    data = net.cli.recv()
    reader = binary.Reader(
        tea.decrypt(data[14:-1])
    )

    sign = reader.read_byte()
    reader.read(2)
    net.token_0038_from_0825 = reader.read(reader.read_int16())
    reader.read(6)
    net.login_time = reader.read(4)
    net.local_ip = reader.read(4)
    reader.read(2)

    if sign == 0xfe:
        reader.read(18)
        net.server_ip = reader.read(4)
        net.redirection_times += 1
        net.redirection_history += net.server_ip
    elif sign == 0x00:
        reader.read(6)
        net.server_ip = reader.read(4)
        net.redirection_history = b''


def apply_qrcode():
    # 0818包 选用扫码登录 向服务器申请登录二维码
    writer = binary.Writer()

    writer.write_hex("00 19 00 10 00 01 00 00 04 4C 00 00 00")
    writer.write_hex("01 00 00 15 51 00 00 01 14 00 1D 01 02")
    writer.write_int16(len(bytes.fromhex(const.PUBLICKEY)))
    writer.write(bytes.fromhex(const.PUBLICKEY))
    writer.write_hex("03 05 00 1E 00 00 00 00 00 00 00")
    writer.write_hex("05 00 00 00 04 00 00 00 00 00 00 00")
    writer.write_hex("48 00 00 00 02 00 00 00 02 00 00")

    tea = binary.QQTea(bytes.fromhex(const.RANDKEY))
    net.send_packet(
        "08 18",
        const.STRUCT_VERSION,
        bytes.fromhex(const.RANDKEY),
        tea.encrypt(writer.clear())
    )

    data = net.cli.recv()
    tea.key = bytes.fromhex(const.SHAREKEY)
    reader = binary.Reader(
        tea.decrypt(data[14:-1])
    )

    if reader.read_byte() != 0x00:
        logger.fatal("ERROR: 登录二维码获取失败，请尝试重新运行")

    reader.read(6)
    net.pckey_for_0819 = reader.read(16)
    reader.read(4)
    net.token_0038_from_0818 = reader.read(reader.read_int16())
    reader.read(4)
    net.token_by_scancode = reader.read(reader.read_int16())
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


def check_scan_state():
    # 0819包 监听当前扫码状态
    writer = binary.Writer()

    writer.write(binary.tlv019())
    writer.write(binary.tlv114())
    writer.write_hex("03 01 00 22")
    writer.write_int16(len(net.token_by_scancode))
    writer.write(net.token_by_scancode)

    tea = binary.QQTea(net.pckey_for_0819)
    net.send_packet(
        "08 19",
        const.STRUCT_VERSION + "00 30 00 3A",
        len(net.token_0038_from_0818).to_bytes(2, 'big'),
        net.token_0038_from_0818,
        tea.encrypt(writer.clear())
    )

    data = net.cli.recv()
    reader = binary.Reader(
        tea.decrypt(data[14:-1])
    )
    state = reader.read_byte()

    if state == 0x01:
        user_id = int.from_bytes(data[7:11], 'big')
        logger.info(f'账号 {user_id} 已扫码，请在手机上确认登录')
    elif state == 0x00:
        net.uin = int.from_bytes(data[7:11], 'big')

        reader.read(2)
        net.password = reader.read(reader.read_int16())
        reader.read(2)
        net.tgt_key = reader.read(reader.read_int16())

        os.remove('QrCode.jpg')
        logger.info(f'账号 {net.uin} 已在手机上确认登录，尝试登录中...')
        return True
    return False


def login_validate():
    # 0836包 登录验证/账密验证
    writer = binary.Writer()

    writer.write(binary.tlv112(net.token_0038_from_0825))
    writer.write(binary.tlv30f())
    writer.write(binary.tlv005(net.uin))

    if net.is_scancode:
        writer.write(binary.tlv303(net.password))
    else:
        writer.write(binary.tlv006(
            uin=net.uin,
            tgtgt_key=net.tgt_key,
            md5_once=net.password,
            md5_twice=utils.hashmd5(
                net.password +
                bytes(4) +
                net.uin.to_bytes(4, "big")
            ),
            login_time=net.login_time,
            local_ip=net.local_ip,
            computer_id=utils.hashmd5(
                f'{net.uin}ComputerID'.encode()
            ),
            tgtgt=net.tgtgt_key
        ))

    writer.write(binary.tlv015())
    writer.write(binary.tlv01a(net.tgt_key))
    writer.write(binary.tlv018(net.uin, net.redirection_times))
    writer.write(binary.tlv103())
    writer.write(binary.tlv312())
    writer.write(binary.tlv508())
    writer.write(binary.tlv313())
    writer.write(binary.tlv102(net.token_0038_from_0825))

    tea = binary.QQTea(bytes.fromhex(const.SHAREKEY))
    net.send_packet(
        "08 36",
        const.STRUCT_VERSION + "00 01 01 02",
        len(bytes.fromhex(const.PUBLICKEY)).to_bytes(2, 'big'),
        bytes.fromhex(const.PUBLICKEY),
        bytes.fromhex("00 00 00 10"),
        bytes.fromhex(const.RANDKEY),
        tea.encrypt(writer.clear())
    )

    data = net.cli.recv()
    if data == b'':
        logger.fatal("ERROR: "+"，".join([
            "登录验证失败",
            "可能是您的设备开启了登录保护",
            "请在手机QQ的[设置]->[账号安全]->[登录设备管理]中关闭[登录保护]选项"
        ]))

    try:
        data = tea.decrypt(data[14:-1])
        tea.key = net.tgt_key
        reader = binary.Reader(tea.decrypt(data))
    except:
        logger.fatal("ERROR: 登录失败，请尝试重启或使用扫码登录")

    sign = reader.read_byte()
    if sign == 0x00:
        for _ in range(5):
            reader.read_byte()

            binary.tlv_id = reader.read_byte()
            binary.tlv_size = reader.read_int16()

            if binary.tlv_id == 9:
                reader.read(2)
                net.pckey_for_0828_send = reader.read(16)

                net.token_0038_from_0836 = reader.read(
                    reader.read_int16())

                reader.read(reader.read_int16())
                reader.read(2)
            elif binary.tlv_id == 8:
                reader.read(8)
                net.nickname = reader.read(reader.read_byte()).decode()
            elif binary.tlv_id == 7:
                reader.read(26)
                net.pckey_for_0828_recv = reader.read(16)

                net.token_0088_from_0836 = reader.read(
                    reader.read_int16())
                reader.read(binary.tlv_size - 180)
            else:
                reader.read(binary.tlv_size)
    elif sign == 0x01:
        reader.read(2)
        net.tgt_key = reader.read(reader.read_int16())
        reader.read(2)
        net.tgtgt_key = reader.read(reader.read_int16())

        tea.key = utils.hashmd5(
            net.password +
            bytes(4) +
            net.uin.to_bytes(4, "big")
        )
        net.tgtgt_key = tea.decrypt(net.tgtgt_key)

        login_validate()
    else:
        logger.fatal(f"ERROR: 登录失败，错误码{hex(sign)}，请尝试重新运行或使用扫码登录")


def open_session():
    # 0828包 申请SessionKey来操作会话
    writer = binary.Writer()

    writer.write(binary.tlv007(net.token_0088_from_0836))
    writer.write(binary.tlv00c(net.server_ip))
    writer.write(binary.tlv015())
    writer.write(binary.tlv036())
    writer.write(binary.tlv018(net.uin, net.redirection_times))
    writer.write(binary.tlv01f())
    writer.write(binary.tlv105())
    writer.write(binary.tlv10b())
    writer.write(binary.tlv02d())

    tea = binary.QQTea(net.pckey_for_0828_send)
    net.send_packet(
        "08 28",
        const.BODY_VERSION + "00 30 00 3A 00 38",
        net.token_0038_from_0836,
        tea.encrypt(writer.clear())
    )

    data = net.cli.recv()
    tea.key = net.pckey_for_0828_recv
    reader = binary.Reader(tea.decrypt(data[14:-1]))
    reader.read(63)
    net.session_key = reader.read(16)
    net.tea = binary.QQTea(net.session_key)


def set_online(state: int):
    # 00EC包 设置QQ状态
    writer = binary.Writer()

    writer.write_hex("01 00")
    writer.write_byte(state)
    writer.write_hex("00 01 00 01 00 04 00 00 00 00")

    net.send_packet(
        "00 EC",
        const.BODY_VERSION,
        writer.clear()
    )
    net.cli.recv()
    logger.info(f"账号 {net.uin} 已上线，欢迎用户 {net.nickname} 使用本协议库")


def login_out():
    # 0062包 注销当前登录
    logger.info(f"账号 {net.uin} 已退出登录，欢迎用户 {net.nickname} 下次使用本协议库")
    net.send_packet(
        "00 62",
        const.BODY_VERSION,
        bytes(16)
    )


def keep_heatbeat():
    # 0058包 与服务端保持心跳
    while True:
        net.send_packet(
            "00 58",
            const.BODY_VERSION,
            bytes.fromhex("00 01 00 01")
        )
        time.sleep(40)


def refresh_skey():
    # 001D包 获取网络操作用的skey
    net.send_packet(
        "00 1D",
        const.BODY_VERSION,
        b'3\x00\x06\x00\x08t.qq.com\x00\nqun.qq.com\x00\x0cqzone.qq.com\x00\x0cjubao.qq.com\x00\tke.qq.com\x00\ntenpay.com'
    )

    data = net.cli.recv()
    reader = binary.Reader(
        net.tea.decrypt(data[14:-1])
    )

    reader.read(2)
    net.skey = reader.read(reader.read_int16()).decode()
    net.bkn = utils.gtk_skey(net.skey)
    net.httper = utils.Httper("uin=o%d; skey=%s" % (net.uin, net.skey))
