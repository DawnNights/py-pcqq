import os
import sys
import asyncio

import pcqq.utils.log as log
import pcqq.core as core
import pcqq.client as client

from ._plugin import Plugin
from ._session import Session

driver = None
plugins = []


def init(uin: int = 0, password: str = '', *admins: int):
    '''
    :param uin: 机器人的账号
    :param password: 机器人的密码
    :param admins: 机器人的超级用户
    PS: 若uin或password留空则使用扫码登录
    '''
    global driver
    qq_client = client.QQClient()

    if os.path.exists('session.token'):
        client.LoginByToken(QQ=qq_client)
    elif uin and password:
        client.LoginByPassword(QQ=qq_client, Uin=uin, Password=password)
    else:
        client.LoginByScancode(QQ=qq_client)

    driver = core.QQDriver(qq_client, *admins)


def run():
    '''
    加载插件，运行机器人
    '''
    global driver, plugins
    plugins = Plugin.__subclasses__()
    print('                        ')
    # log.Println('插件加载完毕，共加载%d个插件，开始接收消息\n' % (len(plugins)))

    async def handle(session: Session, plugin):
        try:
            plugin(session).run()
        except Exception as err:
            log.Panicln(err)

    loop = asyncio.get_event_loop()
    while True:
        session = Session(driver, driver.Channle.get())

        for plugin in plugins:
            loop.run_until_complete(handle(session, plugin))


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