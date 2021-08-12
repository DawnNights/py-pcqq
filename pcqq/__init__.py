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
