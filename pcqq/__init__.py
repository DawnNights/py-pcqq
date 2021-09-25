"""
Created on Thu Sep 23 at 20:20 2021

用前须知:
1. py-pcqq，这是一个本萌新使用Python编写的QQBot库，基于PC版QQ协议
2. 本项目仅作个人娱乐，功能极少，有更强大的功能需求请移步onebot
3. 本项目开源于Github，萌新代码写的很烂，各位大佬请多多包涵( 给点star吧，求求惹QAQ )
4. 本萌新的博客和Github项目首页中有关于该协议库的相关说明

联系方式:
@QQ: 2224825532
@Blog: http://blog.yeli.work
@Github: https://github.com/DawnNights
"""

from ._session import Session, Event, QQDriver, MessageSegment, Rule, HandleFunc
from ._plugin import on_event, on_regex, on_full, on_command, \
    isAtMe, isAdmin, onlyGroup, onlyPrivate, checkUser, checkType
from ._bot import init, run, load_plugins
