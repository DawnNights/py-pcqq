import httpx
import json

from core.entities import QQStruct

async def cgi_get_score(user_id:int) -> dict:
    async with httpx.AsyncClient() as client:
        rsp = await client.get(f"https://r.qzone.qq.com/fcg-bin/cgi_get_score.fcg?mask=7&uins={user_id}")
        
    return json.loads(rsp.text.strip('portraitCallBack();'))

async def search_v3(stru: QQStruct, user_id: int):
    async with httpx.AsyncClient() as client:
        rsp = await client.get(
            url="https://cgi.find.qq.com/qqfind/buddy/search_v3",
            params={"keyword": user_id},
            headers={"Cookie": stru.cookie}
        )
     
    try:
        ret = rsp.json()
        return ret["result"]["buddy"]["info_list"][0]
    except:
        return None


async def get_group_info_all(stru: QQStruct, group_id: int):
    async with httpx.AsyncClient() as client:
        rsp = await client.get(
            url="https://qinfo.clt.qq.com/cgi-bin/qun_info/get_group_info_all",
            params={
                "gc": group_id,
                "bkn": stru.bkn,
                "src": "qinfo_v3",
            },
            headers={"Cookie": stru.cookie}
        )

        return rsp.json()


async def get_group_members_new(stru: QQStruct, group_id: int):
    async with httpx.AsyncClient() as client:
        rsp = await client.get(
            url="https://qinfo.clt.qq.com/cgi-bin/qun_info/get_group_members_new",
            params={
                "gc": group_id,
                "bkn": stru.bkn,
                "src": "qinfo_v3",
            },
            headers={"Cookie": stru.cookie}
        )

        return rsp.json()

# Success: {'ec': 0, 'errcode': 0, 'em': 'ok'}
# Failed: {'ec': 3, 'errcode': 0, 'em': ''}


async def set_group_card(stru: QQStruct, group_id: int, user_id: int, card: str):
    async with httpx.AsyncClient() as client:
        rsp = await client.post(
            url="https://qinfo.clt.qq.com/cgi-bin/qun_info/set_group_card",
            data={
                "u": user_id,
                "gc": group_id,
                "bkn": stru.bkn,
                "src": "qinfo_v3",
                "name": card
            },
            headers={"Cookie": stru.cookie}
        )

        return rsp.json()
