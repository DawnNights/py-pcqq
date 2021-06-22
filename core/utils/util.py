from re import findall
from hashlib import md5
from random import randint

def GetRandomBin(length: int)->bytes:
    '''生成指定长度的随机字节集'''
    dst = [randint(0,255).to_bytes(1,"big") for x in range(length)]
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
    md = md5(src)
    origin = md.hexdigest()
    for i in range(len(origin)):
        s += origin[i]
        if i % 2 != 0:
            int_hex = int(s, 16)
            dst += int_hex.to_bytes(1,"big")
            s = ""
    return dst

def PbToLength(num:int)->str :
    '''特殊加密'''
    temp = ""
    binary = bin(num)[2:]
    while len(binary) > 0:
        binary1 = "0000000" + binary
        temp = temp + "1" + binary1[-7:]
        if len(binary) >= 7:
            binary = binary[0:-7]
        else:
            break
    temp1 = temp[-7:]
    temp = temp[0:-8] + "0" + temp1
    temp = hex(int("0b"+temp,2)).upper()[2:]
    return " ".join(findall(".{2}",temp))
