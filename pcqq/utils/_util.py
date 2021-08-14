import random
import hashlib

def GetRandomBin(length: int)->bytes:
    '''生成指定长度的随机字节集'''
    dst = [random.randint(0,255).to_bytes(1,"big") for x in range(length)]
    return b''.join(dst)

def Bin2HexTo(src: bytes)->str:
    '''字节集转十六进制文本'''
    s = " ".join([hex(b)[2:].upper() for b in src])
    return s

def Hex2Bin(s: str)->bytes:
    '''十六进制文本转字节集'''
    dst = b''.join([int("0x"+i,16).to_bytes(1,"big") for i in s.split(" ")])
    return dst

def HashMD5(src: bytes)->bytes:
    '''将字节集编码为md5 16bit字节集'''
    s = ""
    dst = b''
    md = hashlib.md5(src)
    origin = md.hexdigest()
    for i in range(len(origin)):
        s += origin[i]
        if i % 2 != 0:
            int_hex = int(s, 16)
            dst += int_hex.to_bytes(1,"big")
            s = ""
    return dst

def GroupToGid(groupId:int)->int:
    '''群号转GID'''
    group = str(groupId)
    left = int(group[0:-6])
    if left >= 0 and left <= 10:
        right = group[-6:]
        gid = str(left + 202) + right
    elif left >= 11 and left <= 19:
        right = group[-6:]
        gid = str(left + 469) + right
    elif left >= 20 and left <= 66:
        left = int(str(left)[0:1])
        right = group[-7:]
        gid = str(left + 208) + right
    elif left >= 67 and left <= 156:
        right = group[-6:]
        gid = str(left + 1943) + right
    elif left >= 157 and left <= 209:
        left = int(str(left)[0:2])
        right = group[-7:]
        gid = str(left + 199) + right
    elif left >= 210 and left <= 309:
        left = int(str(left)[0:2])
        right = group[-7:]
        gid = str(left + 389) + right
    elif left >= 310 and left <= 335:
        left = int(str(left)[0:2])
        right = group[-7:]
        gid = str(left + 349) + right
    elif left >= 336 and left <= 386:
        left = int(str(left)[0:3])
        right = group[-6:]
        gid = str(left + 2265) + right
    elif left >= 387 and left <= 499:
        left = int(str(left)[0:3])
        right = group[-6:]
        gid = str(left + 3490) + right
    elif left >= 500:
        return int(group)
    return int(gid)
    # i.to_bytes(4,'big')