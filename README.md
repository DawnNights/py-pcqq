## 简介

因为之前用的轻聊版协议失效, 所以基于最新的 PCQQ9.7.5 协议重新开发

需要安装的第三方库有: `cryptography`, `httpx`, `pillow`

- pip install cryptography==3.4.8
- pip install httpx
- pip install jsondataclass
- ~~pip install pillow~~ (默认调用系统默认应用打开二维码, 如果无法调用则需要 pillow 库在终端中打印)

目前完善了一小部分, 可以 clone 本项目并运行 `example.py` 中的代码查看效果

估摸着这个垃圾玩意也不会有什么用户, 所以本项目将一直处于佛系更新中
