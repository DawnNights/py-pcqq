from pcqq._core import QQBot,Plugin

bot = QQBot()

class DemoPluginA(Plugin):
    def match(self) -> bool:
        return self.on_full_match("hello")
    def handle(self):
        self.send_msg("hello world")

class DemoPluginB(Plugin):
    def match(self) -> bool:
        return self.on_re_match("复读\s(.*)")
    def handle(self):
        self.send_msg(self.Args[0])

bot.ListenMsg()
