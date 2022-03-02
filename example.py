import json
import urllib

import pcqq  # py-pcqq


@pcqq.on_type("group_increase")
def MemberAdd(session: pcqq.Session):
    session.send_msg(f"[PQ:at,qq={session.user_id}]欢迎新人~")


@pcqq.on_full("报时")
def NowTime(session: pcqq.Session):
    now = pcqq.utils.now_add_time(0)
    session.send_msg("现在时间是: " + now)


@pcqq.on_fulls(["来份涩图", "来张涩图", "搞快点"])
def SetuTime(session: pcqq.Session):
    with urllib.request.urlopen("https://api.lolicon.app/setu/v2?size=regular") as rsp:
        ret = json.loads(rsp.read())["data"][0]
    
    url = ret["urls"]["regular"].replace("pixiv.cat", "pixiv.re")
    session.send_msg("\n".join([
        "[PQ:image,url=%s]" % (url),
        "Title: %s" % (ret["title"]),
        "Author: %s" % (ret["author"]),
        "Tags: %s" % (json.dumps(ret["tags"], ensure_ascii=False))
    ]))


@pcqq.on_regex(r"^禁言\[PQ:at,qq=(\d{6,11})\] (\d{1,7})$")
def ShutUp(session: pcqq.Session):
    uid, time = session.matched[0]
    pcqq.set_group_shutup(session.group_id, int(uid), int(time))


@pcqq.on_command("运行代码", prompt="请提交python3代码")
def RunCode(session: pcqq.Session):
    request = urllib.request.Request(
        method="POST",
        url="https://tool.runoob.com/compile2.php",
        data=urllib.parse.urlencode({
            "code":     session.matched,
            "token":    "4381fe197827ec87cbac9552f14ec62a",
            "stdin":    "",
            "language": "15",
            "fileext":  "py3",
        }).encode()
    )
    with urllib.request.urlopen(request) as rsp:
        ret = json.loads(rsp.read())
        session.send_msg((ret["output"]+ret["errors"]).strip())


@pcqq.on_commands(["点歌", "qq点歌", "QQ点歌"], prompt="请说出你要点的歌名")
def PlayMusic(session: pcqq.Session):
    session.send_msg("[PQ:music,keyword=%s]" % (session.matched))


# 不填入账密信息代表使用扫码登录
pcqq.run_bot()
