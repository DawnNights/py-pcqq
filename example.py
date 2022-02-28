import json
import urllib

import pcqq # py-pcqq


@pcqq.on_full("报时")
def NowTime(session: pcqq.Session):
    now = pcqq.utils.now_add_time(0)
    session.send_msg("现在时间是: " + now)


@pcqq.on_regex(r"^禁言\[PQ:at,qq=(\d{6,11})\] (\d{1,7})$")
def ShutUp(session: pcqq.Session):
    uid, time = session.matched[0]
    pcqq.set_group_shutup(session.group_id, int(uid), int(time))


@pcqq.on_command("运行代码")
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
    with urllib.request.urlopen(request) as ret:
        ret = json.loads(ret.read())
        session.send_msg((ret["output"]+ret["errors"]).strip())


@pcqq.on_commands(["点歌", "qq点歌", "QQ点歌"], prompt="请说出你要点的歌名")
def PlayMusic(session: pcqq.Session):
    keyword = urllib.parse.quote(session.matched)
    with urllib.request.urlopen("https://c.y.qq.com/soso/fcgi-bin/client_search_cp?w=" + keyword) as ret:
        info = json.loads(ret.read()[9:-1])["data"]["song"]["list"][0]

    request = urllib.request.Request(
        method="GET",
        url="https://u.y.qq.com/cgi-bin/musicu.fcg?data=" + urllib.parse.quote(
            json.dumps(
                {
                    "comm": {"uin": 0, "format": "json", "ct": 24, "cv": 0},
                    "req": {"module": "CDN.SrfCdnDispatchServer", "method": "GetCdnDispatch", "param": {"guid": "3982823384", "calltype": 0, "userip": ""}},
                    "req_0": {"module": "vkey.GetVkeyServer", "method": "CgiGetVkey", "param": {"guid": "3982823384", "songmid": [info["songmid"]], "songtype": [0], "uin": "0", "loginflag": 1, "platform": "20"}}
                }
            ))
    )
    with urllib.request.urlopen(request) as ret:
        audio = json.loads(ret.read())[
            "req_0"]["data"]["midurlinfo"][0]["purl"]

    with urllib.request.urlopen(f"https://y.qq.com/n/yqq/song/{info['songmid']}.html") as ret:
        html = ret.read().decode()
        start = html.find(r"photo_new\u002F")+15
        end = html.find(r"?max_age", start)

    session.send_msg(pcqq.message.pqcode_compile(
        typ="music",
        title=info["songname"],
        content=info["singer"][0]["name"],
        url=f"https://y.qq.com/n/yqq/song/{info['songmid']}.html",
        audio="http://dl.stream.qqmusic.qq.com/" + audio,
        cover="https://y.qq.com/music/photo_new/" + html[start:end]
    ))
pcqq.const.MUSIC_CODE = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><msg serviceID="2" templateID="1" action="web" brief="[分享] {title}" sourceMsgId="0" url="{url}" flag="0" adverSign="0" multiMsgFlag="0"><item layout="2"><audio cover="{cover}" src="{audio}" /><title>{title}</title><summary>{content}</summary></item><source name="" icon="" action="" appid="-1" /></msg>"""

# 不填入账密信息代表使用扫码登录
pcqq.run_bot()
