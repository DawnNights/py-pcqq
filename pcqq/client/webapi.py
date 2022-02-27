import json
import pcqq.utils as utils
import pcqq.network as net
import pcqq.logger as logger


def set_group_card(user_id: int, group_id: int,  nickname: str) -> None:
    ret = json.loads(net.httper.post_with_cookie(
        url="https://qinfo.clt.qq.com/cgi-bin/qun_info/set_group_card",
        u=user_id,
        name=nickname,
        gc=group_id,
        bkn=net.bkn,
        src="qinfo_v3"
    ))

    if ret["em"] == "ok":
        logger.info("成功将 %s(%d) 在群聊 %s(%d) 的名片设置为 %s" % (
            get_group_cord(user_id, group_id), user_id,
            get_group_name(group_id), group_id, nickname
        ))
    else:
        logger.error("无法在群聊 %s(%d) 中修改 %s(%d) 的名片" %
            get_group_name(group_id), group_id,
            get_group_cord(user_id, group_id), user_id
        )


def set_group_shutup(group_id: int, user_id: int, secs: int = 60):
    ret=json.loads(net.httper.post_with_cookie(
        url="https://qinfo.clt.qq.com/cgi-bin/qun_info/set_group_shutup",
        shutup_list=json.dumps([{"uin": user_id, "t": secs}]),
        gc=group_id,
        bkn=net.bkn,
        src="qinfo_v3"
    ))

    if not ret["ec"]:
        logger.info("成功将 %s(%d) 在群聊 %s(%d) 中禁言， 预计解禁时间 %s" % (
            get_group_cord(user_id, group_id), user_id,
            get_group_name(group_id), group_id,
            utils.now_add_time(secs)
        ))
    else:
        logger.error("无法将 %s(%d) 在群聊 %s(%d) 中禁言" % (
            get_group_cord(user_id, group_id), user_id,
            get_group_name(group_id), group_id
        ))


cache=utils.SqliteDB("cache.db")
if cache.count("ginfo") == -1:
    cache.create(
        "ginfo",
        "name text", "owner integer",
        "group_id integer", "board text",
        "intro text", "mem_num integer"
    )
if cache.count("gmember") == -1:
    cache.create(
        "gmember",
        "name text", "card text",
        "user_id integer", "group_id integer",
        "op boolean"
    )


def cache_set_info(info: dict):
    if not cache.exist("ginfo", group_id = info["gid"]):
        cache.insert(
            "ginfo",
            info["name"],
            info["owner"],
            info["gid"],
            info["board"],
            info["intro"],
            info["mem_num"],
        )

    for mem in info["members"]:
        if cache.exist("gmember", user_id=mem["uid"], group_id=info["gid"]):
            continue
        cache.insert(
            "gmember",
            mem["name"],
            mem["card"],
            mem["uid"],
            info["gid"],
            mem["op"]
        )
        cache.commit()


def get_group_members_nocache(group_id: int) -> list:
    ret = json.loads(net.httper.post_with_cookie(
        "https://qinfo.clt.qq.com/cgi-bin/qun_info/get_group_members_new",
        gc=group_id,
        bkn=net.bkn,
        src="qinfo_v3"
    ).replace(b"&nbsp;", b" ").replace(b"&amp;", b"&"))

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


def get_group_info_all_nocache(group_id: int) -> dict:
    ret = json.loads(net.httper.post_with_cookie(
        "https://qinfo.clt.qq.com/cgi-bin/qun_info/get_group_info_all",
        gc=group_id,
        bkn=net.bkn,
        src="qinfo_v3"
    ).replace(b"&nbsp;", b" ").replace(b"&amp;", b"&"))

    return {
        "gid": group_id,
        "name": ret["gName"],
        "owner": ret["gOwner"],
        "board": ret["gBoard"],
        "intro": ret["gRIntro"],
        "mem_num": ret["gMemNum"],
        "members": get_group_members_nocache(group_id)
    }


name_cache = {}  # 用户昵称缓存


def get_user_name(user_id: int) -> str:
    if not user_id in name_cache:
        ret = net.httper.get(
            "https://r.qzone.qq.com/fcg-bin/cgi_get_score.fcg",
            mask=7,
            uins=user_id
        ).decode()

        name_cache[user_id] = ret[ret.rfind(',"')+2:ret.rfind('",')]
    return name_cache[user_id]


def get_group_name(group_id: int) -> str:
    ret = cache.select("ginfo", group_id=group_id)
    if ret:
        return ret[0][0]
    cache_set_info(get_group_info_all_nocache(group_id))
    return get_group_name(group_id)


def get_group_cord(user_id: int, group_id: int) -> str:
    ret = cache.select("gmember", user_id=user_id, group_id=group_id)
    if ret:
        return ret[0][1]

    cache_set_info(get_group_info_all_nocache(group_id))

    return get_group_cord(user_id, group_id)
