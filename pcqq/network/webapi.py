import json
import pcqq.utils as utils
import pcqq.client as cli
import pcqq.logger as logger


def write_ginfo(info: dict):
    if not cli.cache.exist("ginfo", group_id=info["gid"]):
        cli.cache.insert(
            "ginfo",
            info["name"],
            info["owner"],
            info["gid"],
            info["board"],
            info["intro"],
            info["mem_num"],
        )
    for mem in info["members"]:
        if cli.cache.exist("gmember", user_id=mem["uid"], group_id=info["gid"]):
            continue
        cli.cache.insert(
            "gmember",
            mem["card"],
            mem["uid"],
            mem["name"],
            info["gid"],
            mem["op"]
        )
    cli.cache.commit()


# 封装 Web Api 调用
# cli = cli.QQClient()

async def get_group_members(group_id: int) -> list:
    """
    获取群成员列表
    """
    rsp = await cli.webget(
        "https://qinfo.clt.qq.com/cgi-bin/qun_info/get_group_members_new",
        gc=group_id,
        bkn=cli.bkn,
        src="qinfo_v3",
        headers={"Cookie": cli.cookie}
    )
    rsp.content = rsp.content.split(b'\r\n')[1]
    rsp.content = rsp.content.replace(b"&nbsp;", b" ").replace(b"&amp;", b"&")
    ret = rsp.json()

    cards = ret.get("cards", {})
    admins = [ret["owner"], *ret.get("adm", [])]
    return [
        {
            "uid": mem["u"],
            "name": mem["n"],
            "card": cards.get(str(mem["u"]), mem["n"]),
            "op": int(mem["u"] in admins)
        }
        for mem in ret["mems"]
    ]


async def get_group_info(group_id: int) -> dict:
    """
    获取群信息
    """
    rsp = await cli.webget(
        "https://qinfo.clt.qq.com/cgi-bin/qun_info/get_group_info_all",
        gc=group_id,
        bkn=cli.bkn,
        src="qinfo_v3",
        headers={"Cookie": cli.cookie}
    )
    rsp.content = rsp.content.split(b'\r\n')[1]
    rsp.content = rsp.content.replace(b"&nbsp;", b" ").replace(b"&amp;", b"&")
    ret = rsp.json()

    return {
        "gid": group_id,
        "name": ret["gName"],
        "owner": ret["gOwner"],
        "board": ret["gBoard"],
        "intro": ret["gRIntro"],
        "mem_num": ret["gMemNum"],
        "members": await get_group_members(group_id)
    }


temp_cache = {}


async def get_user_name(user_id: int) -> str:
    if user_id in temp_cache:
        return temp_cache[user_id]

    rsp = await cli.webget("https://r.qzone.qq.com/fcg-bin/cgi_get_score.fcg", mask=7, uins=user_id)
    rsp.content = rsp.content[17:-2]
    temp_cache[user_id] = rsp.json()[str(user_id)][-4]

    return temp_cache[user_id]


async def set_group_card(group_id: int, user_id: int,  nickname: str) -> None:
    """
    修改群成员卡片

    :param group_id: 被修改成员所在的群号

    :param user_id: 被修改成员的QQ号

    :param nickname: 修改后的昵称

    """
    rsp = await cli.webpost(
        url="https://qinfo.clt.qq.com/cgi-bin/qun_info/set_group_card",
        u=user_id,
        name=nickname,
        gc=group_id,
        bkn=cli.bkn,
        src="qinfo_v3",
        headers={"Cookie": cli.cookie}
    )
    rsp.content = rsp.content.split(b'\r\n')[1]
    rsp.content = rsp.content.replace(b"&nbsp;", b" ").replace(b"&amp;", b"&")
    ret = rsp.json()

    gname = await get_group_cache(group_id)
    cord = await get_user_cache(user_id, group_id)
    if ret["em"] == "ok":
        logger.info("成功将 %s(%d) 在群聊 %s(%d) 的名片设置为 %s" % (
            cord, user_id,
            gname, group_id, nickname
        ))
    else:
        logger.error("无法在群聊 %s(%d) 中修改 %s(%d) 的名片" % (
            gname, group_id,
            cord, user_id
        ))


async def set_group_shutup(group_id: int, user_id: int, secs: int = 60):
    """
    设置群成员禁言

    :param group_id: 被禁言成员所在的群号

    :param user_id: 被禁言成员的QQ号

    :param secs: 禁言时长(单位: 秒)

    """
    rsp = await cli.webget(
        url="https://qinfo.clt.qq.com/cgi-bin/qun_info/set_group_shutup",
        shutup_list=json.dumps([{"uin": user_id, "t": secs}]),
        gc=group_id,
        bkn=cli.bkn,
        src="qinfo_v3",
        headers={"Cookie": cli.cookie,}
    )
    rsp.content = rsp.content.split(b'\r\n')[1]
    rsp.content = rsp.content.replace(b"&nbsp;", b" ").replace(b"&amp;", b"&")
    ret = rsp.json()

    gname = await get_group_cache(group_id)
    cord = await get_user_cache(user_id, group_id)
    if not ret["ec"]:

        logger.info("成功将 %s(%d) 在群聊 %s(%d) 中禁言， 预计解禁时间 %s" % (
            cord, user_id,
            gname, group_id,
            utils.time_lapse(secs)
        ))
    else:
        logger.error("无法将 %s(%d) 在群聊 %s(%d) 中禁言" % (
            cord, user_id,
            gname, group_id
        ))

# 封装 cache 简单调用


async def get_user_cache(user_id: int, group_id: int = 0) -> tuple:
    """
    在缓存内取用户昵称
    """
    if group_id:
        ret = cli.cache.select(
            table_name="gmember",
            user_id=user_id,
            group_id=group_id
        )
        if not ret:
            write_ginfo(await get_group_info(group_id))
            return await get_user_cache(user_id, group_id)
        return ret[0][0]
    else:
        return await get_user_name(user_id)


async def get_group_cache(group_id: int) -> str:
    """
    在缓存内取群名称
    """
    ret = cli.cache.select("ginfo", group_id=group_id)
    if not ret:
        write_ginfo(await get_group_info(group_id))
        return await get_group_cache(group_id)
    return ret[0][0]
