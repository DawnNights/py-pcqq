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
        point = ["剪刀","石头","布"]
        winPoint = [("剪刀","石头"),("石头","布"),("布","剪刀")]

        if self.Args[0] in point:
            result = (__import__("random").choice(point),self.Args[0])
            if result[0] == result[1]:
                self.send_msg(f"机器人出{result[0]}，您出{result[1]}，是平局")
            elif result in winPoint:
                self.send_msg(f"机器人出{result[0]}，您出{result[1]}，您赢了")
            else:
                self.send_msg(f"机器人出{result[0]}，您出{result[1]}，您输了")


bot.RunBot()
