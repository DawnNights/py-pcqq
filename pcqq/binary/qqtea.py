import struct


def xor(a, b) -> bytes:
    op = 0xffffffff
    a1, a2 = struct.unpack(b'>LL', a[0:8])
    b1, b2 = struct.unpack(b'>LL', b[0:8])
    return struct.pack(b'>LL', (a1 ^ b1) & op, (a2 ^ b2) & op)


def code(v, k) -> bytes:
    n = 16
    op = 0xffffffff
    delta = 0x9e3779b9
    k = struct.unpack(b'>LLLL', k[0:16])
    y, z = struct.unpack(b'>LL', v[0:8])
    s = 0
    for _ in range(n):
        s += delta
        y += (op & (z << 4)) + k[0] ^ z + s ^ (op & (z >> 5)) + k[1]
        y &= op
        z += (op & (y << 4)) + k[2] ^ y + s ^ (op & (y >> 5)) + k[3]
        z &= op
        r = struct.pack(b'>LL', y, z)
    return r


def decipher(v, k):
    n = 16
    op = 0xffffffff
    y, z = struct.unpack(b'>LL', v[0:8])
    a, b, c, d = struct.unpack(b'>LLLL', k[0:16])
    delta = 0x9E3779B9
    s = (delta << 4) & op
    for _ in range(n):
        z -= ((y << 4) + c) ^ (y + s) ^ ((y >> 5) + d)
        z &= op
        y -= ((z << 4) + a) ^ (z + s) ^ ((z >> 5) + b)
        y &= op
        s -= delta
        s &= op
    return struct.pack(b'>LL', y, z)


def TeaEncrypt(body: bytes, key: bytes) -> bytes:
    END_CHAR = b'\0'
    FILL_N_OR = 0xF8
    vl = len(body)
    filln = (8 - (vl + 2)) % 8 + 2
    fills = b''
    for i in range(filln):
        fills = fills + bytes([220])
    body = (bytes([(filln - 2) | FILL_N_OR])
            + fills
            + body
            + END_CHAR * 7)
    tr = b'\0' * 8
    to = b'\0' * 8
    r = b''
    o = b'\0' * 8
    for i in range(0, len(body), 8):
        o = xor(body[i:i + 8], tr)
        tr = xor(code(o, key), to)
        to = o
        r += tr
    return r


def TeaDecrypt(body: bytes, key: bytes) -> bytes:
    l = len(body)
    prePlain = decipher(body, key)
    pos = (prePlain[0] & 0x07) + 2
    r = prePlain
    preCrypt = body[0:8]
    for i in range(8, l, 8):
        x = xor(decipher(xor(body[i:i + 8], prePlain), key), preCrypt)
        prePlain = xor(x, preCrypt)
        preCrypt = body[i:i + 8]
        r += x
    if r[-7:] != b'\0' * 7:
        return None
    return r[pos + 1:-7]
