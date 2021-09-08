import random
import hashlib

def ToBytes(*arg):
	return b''.join([x.to_bytes(1,'big') for x in arg])

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

def GetRandomBin(length: int)->bytes:
    '''生成指定长度的随机字节集'''
    dst = [random.randint(0,255).to_bytes(1,"big") for _ in range(length)]
    return b''.join(dst)

def Bin2HexTo(src: bytes)->str:
    '''字节集转十六进制文本'''
    s = " ".join([hex(b)[2:].upper() for b in src])
    return s

def Hex2Bin(s: str)->bytes:
    '''十六进制文本转字节集'''
    dst = b''.join([int("0x"+i,16).to_bytes(1,"big") for i in s.split(" ")])
    return dst

def VarInt(num: int)->list:
    '''转可变整数列表'''
    n = 0
    buf = [None for x in range(10)]
    while num > 127:
        buf[n] = 0x80 | num&0x7F
        num = num >> 7
        n += 1
    buf[n] = num
    return [x for x in buf if x != None]

def IntSize(num: int)->int:
    '''取整数转字节集长度'''
    size = 1
    while True:
        if num <= int.from_bytes(b'\xff'*size,"big"):
            break
        size += 1
    return size

def IpToHex(ip:str)->str:
    '''Ip地址转16进制文本'''
    return " ".join([hex(int(i))[2:] for i in ip.split(".")])

def HexToIp(string:str)->str:
    '''16进制文本转Ip地址'''
    return ".".join([str(eval("0x"+s)) for s in string.split(" ")])

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

def SkeyToGtk(skey:str)->str:
    base = 5381
    for s in skey:
        base += (base << 5) + ord(s)
    return str(base & 2147483647)