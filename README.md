# py-pcqq

Python语言PCQQ协议的简单封装，萌新代码写的很烂，大佬多多包涵

本作品完全使用python3的标准库实现，无需安装第三方依赖

仅支持扫码登录

支持群消息/好友消息的接收(仅解析文本、表情与图片)

支持群消息/好友消息的发送(仅支持纯文本)

# How to use

首先pip install py-pcqq安装该协议库

随后请参考以下写法

``` bash
import pcqq

bot = pcqq.QQBot()

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

bot.ListenMsg()
```

# 特别感谢
- [Py3QQTEA](https://github.com/ColasDAD/Py3QQTEA)
- [voidbot](https://github.com/FloatTech/voidbot)
