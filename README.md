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
- [x] 卡片

#### 接收消息
- [x] At
- [x] 文本
- [x] 图片
- [x] 表情

# 安装
> `注意`
> 请确保你的 Python 版本 >= 3.5

可以使用 pip/pip3 安装已发布的最新版本
```
pip install py-pcqq
```

也可以直接通过 git 下载发布于github上的源码
```
git clone https://github.com/DawnNights/py-pcqq
```

# 开始使用

在确保你已经安装该协议库的情况下，你可以使用以下方法来创造一个机器人

### 最小实例

```python
import pcqq

pcqq.init(uin, password)
pcqq.run()
```

1. uin是机器人的账号, 为 int 类型; password是登录机器人的密码, 为 str 类型

2. 在 uin 或 password 为空值时自动启用扫码登录，Linux系统下需要手动安装pillow库以便于程序在终端打印二维码

3. 当一次登录完成后，程序会在运行路径下生成一个 session.token 的文件，下次运行程序时自动调用文件中的token完成登录

### 编写功能

```
import pcqq

@pcqq.on_event(pcqq.checkType('group_increase'))
def welcome(session: pcqq.Session):
    msg = pcqq.MessageSegment()
    msg.AddAt(session.event.UserID)
    msg.AddText('欢迎新人')
    session.send(msg)

@pcqq.on_regex('^(.{0,2})点歌(.{1,25})$')
def music(session: pcqq.Session):
    typ, keyword = session.get()[0]
    typ = {'': 'qqmusic', '酷我': 'kuwo', '酷狗': 'kugou', '网易': 'cloud163'}.get(typ, '')
    if typ and keyword:
        session.send(f'[PQ:music,type={typ},keyword={keyword}]')

@pcqq.on_full('hello')
def hello(session: pcqq.Session):
    session.send('hello world')

@pcqq.on_command('复读',aliases=['跟我读'])
def reread(session: pcqq.Session):
    words = session.get('请告诉我要复读的内容')
    session.send(words)

pcqq.init(uin, password)
pcqq.run()
```

### 注册插件

如代码中所展示的，你可以使用协议库中的`on_event`、`on_regex`、`on_full`、`on_command`的装饰器来注册机器人功能

被装饰的是一个pcqq.HandleFunc类型的函数，即代码中唯一传参为pcqq.Session类型，无返回值的函数

|       内置装饰器        |      功能      | 说明 |
| ---------------- | ------------- | ---- |
| on_event         | 规则匹配       | 当接收消息满足所有的rules时满足匹配     |
| on_regex         | 正则匹配       | 当接收消息满足正则表达式解析并满足rules时满足匹配     |
| on_full         | 完全匹配       | 当接收消息为指定字符串时满足匹配     |
| on_command     | 命令匹配      | 当关键字出现在接收消息首部时满足匹配     |


你也可以按自己的想法自定义装饰器，参照如下: 

``` python
def on_keyword(keyword: str, *rules: pcqq.Rule):
    def keyRule(session: pcqq.Session) -> pcqq.Rule:
        return keyword in session.event.MessageText

    return pcqq.on_event(*rules, keyRule)
```

### 导入外部插件

`pcqq.load_plugins`是一个用于导入外部模块中注册的插件的功能，其参数`moudles_path`是模块或包的路径( 到文件夹 )

当然，其本质上还是通过import的方式将这些注册的函数导入，你也可以通过`from xx import xxx`或`import xx`的方式来导入