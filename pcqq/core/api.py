# 注: 为了节省你们安装requests的时间，我就直接拿标准库写咯~
import time
import json
import hashlib
import urllib.parse as parse
import urllib.request as request


def kuwo(keyword: str) -> dict:
    '''酷我音乐'''
    headers = {
        "Cookie": "kw_token=LWKACV45JSQ",
        "csrf": "LWKACV45JSQ",
        "Referer": "https://www.kuwo.cn/search/list"
    }
    req = request.Request(
        url=f"https://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key={parse.quote(keyword)}&pn=1&rn=1&httpsStatus=1",
        headers=headers,
        method="GET")
    with request.urlopen(req) as rsp:
        info = json.loads(rsp.read())["data"]["list"][0]

    req = request.Request(
        url=f"http://www.kuwo.cn/url?format=mp3&rid={info['rid']}&response=url&type=convert_url3&br=128kmp3&from=web&httpsStatus=1",
        headers=headers,
        method="GET")

    with request.urlopen(req) as rsp:
        music = json.loads(rsp.read())

    return {
        "title": info["name"],
        "content": info["artist"],
        "url": "https://www.kuwo.cn/play_detail/" + str(info["rid"]),
        "audio": music["url"],
        "cover": info["pic"],
    }


def kugou(keyword: str) -> dict:
    '''酷狗音乐'''
    md5 = hashlib.md5()
    stamp = int(time.time()) * 1000
    md5.update("".join([
        "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwtbitrate=0", "callback=callback123",
        "clienttime={time}", "clientver=2000", "dfid=-", "inputtype=0",
        "iscorrection=1", "isfuzzy=0", "keyword={keyword}", "mid={time}",
        "page=1", "pagesize=1", "platform=WebFilter", "privilege_filter=0",
        "srcappid=2919", "tag=em", "userid=-1", "uuid={time}",
        "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"
    ]).format(time=stamp, keyword=keyword).encode())

    with request.urlopen(
            url="https://complexsearch.kugou.com/v2/search/song?" + "&".join([
                "callback=callback123", "keyword={keyword}", "page=1",
                "pagesize=1", "bitrate=0", "isfuzzy=0", "tag=em",
                "inputtype=0", "platform=WebFilter", "userid=-1",
                "clientver=2000", "iscorrection=1", "privilege_filter=0",
                "srcappid=2919", "clienttime={time}", "mid={time}",
                "uuid={time}", "dfid=-", "signature={sign}"
            ]).format(time=stamp,
                      keyword=parse.quote(keyword),
                      sign=md5.hexdigest().upper())) as rsp:
        info = json.loads(rsp.read().decode()[12:-2].replace(
            "<\\/em>", "").replace("<em>", ""))["data"]["lists"][0]

    req = request.Request(
        method="GET",
        url="https://wwwapi.kugou.com/yy/index.php?r=play/getdata&hash=%s&album_id=%s"
        % (info["FileHash"], info["AlbumID"]),
        headers={"Cookie": "kg_mid=d8e70a262c93d47599c6196c612d6f4f"})

    with request.urlopen(req) as rsp:
        music = json.loads(rsp.read())["data"]

    return {
        "title":
        music["song_name"],
        "content":
        music["author_name"],
        "url":
        "https://www.kugou.com/song/#hash=%s&album_id=%s" %
        (info["FileHash"], info["AlbumID"]),
        "audio":
        music["play_backup_url"].replace("\\/", "/"),
        "cover":
        music["img"],
    }


def qqmusic(keyword: str) -> dict:
    '''QQ音乐'''
    req = request.Request(
        method="GET",
        url="https://c.y.qq.com/soso/fcgi-bin/client_search_cp?w=" +
        parse.quote(keyword),
        headers={
            "User-Agent":
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
        })

    with request.urlopen(req) as rsp:
        info = json.loads(rsp.read()[9:-1])["data"]["song"]["list"][0]

    with request.urlopen(
            f"https://y.qq.com/n/yqq/song/{info['songmid']}.html") as rsp:
        page = rsp.read().decode()
        pre = page.find(r"photo_new\u002F")
        pfx = page.find(r"?max_age", pre)
    cover = "https://y.gtimg.cn/music/" + page[pre:pfx].replace(r"\u002F", "/")

    params = {
        "req": {
            "module": "CDN.SrfCdnDispatchServer",
            "method": "GetCdnDispatch",
            "param": {
                "guid": "3982823384",
                "calltype": 0,
                "userip": ""
            }
        },
        "req_0": {
            "module": "vkey.GetVkeyServer",
            "method": "CgiGetVkey",
            "param": {
                "guid": "3982823384",
                "songmid": [str(info["songmid"])],
                "songtype": [0],
                "uin": "0",
                "loginflag": 1,
                "platform": "20"
            }
        },
        "comm": {
            "uin": 0,
            "format": "json",
            "ct": 24,
            "cv": 0
        }
    }

    req = request.Request(
        method="GET",
        url="https://u.y.qq.com/cgi-bin/musicu.fcg?data=" + json.dumps(params),
        headers={
            "User-Agent":
            "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
            "referer": "http://y.qq.com"
        })

    with request.urlopen(req) as rsp:
        music = json.loads(rsp.read())['req_0']['data']['midurlinfo'][0]

    return {
        "title": info["songname"],
        "content": info["singer"][0]["name"],
        "url": f"https://y.qq.com/n/yqq/song/{info['songmid']}.html",
        "audio": "https://isure.stream.qqmusic.qq.com/" + music['purl'],
        "cover": cover,
    }


def cloud163(keyword: str) -> dict:
    '''网易云音乐'''
    req = request.Request(
        method="POST",
        url="http://music.163.com/api/search/pc",
        headers={
            "Content-Type":
            "application/x-www-form-urlencoded",
            "User-Agent":
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
        },
        data=parse.urlencode({
            "offset": "0",
            "total": "true",
            "limit": "9",
            "type": "1",
            "s": keyword
        }).encode())

    with request.urlopen(req) as rsp:
        info = json.loads(rsp.read())["result"]["songs"][0]

    return {
        "title": info["name"],
        "content": info["artists"][0]["name"],
        "url": f"https://music.163.com/song?id={info['id']}",
        "audio":
        f"http://music.163.com/song/media/outer/url?id={info['id']}.mp3",
        "cover": info["album"]["blurPicUrl"],
    }


__nickNameCache__ = {}


def GetNickName(userID: int):
    global __nickNameCache__
    nickname = __nickNameCache__.get(userID, "")

    if nickname:
        return nickname

    with request.urlopen(
            "http://r.qzone.qq.com/fcg-bin/cgi_get_score.fcg?mask=7&uins=" +
            str(userID)) as rsp:
        page = rsp.read().decode()

    return page[page.find(",\"") + 2:page.rfind("\",")]
