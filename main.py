"""
Created on Tue June 21 22:41:34 2021
/**
 * py-pcqq，一个python实现的简单pcqq协议

 * 本作品完全采用python3的标准库编写

 * 仅支持扫码登录

 * 支持私聊/群聊消息的发送(仅纯文本)

 * 支持私聊/群聊消息的接收与解析(仅纯文本/艾特/图片)

 * Demo使用青云客聊天接口进行交流互动

 */
@author: DawnNights
"""
from json import loads
from core.pcqq import PCQQ
from urllib.parse import quote
from urllib.request import urlopen

def demoHandle(question:str)->str:
    '''
    处理问题并回答的demo，此处采用青云客API
    :param question: 处理的问题文本
    :return: 回答文本
    '''
    if question == "":
        return ""
    rsp = urlopen("http://api.qingyunke.com/api.php?key=free&appid=0&msg="+quote(question))
    res = loads(rsp.read().decode())
    rsp.close()

    if res["result"] == 0:
        return res["content"]
    else:
        return ""

pc = PCQQ()
pc.Init()
pc.GetQrCode()
pc.ListenMsg(demoHandle)