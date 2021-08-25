# py-pcqq

- Python语言PCQQ协议的简单封装，萌新代码写的很烂，大佬多多包涵

- 本作品完全使用python3的标准库实现，无需安装第三方依赖

- 仅支持扫码登录

- 支持群消息/好友消息的接收(仅解析文本、表情与图片)

- 支持群消息/好友消息的发送(仅支持纯文本)

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

#### 创建机器人对象
1. 创建一个pcqq.QQBot类的实例化对象，通过扫码完成机器人的登录

2. 使用前请在手机QQ的`设置`->`账号安全`->`登录设备管理`中关闭`登录保护`

#### 编写机器人功能

通过创建pcqq.Plugin类的子类，并重写match和handle方法来编写机器人的功能

|       内置方法        |      功能      | 说明 |
| ---------------- | ------------- | ---- |
| send_msg         | 发送消息       | 向接收群/接收用户发送消息内容     |
| on_full_match    | 完全匹配消息      | 详见on_full_match方法注释     |
| on_reg_match     | 正则匹配消息      | 详见on_reg_match方法注释     |
| on_common_match    | 命令匹配消息      | 详见on_common_match方法注释     |