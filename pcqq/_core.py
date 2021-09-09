import re
import asyncio

import pcqq.log as log
import pcqq.const as const
import pcqq.message as msg
import pcqq.utils as utils
import pcqq.client as client
import pcqq.binary as binary



class QQBot:
    def __init__(self) -> None:
        self._QQ = client.QQClient()    # 创建QQ客户端
        client.LoginByScanCode(self._QQ)    # 使用扫码登录
        self._QQ.HeartBeat()    # 启动心跳包循环
    
    def SendPrivateMsg(self, userID:int, message:str):
        '''
        发送私聊消息
        :param userID: 私聊用户的账号
        :param message: 欲发送的消息文本，可以识别PQ码
        '''
        if type(message) == str:
            source = msg.PQCode(message)
        else:
            message = str(message)
            source = msg.Text(message)
        
        if self._QQ.SendPrivateMsg(userID, source):
            log.Println(f"发送私聊消息({userID}): {message}")
        else:
            log.Fatalln(f"尝试发送私聊消息({userID})失败")
    
    def SendGroupMsg(self, groupID:int, message:str):
        '''
        发送群聊消息
        :param groupID: 聊天群的群号
        :param content: 欲发送的消息文本，可以识别PQ码
        '''
        if type(message) == str:
            source = msg.PQCode(message)
        else:
            message = str(message)
            source = msg.Text(message)
        
        if self._QQ.SendGroupMsg(groupID, source):
            log.Println(f"发送群聊消息({groupID}): {message}")
        else:
            log.Fatalln(f"尝试发送群聊消息({groupID})失败")
    

    def RunBot(self):
        '''装载插件，监听消息'''
        self._prompt = {}
        self.plugins = Plugin.__subclasses__()
        for name in [plugin.__name__ for plugin in self.plugins]:
            log.Println(f"插件<< {name} >>已装载完成")
        
        async def HandleMsg(self:QQBot):
            '''接收并处理一条信息'''
            src = self._QQ.Recv()
            try:
                body = binary.TeaDecrypt(src[16:-1], self._QQ.SessionKey)
                if not body:
                    return
            except:
                return
            
            self._QQ.Send(
                src[2:13] + 
                const.BodyVersion +
                binary.TeaEncrypt(body[0:16], self._QQ.SessionKey) + 
                const.Tail
                )   # 消息初步回执

            msgBody = msg.MsgBody()
            if msg.MsgParse(body=body, msgBody=msgBody, QQ=self._QQ):
                if msgBody.Type == "group":
                    log.Println(f"收到群聊({msgBody.FromGroup})消息 {msg._GetNickName(msgBody.FromQQ)}: {msgBody.MsgText}")
                elif msgBody.Type == "friend":
                    log.Println(f"收到私聊({msgBody.FromQQ})消息 {msg._GetNickName(msgBody.FromQQ)}: {msgBody.MsgText}")
                
                command = self._prompt.get(msgBody.FromQQ, "")
                if command:
                    msgBody.MsgText = command + msgBody.MsgText
                    self._prompt.pop(msgBody.FromQQ)

                for plugin in self.plugins:
                    plugin = plugin(bot=self, msgBody=msgBody)
                    if plugin.match():
                        plugin.handle()  


        # import time
        loop = asyncio.get_event_loop()
        while True:
            # time.sleep(0.2)
            loop.run_until_complete(HandleMsg(self))

class Plugin:
    def __init__(self, bot:QQBot, msgBody:msg.MsgBody):
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
        '''判断消息是否满足匹配功能'''
        return self.on_full_match("hello")

    def handle(self):
        '''当match方法返回值为True时调用的功能'''
        self.send_msg("hello, "+ msg._GetNickName(self.msgBody.FromQQ))