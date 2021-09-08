import re

import pcqq.message as msg
import pcqq.utils.log as log

from pcqq.client.client import QQClient
from pcqq.client.login import LoginByScanCode
from pcqq.message._msgBody import MsgBody, HandleMessage

class QQBot:
    def __init__(self):
        self._QQ = QQClient()
        LoginByScanCode(self._QQ)   # 尝试扫码登录
        self._QQ.HeartBeat()    # 循环发送心跳包
    
    def SendPrivateMsg(self, userID:int, message:str):
        '''
        发送私聊消息
        :param userID: 私聊用户的账号
        :param message: 欲发送的消息文本，可以识别PQ码
        '''
        if type(message) == str:
            fulfil = self._QQ.SendPrivateMsg(userID, msg.PQCode(message))
        else:
            message = str(message)
            fulfil = self._QQ.SendPrivateMsg(userID, msg.Text(message))
        
        if fulfil:
            log.info(f"发送私聊消息({userID}): {message}")
        else:
            log.warning(f"尝试发送私聊消息({userID})失败")
    
    def SendGroupMsg(self, groupID:int, message:str):
        '''
        发送群聊消息
        :param groupID: 聊天群的群号
        :param content: 欲发送的消息文本，可以识别PQ码
        '''
        if type(message) == str:
            fulfil = self._QQ.SendGroupMsg(groupID, msg.PQCode(message))
        else:
            message = str(message)
            fulfil = self._QQ.SendGroupMsg(groupID, msg.Text(message))
        
        if fulfil:
            log.info(f"发送群聊消息({groupID}): {message}")
        else:
            log.warning(f"尝试发送群聊消息({groupID})失败")

    def RunBot(self):
        msgBody = MsgBody()
        self._prompt = {}    # 延后命令
        self._plugins = []   # 插件列表

        # 装载插件
        for plugin in Plugin.__subclasses__():
            self._plugins.append(plugin(self, None))
            log.debug(f"插件【{plugin.__name__}】已装载完成")
        print("\n",end="")
        
        # 监听信息
        while True:
            msgBody.__init__()
            HandleMessage(bot=self, src=self._QQ.Recv(), msgBody=msgBody)

    def ExitLogin(self):
        '''退出机器人登录'''
        self._QQ.ExitLogin()

class Plugin:
    def __init__(self, bot:QQBot, msgBody:MsgBody):
        self.state = {}
        self.msgBody = msgBody

        self._prompt = bot._prompt
        self.send_group_msg = bot.SendGroupMsg
        self.send_private_msg = bot.SendPrivateMsg

    def on_full_match(self, keyword:str)->bool:
        '''
        完全匹配模式

        :param keyword: 当接收消息为keyword时满足匹配
        '''
        return self.msgBody.MsgText == keyword
    
    def on_cmd_match(self, cmd:str, prompt:str="")->bool:
        '''
        命令匹配模式，匹配参数存于 self.state["matched"]

        :param keyword: 当接收消息触发词为cmd时满足匹配
        :param prompt: 若匹配参数为空则发送prompt重新向发送者索要参数
        '''
        if self.msgBody.MsgText.find(cmd) == 0:
            self.state["matched"] = self.msgBody.MsgText[len(cmd):].strip()

            if self.state["matched"] == "" and prompt != "":
                if self.msgBody.Type == "group":
                    prompt = "[PQ:at,qq=%d]"%(self.msgBody.FromQQ) + prompt
                
                self.send_msg(prompt)
                self._prompt[self.msgBody.FromQQ] = cmd
            return self.state["matched"] != ""
        return False

    def on_reg_match(self, pattern:str) -> bool:
        '''
        正则匹配模式，匹配参数存于 self.state["regex_matched"]

        :param keyword: 当接收消息能被pattern正则表达式解析时满足匹配
        '''
        self.state["regex_matched"] = re.findall(pattern, self.msgBody.MsgText)
        return self.state["regex_matched"] != []

    def send_msg(self, message:str):
        '''发送消息'''
        if self.msgBody.Type == "group":
            self.send_group_msg(self.msgBody.FromGroup, message)
        elif self.msgBody.Type == "friend":
            self.send_private_msg(self.msgBody.FromQQ, message)
    
    def match(self)->bool:
        '''判断消息是否满足匹配代码'''
        return self.on_full_match("hello")

    def handle(self):
        '''当match方法返回值为True时触发'''
        self.send_msg("hello, "+ msg._GetNickName(self.msgBody.FromQQ))
    
    def _execute_(self):
        if self.match():
            self.handle()