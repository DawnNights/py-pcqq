Python语言PCQQ协议的简单封装，仅用标准库实现，萌新已退坑编程不再做完善

你可以在我博客的[这篇帖子](http://blog.yeli.work/2021/09/11/py-pcqq/)查看更详细的介绍与使用方法

代码写的很烂，Bug应该也不少，如果有需求最好移步[OneBot](https://github.com/botuniverse/onebot)

# 已实现功能

#### 登录
- [x] 扫码登录
- [x] 账密登录

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

# 使用案例

你可以使用 `pip install py-pcqq` 来安装本协议库，开发案例如下:

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

pcqq.init()
pcqq.run()
```
