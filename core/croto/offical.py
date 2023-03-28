import ctypes
from hashlib import md5


def ulong_overflow(val):
    MAX = 2147483647
    if not -MAX-1 <= val <= MAX:
        val = (val + (MAX + 1)) % (2 * (MAX + 1)) - MAX - 1
    # return ctypes.c_ulong(val).value
    return ctypes.c_uint(val).value


def offical(data, key):
    eax = int.from_bytes(data[0:4], "big")
    esi = int.from_bytes(data[4:8], "big")

    var4 = int.from_bytes(key[0:4][::-1], "big")
    ebp = int.from_bytes(key[4:8][::-1], "big")
    var3 = int.from_bytes(key[8:12][::-1], "big")
    var2 = int.from_bytes(key[12:16][::-1], "big")

    edi = 0x9E3779B9
    ecx = edx = 0

    for _ in range(16):
        edx = esi
        ecx = esi

        edx = ulong_overflow(edx >> 5)
        ecx = ulong_overflow(ecx << 4)

        edx = ulong_overflow(edx + ebp)
        ecx = ulong_overflow(ecx + var4)

        edx = ulong_overflow(edx ^ ecx)
        ecx = ulong_overflow(esi + edi)

        edx = ulong_overflow(edx ^ ecx)
        eax = ulong_overflow(eax + edx)
        edx = eax
        ecx = eax

        edx = ulong_overflow(edx << 4)
        edx = ulong_overflow(edx + var3)
        ecx = ulong_overflow(ecx >> 5)
        ecx = ulong_overflow(ecx + var2)

        edx = ulong_overflow(edx ^ ecx)
        ecx = ulong_overflow(eax + edi)
        edx = ulong_overflow(edx ^ ecx)
        edi = edi - 0x61C88647
        esi = ulong_overflow(esi + edx)

    return eax.to_bytes(4, "big") + esi.to_bytes(4, "big")


def create_official(bufKey, bufSig, tgt_encrypt):
    MD5InfoCount = 4
    round = 256
    TmOffMod = 19
    TmOffModAdd = 5
    md5info = md5(bufKey).digest()
    md5info = md5info + md5(bufSig).digest()
    keyround = 480 % TmOffMod + TmOffModAdd
    seq = bytearray(256)
    ls = bytearray(256)
    off = bytearray(16)

    for i in range(round):
        seq[i] = i
        ls[i] = md5info[16 + (i % 16)]

    x = 0
    for i in range(round):
        x = (x + seq[i] + ls[i]) % round
        m = seq[x]
        seq[x] = seq[i]
        seq[i] = m

    x = 0
    for i in range(16):
        x = (x + seq[i + 1]) % round
        m = seq[x]
        seq[x] = seq[i + 1]
        seq[i + 1] = m

        v = (seq[x] + seq[i + 1]) % round + 1
        md5info = md5info + bytes([seq[v - 1] ^ md5info[i]])

    md5info = md5info + md5(tgt_encrypt).digest()
    MD5MD5info = md5(md5info).digest()
    M0 = MD5MD5info
    for i in range(keyround):
        M0 = md5(M0).digest()
    md5info = M0 + md5info[16:]

    t1 = MD5MD5info[:8]
    t2 = MD5MD5info[8:]

    for i in range(MD5InfoCount):
        lp = i * 16
        prekey = md5info[lp:]
        prekey = prekey[:17]

        KEY = bytes(0)
        a = 0
        while a < 16:
            KEY = KEY + bytes([prekey[a + 3]]) + bytes([prekey[a + 2]]) + \
                bytes([prekey[a + 1]]) + bytes([prekey[a + 0]])
            a += 4

        ii = offical(t1, KEY) + offical(t2, KEY)
        b = i

        while b < 16:
            off[b] = off[b] ^ ii[b]
            b += 1

    return md5(off).digest()
