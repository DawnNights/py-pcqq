# py-pcqq

Python语言PCQQ协议的简单封装，萌新代码写的很烂，大佬多多包涵

# 已实现功能

#### 登录
- [x] 扫码登录
- [x] 账密登录
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
1. 创建一个pcqq.QQBot类的实例化对象，通过扫码或填写账密完成机器人的登录

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

class Menu(pcqq.Plugin):
    def match(self) -> bool:
        return self.on_full_match("菜单") 
    def handle(self):
        self.send_msg("没有菜单呢")

class ReRead(pcqq.Plugin):
    def match(self) -> bool:
        return self.on_reg_match("^复读(.+)$")
    def handle(self):
        self.send_msg(self.state["regex_matched"][0])
    
class Game(pcqq.Plugin):
    def match(self) -> bool:
        return self.on_cmd_match("猜拳", "你要出什么手势呢?")
    
    def handle(self):
        point = ["剪刀","石头","布"]
        winPoint = [("剪刀","石头"),("石头","布"),("布","剪刀")]

        if self.state["matched"] in point:
            result = (__import__("random").choice(point),self.state["matched"])
            if result[0] == result[1]:
                self.send_msg("机器人出{0}，您出{1}，是平局".format(*result))
            elif result in winPoint:
                self.send_msg("机器人出{0}，您出{1}，您赢了".format(*result))
            else:
                self.send_msg("机器人出{0}，您出{1}，您输了".format(*result))

bot = pcqq.QQBot()
# bot = pcqq.QQBot(账号, 密码)
bot.RunBot()
```