# py-pcqq

Python语言PCQQ协议的简单封装，萌新代码写的很烂，大佬多多包涵

本作品完全使用python3的标准库实现，无需安装第三方依赖

仅支持扫码登录

支持群消息/好友消息的接收(仅解析文本、表情与图片)

支持群消息/好友消息的发送(仅支持纯文本)

# How to use

请参考demo.py中的写法

``` bash
import pcqq
bot = pcqq.QQBot()

# 完全匹配模式
class Hello(pcqq.Plugin):
    def match(self):
        return self.on_full_match("你好")
    def handle(self):
        self.send_msg("你也好呀")

# 正则匹配模式
class Reread(pcqq.Plugin):
    def match(self):
        return self.on_reg_match("复读\s(.*)")
    
    def handle(self):
        self.send_msg(self.Args[0])

# 命令匹配模式
class Game(pcqq.Plugin):
    def match(self):
        return self.on_common_match("猜拳","您要出什么手势呢")
    
    def handle(self):
        self.send_msg(f"咱的手势是剪刀，您的手势是{self.Args[0]}")

bot.RunBot()


```