# py-pcqq

Python语言PCQQ协议的简单封装，萌新代码写的很烂，大佬多多包涵

# 已实现功能

#### 登录
- [x] 扫码登录
- [x] 退出登录

#### 发送消息
- [x] At
- [x] 文本
- [x] 表情
- [x] Xml卡片

#### 接收消息
- [x] At
- [x] 文本
- [x] 图片
- [x] 表情

# How to use

#### 创建机器人对象
1. 创建一个pcqq.QQBot类的实例化对象，通过扫码完成机器人的登录

2. 使用前请在手机QQ的`设置`->`账号安全`->`登录设备管理`中关闭`登录保护`

3. 调用对象的`ExitLogin`方法退出登录
#### 编写机器人功能

通过创建pcqq.Plugin类的子类，并重写match方法和handle方法来编写机器人的功能

|       内置方法        |      功能      | 说明 |
| ---------------- | ------------- | ---- |
| send_msg         | 发送消息       | 向接收群/接收用户发送消息内容     |
| send_group_msg         | 发送群聊消息       | 向指定群发送消息内容     |
| send_private_msg         | 发送私聊消息       | 向指定用户发送消息内容     |
| on_reg_match     | 正则匹配消息      | 详见on_reg_match方法注释     |
| on_cmd_match    | 命令匹配消息      | 详见on_cmd_match方法注释     |
| on_full_match    | 完全匹配消息      | 详见on_full_match方法注释     |

#### 低配CQ之PQ码


| PQ 码        | 功能                        |
| ------------ | --------------------------- |
| [PQ:at,qq=`对方QQ`]      | @对方                     |
| [PQ:face,id=`表情ID`]    | 发送QQ 表情                   |
| [PQ:xml,file=`xml代码`]     | 发送XML卡片                 |
| [PQ:music,title=`标题`,author=`歌手`,url=`跳转链接`,audio=`音频链接`,cover=`封面链接`]   | 分享自定义音乐 |

#### 一个简单的小案例

```
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

```
