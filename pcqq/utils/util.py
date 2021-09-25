import random
import hashlib


def HashMD5(src: bytes) -> bytes:
    bin = hashlib.md5(src).digest()
    return bin


def HexToBin(hex: str) -> bytes:
    size = len(hex.split(' '))
    hexa = hex.replace(' ', '')
    return int(hexa, 16).to_bytes(size, 'big')


def GetRandomBin(len: int) -> bytes:
    bin = [random.randint(0, 255) for _ in range(len)]
    return bytes(bin)