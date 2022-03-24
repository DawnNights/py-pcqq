import time
import random
import string
import hashlib

def hashmd5(src: bytes):
    return hashlib.md5(src).digest()

def randbytes(size: int):
    return bytes([random.randint(0, 255) for _ in range(size)])

def randstr(size: int):
    return ''.join(random.sample(string.ascii_letters + string.digits, size))


def gtk_skey(skey: str) -> int:
    accu = 5381
    for s in skey:
        accu += (accu << 5) + ord(s)
    return accu & 2147483647


def time_lapse(seconds: int):
    time_stamp = int(time.time()) + seconds
    return time.strftime("%Y年%m月%d日 %H:%M:%S", time.localtime(time_stamp))