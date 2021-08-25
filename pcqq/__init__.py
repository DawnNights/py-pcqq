"""
Created on Mon Aug  22:08:34 2021

- Python语言PCQQ协议的简单封装，萌新代码写的很烂，大佬多多包涵

- 本作品完全使用python3的标准库实现，无需安装第三方依赖

- 仅支持扫码登录

- 支持群消息/好友消息的接收(仅解析文本、表情与图片)

- 支持群消息/好友消息的发送(仅支持纯文本)

@author: DawnNights

@blog: http://blog.yeli.work/

@project: https://github.com/DawnNights/py-pcqq

ps: 虽然写的很烂，但请各位大佬给萌新一个star吧，求求惹QAQ
"""
from ._msg import Message
from ._bot import QQBot, Plugin

from ._client import QQClient
from ._struct import QQStruct