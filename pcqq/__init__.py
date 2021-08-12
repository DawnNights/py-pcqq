"""
Created on Tue June 21 22:41:34 2021
/**
 * py-pcqq，一个python实现的简单pcqq协议
 * 本作品完全使用python3的标准库编写，无需第三方依赖
 * 代码写的很烂，功能也不齐全，BUG还不少，请各位多多包涵
 * 仅支持扫码登录
 * 支持群消息/好友消息的接收(仅解析文本、表情与图片)
 * 支持群消息/好友消息的发送(仅支持纯文本)
 */
@author: DawnNights
@project: https://github.com/DawnNights/py-pcqq
"""

from ._core import QQBot,Plugin

def help():
    helpText = """
1.想要创建一个机器人，你需要先实例化一个pcqq.QQBot的对象，并在60秒内扫码登录，例:
bot = pcqq.QQBot()

2.在登录成功后，想为机器人编写功能，你只需要定义一个pcqq.Plugin的子类，并重写match和handle方法即可，例:
class TestPluginA(pcqq.Plugin):
    def match(self) -> bool:
        return self.on_full_match("hellp")
    
    def handle(self):
        self.send_msg("hello world")

class TestPluginB(pcqq.Plugin):
    def match(self) -> bool:
        return self.on_reg_match("复读\s(.*)")
    
    def handle(self):
        self.send_msg(self.Args[0])

3.在功能插件编写完成后，你只需要调用pcqq.QQBot对象的ListenMsg方法，便可让机器人开始运行，例:
bot.ListenMsg()
"""
    print(helpText)