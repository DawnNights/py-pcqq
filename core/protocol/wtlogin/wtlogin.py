import os
import sys
import asyncio

from logger import logger
from core.utils import Stream
from core import const
from core.client import QQClient

from .p1_0825_ping import pack_0825, unpack_0825
from .p2_0818_qrcode import pack_0818, unpack_0818
from .p3_0819_scan import pack_0819, unpack_0819
from .p4_0836_login import pack_0836, unpack_0836
from .p5_0828_session import pack_0828, unpack_0828
from .p6_00ec_online import pack_00ec, unpack_00ec
from .p7_001d_skey import pack_001d, unpack_001d
from .p8_0058_heartbeat import pack_0058, unpack_0058
from .p9_0062_login_out import pack_0062

def login_out(cli: QQClient):
    if not cli.stru.is_running:
        raise RuntimeError("当前客户端还未登录, 无法执行下线操作")
    
    cli.send(pack_0062(cli.stru))
    logger.info("已退出当前登录, 期待您的下次使用")    
    

async def login_by_scan(cli: QQClient):
    # ping 服务器
    cli.send(pack_0825(cli.stru))
    cli.manage.append(unpack_0825(cli.stru))
    await cli.recv_and_exec(const.RandKey)

    # 申请登录二维码
    cli.send(pack_0818(cli.stru))
    cli.manage.append(unpack_0818(cli.stru))
    await cli.recv_and_exec(cli.stru.ecdh.share_key)

    # 每两秒判断一次扫码结果
    while cli.stru.password == b'':
        await asyncio.sleep(2)
        
        cli.send(pack_0819(cli.stru))
        cli.manage.append(unpack_0819(cli.stru))
        await cli.recv_and_exec(cli.stru.pckey_for_0819)

    # 进行登录校验
    cli.send(pack_0836(cli.stru))
    cli.manage.append(unpack_0836(cli.stru))
    await cli.recv_and_exec(cli.stru.ecdh.share_key)

    # 申请会话密匙
    cli.send(pack_0828(cli.stru))
    cli.manage.append(unpack_0828(cli.stru))
    await cli.recv_and_exec(cli.stru.pckey_for_0828_recv)
    
    # 申请网络密匙
    cli.send(pack_001d(cli.stru))
    cli.manage.append(unpack_001d(cli.stru))
    await cli.recv_and_exec(cli.stru.session_key)

    # 置上线状态
    cli.send(pack_00ec(cli.stru))
    cli.manage.append(unpack_00ec(cli.stru))
    await cli.recv_and_exec(cli.stru.session_key)
    
    # 开启心跳循环
    async def heart_beat():
        cli.send(pack_0058(cli.stru))
        await asyncio.sleep(40)
        cli.add_task(heart_beat())
    cli.manage.append(unpack_0058(cli.stru))
    cli.add_task(heart_beat())

    # 写入 Token 用于二次登录
    path = os.path.join(cli.stru.path, "session.token")
    with open(path, "wb") as f:
        stream = Stream()

        stream.write_token(cli.stru.server_ip)
        stream.write_int32(cli.stru.uin)
        stream.write_token(cli.stru.nickname.encode())

        stream.write_token(cli.stru.token_0038_from_0836)
        stream.write_token(cli.stru.token_0088_from_0836)
        stream.write_token(cli.stru.pckey_for_0828_send)
        stream.write_token(cli.stru.pckey_for_0828_recv)
        f.write(stream.read_all())
        

    logger.info(f"已写入 Token 至 {path}, 下次登录无需再进行扫码")

async def login_by_token(cli: QQClient):
    # ping 服务器
    cli.send(pack_0825(cli.stru))
    cli.manage.append(unpack_0825(cli.stru))
    await cli.recv_and_exec(const.RandKey)
    
    # 读取 Token 用于二次登录
    path = os.path.join(cli.stru.path, "session.token")
    if not os.path.exists(path):
        logger.error(f"{path} 所指向的 Token 文件不存在, 请先使用扫码登录生成")
        sys.exit(0)
    
    with open(path, "rb") as f:
        stream = Stream(f.read())

        cli.stru.server_ip = stream.read_token()
        cli.stru.uin = stream.read_int32()
        cli.stru.nickname = stream.read_token().decode()
        cli.stru.token_0038_from_0836 = stream.read_token()
        cli.stru.token_0088_from_0836 = stream.read_token()
        cli.stru.pckey_for_0828_send = stream.read_token()
        cli.stru.pckey_for_0828_recv = stream.read_token()

    try:
        # 申请会话密匙
        cli.send(pack_0828(cli.stru))
        cli.manage.append(unpack_0828(cli.stru))
        
        coro = cli.recv_and_exec(cli.stru.pckey_for_0828_recv)
        await asyncio.wait_for(coro, timeout=10)
    except:
        os.remove(path)
        logger.error(f"本地Token已失效, 请重新运行程序使用扫码登录")
        sys.exit(0)
    
    # 置上线状态
    cli.send(pack_001d(cli.stru))
    cli.manage.append(unpack_001d(cli.stru))
    await cli.recv_and_exec(cli.stru.session_key)

    # 置上线状态
    cli.send(pack_00ec(cli.stru))
    cli.manage.append(unpack_00ec(cli.stru))
    await cli.recv_and_exec(cli.stru.session_key)
    
    # 开启心跳循环
    async def heart_beat():
        cli.send(pack_0058(cli.stru))
        await asyncio.sleep(40)
        cli.add_task(heart_beat())
    cli.manage.append(unpack_0058(cli.stru))
    cli.add_task(heart_beat())