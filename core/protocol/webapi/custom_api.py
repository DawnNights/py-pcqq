import os
from typing import Dict, List
from dataclasses import dataclass
from jsondataclass import from_json, to_json

from core.client import QQClient
from .offical_api import (
    cgi_get_score,
    search_v3,
    get_group_info_all,
    get_group_members_new,
)


@dataclass
class QQUser:
    name: str
    sex: str
    area: str


@dataclass
class QQMember:
    name: str
    card: str
    role: str


@dataclass
class QQGroup:
    name: str
    owner: int
    admins: List[int]
    members: Dict[str, QQMember]


QQUserCache: Dict[str, QQUser] = {}
QQGroupCache: Dict[str, QQGroup] = {}


async def get_user(cli: QQClient, user_id: int) -> QQUser:
    global QQUserCache
    user_id = str(user_id)
    path = os.path.join(cli.stru.path, "QQUser.json")

    if QQUserCache == {} and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            QQUserCache = from_json(f.read(), Dict[str, QQUser])


    if user_id in QQUserCache:
        return QQUserCache[user_id]

    ret = await search_v3(cli.stru, user_id)
    if ret == None:
        ret = await cgi_get_score(user_id)
        QQUserCache[user_id] = QQUser(
            name=ret[user_id][-4],
            sex="unknow",
            area="",
        )
    else:
        QQUserCache[user_id] = QQUser(
            name=ret["nick"],
            sex={1: "male", 2: "female"}.get(ret["gender"], "unknow"),
            area=ret["country"],
        )

    with open(path, "w", encoding="utf-8") as f:
        f.write(to_json(QQUserCache, ensure_ascii=False))

    return QQUserCache[user_id]


async def get_group(cli: QQClient, group_id: int):
    global QQUserCache, QQGroupCache
    group_id = str(group_id)
    path = os.path.join(cli.stru.path, f"{group_id}.json")

    if not group_id in QQGroupCache and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            QQGroupCache[group_id] = from_json(f.read(), QQGroup)

    if group_id in QQGroupCache:
        return QQGroupCache[group_id]

    ret = await get_group_info_all(cli.stru, group_id)
    group = QQGroup(
        name=ret["gName"],
        owner=ret["gOwner"],
        admins=ret["gAdmins"],
        members=dict()
    )

    ret = await get_group_members_new(cli.stru, group_id)
    for mem in ret["mems"]:
        if mem['u'] == group.owner:
            mem_role = "owner"
        elif mem['u'] in group.admins:
            mem_role = "admin"
        else:
            mem_role = "member"

        group.members[str(mem['u'])] = QQMember(
            name=mem["n"],
            card=ret['cards'].get(str(mem['u']), mem["n"]),
            role=mem_role,
        )

    QQGroupCache[group_id] = group
    with open(path, "w", encoding="utf-8") as f:
        f.write(to_json(QQGroupCache[group_id], ensure_ascii=False))

    return QQGroupCache[group_id]
