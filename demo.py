import pcqq

class Hello(pcqq.Plugin):
    pass

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
bot.RunBot()
