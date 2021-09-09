import pcqq

import json
import random
import urllib.parse as parse
import urllib.request as request

class Hello(pcqq.Plugin):
    def match(self) -> bool:
        return self.on_full_match("hello")

class ReRead(pcqq.Plugin):
    def match(self) -> bool:
        return self.on_reg_match("^复读(.+)$")
    def handle(self):
        self.send_msg(self.state["regex_matched"][0])

class Welcome(pcqq.Plugin):
    def match(self) -> bool:
        return self.msgBody.SubType == "increase"
    def handle(self):
        self.send_msg(f"[PQ:at,qq={self.msgBody.FromQQ}]欢迎进群")

class Game(pcqq.Plugin):
    def match(self) -> bool:
        return self.on_cmd_match("猜拳", "你要出什么手势呢?")
    
    def handle(self):
        point = ["剪刀","石头","布"]
        winPoint = [("剪刀","石头"),("石头","布"),("布","剪刀")]

        if self.state["matched"] in point:
            result = (random.choice(point),self.state["matched"])
            if result[0] == result[1]:
                self.send_msg("机器人出{0}，您出{1}，是平局".format(*result))
            elif result in winPoint:
                self.send_msg("机器人出{0}，您出{1}，您赢了".format(*result))
            else:
                self.send_msg("机器人出{0}，您出{1}，您输了".format(*result))

class KuwoMusic(pcqq.Plugin):   # 酷我点歌
    def match(self) -> bool:
        return self.on_cmd_match("点歌", "请问你要点的歌名是什么")
    def handle(self):
        headers = {
            "Cookie": "Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1610284708,1610699237; _ga=GA1.2.1289529848.1591618534; kw_token=LWKACV45JSQ; Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1610699468; _gid=GA1.2.1868980507.1610699238; _gat=1",
            "csrf": "LWKACV45JSQ",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
            "Referer": "https://www.kuwo.cn/search/list?key=",
        }

        req = request.Request(
            url = f"https://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key={parse.quote(self.state['matched'])}&pn=1&rn=1&httpsStatus=1", 
            headers = headers, 
            method = "GET"
        )
        with request.urlopen(req) as rsp:
            info = json.loads(rsp.read())["data"]["list"][0]
        
        req = request.Request(
            url = f"http://www.kuwo.cn/url?format=mp3&rid={info['rid']}&response=url&type=convert_url3&br=128kmp3&from=web&httpsStatus=1", 
            headers = headers, 
            method = "GET"
        )
        
        with request.urlopen(req) as rsp:
            music = json.loads(rsp.read())
        
        self.send_msg(f"[PQ:music,title={info['name']},author={info['artist']},url=https://www.kuwo.cn/play_detail/{info['rid']},audio={music['url']},cover={info['pic']}]")

bot = pcqq.QQBot()
bot.RunBot()
