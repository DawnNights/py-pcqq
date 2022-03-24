import pcqq


@pcqq.on(pcqq.check_type("group_increase", "group_decrease"))
async def Welcome(session: pcqq.Session):
    if session.event_type == "group_increase":
        await session.send_msg({"type": "at", "qq": session.target_id}, "欢迎新人")
    else:
        await session.send_msg(
            {"type":"image","url": f"http://q1.qlogo.cn/g?b=qq&nk={session.user_id}&s=640"},
            {"type": "at", "qq": session.target_id},
            f"({session.target_id})退出了群聊"
            )


@pcqq.on_full("报时")
async def NowTime(session: pcqq.Session):
    await session.send_msg({"type": "at", "qq": session.user_id}, pcqq.utils.time_lapse(0))


@pcqq.on_fulls(["来份涩图", "我要涩涩"])
async def SetuTime(session: pcqq.Session):
    ret = (await pcqq.client.webget(
        url="https://api.lolicon.app/setu/v2?size=original&size=regular&proxy=i.pixiv.re"
    )).json()["data"][0]
    print("网络图片", ret["urls"]["regular"])
    await session.send_msg({"type": "image", "url": ret["urls"]["regular"]}, "\n".join([
        "Title: " + ret["title"],
        "Author: " + ret["author"],
        "Tags: " + ", ".join(ret["tags"]),
        "ImgUrl: " + ret["urls"]["original"],
    ]))


@pcqq.on_command("点歌", prompt="请发送要点的歌名")
async def QQMusic(session: pcqq.Session):
    await session.send_msg({"type": "music", "keyword": session.matched})


@pcqq.on_regex(r"^禁言\[PQ:at,qq=(\d{6,11})\] (\d{1,7})$")
async def ShutUp(session: pcqq.Session):
    qq, secs = session.matched[0]
    await pcqq.set_group_shutup(session.group_id, int(qq), int(secs))

@pcqq.on_regex(r"^改名\[PQ:at,qq=(\d{6,11})\] (.+?)$")
async def ShutUp(session: pcqq.Session):
    qq, nickname = session.matched[0]
    await pcqq.set_group_card(session.group_id, int(qq), nickname)

pcqq.run_bot()
