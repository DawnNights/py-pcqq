import os
import sys
import asyncio
import threading

import pcqq.log as log
import pcqq.core as core
import pcqq.client as client

from ._plugin import Plugin
from ._session import Session

driver = None
plugins = None


def init(uin: int = 0, password: str = '', *admins: int):
    '''
    :param uin: 机器人的账号
    :param password: 机器人的密码
    :param admins: 机器人的超级用户集

    1. 若uin或password留空则使用扫码登录
    2. admins的内容用户isAdmin规则判断
    3. 插件功能必须在此函数被调用前注册或导入
    '''
    global driver, plugins

    plugins = Plugin.__subclasses__()[:]
    plugins.sort(key=lambda self: self.priority)    # 根据优先级排序
    log.Println('检测到%d个插件，装载完成，开始尝试登录\n' % (len(plugins)))

    driver = core.QQDriver(client.QQClient(), *admins)

    if os.path.exists('session.token'):
        client.LoginByToken(QQ=driver._Caller_)
    elif uin and password:
        client.LoginByPassword(QQ=driver._Caller_, Uin=uin, Password=password)
    else:
        client.LoginByScancode(QQ=driver._Caller_)

    threading.Thread(target=driver.__HeartBeat__).start()   # 开启心跳线程


def run():
    '''
    开始监听事件
    '''
    global driver, plugins
    threading.Thread(target=driver.__ListenEvent__).start()  # 开启事件监听线程

    def handle(session: Session):
        for plugin in plugins:
            try:
                if plugin(session).run() and plugin.block:
                    break
            except Exception as err:
                log.Panicln(err)
    
    
    loop = asyncio.get_event_loop()
    while True:
        session = Session(driver, driver.Channle.get())
        loop.run_in_executor(None, handle, session)    # 将事件分配给处理函数


def load_plugins(moudles_path: str = ""):
    '''
    导入指定路径下模块或包内注册的插件功能

    :param moudles_path: 插件模块或包的路径
    '''
    if not moudles_path:
        moudles_path = os.getcwd()

    selfPath = ""
    if moudles_path == os.getcwd():
        selfPath = os.path.normcase(sys.argv[0]).lower()

    for root, dirs, files in os.walk(moudles_path):
        sys.path.append(root)

        for file in files:

            if selfPath and os.path.join(root, file).lower() == selfPath:
                continue

            if file.endswith(('.py', '.pyw', '.pyd')):
                __import__(file[:file.rfind('.')])

        for dir in dirs:
            if '__init__.py' in os.listdir(os.path.join(root, dir)):
                __import__(dir)

        break
