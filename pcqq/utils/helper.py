import time
import random
import hashlib
import asyncio

from typing import Dict, Generator
from urllib.request import urlopen, Request
from urllib.parse import urlparse, urlencode


def hashmd5(src: bytes):
    return hashlib.md5(src).digest()


def randbytes(size: int):
    return bytes([random.randint(0, 255) for _ in range(size)])


def gtk_skey(skey: str) -> int:
    accu = 5381
    for s in skey:
        accu += (accu << 5) + ord(s)
    return accu & 2147483647


def int_to_bytes(num: int) -> bytes:
    size = 1
    while num >= int.from_bytes(b'\xff' * size, 'big'):
        size += 1
    return num.to_bytes(size, 'big')

def now_add_time(seconds:int):
    time_stamp  = int(time.time()) + seconds
    return time.strftime("%Y年%m月%d日 %H:%M:%S", time.localtime(time_stamp))

class Httper:
    def __init__(self, cookies: str) -> None:
        self.cookies = cookies

    def get_with_cookie(self, url: str, **params) -> bytes:
        print(url + "?" + urlencode(params))
        request = Request(
            url=url + "?" + urlencode(params),
            method="GET",
            headers={
                "Host": urlparse(url).netloc,
                "Origin": urlparse(url).netloc,
                "Cookie": self.cookies,
            }
        )

        with urlopen(request) as rsp:
            return rsp.read()

    def post_with_cookie(self, url: str, **params) -> bytes:
        request = Request(
            url=url,
            method="POST",
            data=urlencode(params).encode(),
            headers={
                "Host": urlparse(url).netloc,
                "Origin": urlparse(url).netloc,
                "Cookie": self.cookies,
            }
        )

        with urlopen(request) as rsp:
            return rsp.read()

    def get(self, url: str, **params):
        url = url + "?" + urlencode(params)
        with urlopen(url) as rsp:
            return rsp.read()


class Waiter(Dict[int, Generator]):
    async def wait(self, uid: int, ret: Generator) -> bool:
        self[uid] = ret,
        for _ in range(60):
            if not uid in self:
                return False
            await asyncio.sleep(0.5)
        return True
