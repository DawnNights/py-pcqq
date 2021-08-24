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
