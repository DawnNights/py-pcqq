import ctypes
import random
import hashlib


def memwrite(dest: bytearray, i: int, value: bytes):
    for i2 in range(len(value)):
        dest[i + i2] = value[i2]


def memset(dest: bytearray, value: int):
    for i in range(len(dest)):
        dest[i] = value

# ------------------------------------------


def md5(src: bytes):
    return hashlib.md5(src).digest()


def sha256(data: bytes, val: bytes):
    v17 = bytearray(8)

    memwrite(v17, 0, (953751936).to_bytes(4, "little"))
    memwrite(v17, 4, (27660).to_bytes(2, "little"))
    memwrite(v17, 6, (28329).to_bytes(2, "little"))

    v7 = bytearray(hashlib.sha1(data).digest())
    v9 = len(v7)

    v8 = 0
    while v7 != bytearray(0):
        b = v7[v8] ^ (val[v8 % 20] + v17[v8 % 7])
        v7[v8] = ctypes.c_ubyte(b).value

        v8 += 1
        if v8 >= v9:
            break

    return bytes(v7)


def sha512(data: bytes, val: bytes):
    v7 = bytearray(64)
    v11 = bytearray(8)
    v15 = bytearray(64)
    v19 = bytearray(64)

    memwrite(v11, 0, (1980729049).to_bytes(4, "little"))
    memwrite(v11, 4, (22840).to_bytes(2, "little"))
    memwrite(v11, 6, (108).to_bytes(1, "little"))

    memwrite(v7, 0, val)
    memset(v19, 22)
    memset(v15, 60)

    for i in range(64):
        v19[i] = v19[i] ^ v7[i]
        v15[i] = v15[i] ^ v7[i]

    v18 = hashlib.sha256(bytes(v19) + data).digest()
    v20 = bytearray(hashlib.sha256(v15 + v18[:36]).digest())

    v9 = 0
    while v20 != bytearray(0):
        b = v20[v9] ^ v11[v9 % 7]
        v20[v9] = ctypes.c_ubyte(b).value
        v9 += 1

        if v9 >= 32:
            break

    return bytes(v20)


def sha1024(data: bytes, val: bytes):
    v22 = bytearray(7)
    v25 = bytearray(5)

    memwrite(v22, 0, (249112998).to_bytes(4, "little"))
    memwrite(v22, 4, (39555).to_bytes(2, "little"))
    memwrite(v22, 6, (194).to_bytes(1, "little"))

    memwrite(v25, 0, (2840686918).to_bytes(4, "little"))
    memwrite(v25, 4, (33).to_bytes(1, "little"))

    v16 = bytearray(hashlib.sha1(data).digest())
    v9 = len(v16)
    v8 = 0

    while v16 != bytearray(0):
        b = v16[v8] ^ (v8 + val[v8 % 20] + v25[v8 % 5] + v22[v8 % 7])
        v16[v8] = ctypes.c_ubyte(b).value

        v8 += 1
        if v8 >= v9:
            break

    return bytes(v16)


def rand_str(v1_3: bytearray):
    v1 = bytearray(10)
    memset(v1, 11)

    v3 = bytearray(20)
    memset(v3, 12)
    memwrite(v3, 0, (16204).to_bytes(2, "little"))
    memwrite(v3, 2, (928279336).to_bytes(4, "little"))
    memwrite(v3, 6, (610353194).to_bytes(4, "little"))

    v16 = bytearray(10)
    memwrite(v16, 0, (24896).to_bytes(2, "little"))
    memwrite(v16, 2, (910043961).to_bytes(4, "little"))
    memwrite(v16, 6, (1327901016).to_bytes(4, "little"))

    v11 = bytes([97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 111, 112, 113, 114, 115, 116, 117,
                118, 119, 120, 121, 122, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 65, 66, 67, 68, 69, 69, 70, 71, 77, 78])
    v2 = 3
    while True:
        v1[v2] = v11[random.randint(0, 32767) % 44]
        v2 += 1
        if v2 > 9:
            break
    v1[0] = v1[3]
    v1[1] = v1[6]
    v1[2] = v1[9]

    v7 = 7
    while True:
        v8 = v7 - 7
        if v8 >= 7:
            break

        v3[v7] = v16[v8] ^ v1[v8]

        v7 += 1
        if v7 >= 19:
            break
    v1_3.clear()
    v1_3 += v3[-2:] + v3[:18]
    return bytes(v1)


def rand_str2(v1_3: bytearray):
    v1 = bytearray(10)
    memset(v1, 13)

    v3 = bytearray(20)
    memset(v3, 13)
    memwrite(v3, 0, (16204).to_bytes(2, "little"))
    memwrite(v3, 2, (928279336).to_bytes(4, "little"))
    memwrite(v3, 6, (610353194).to_bytes(4, "little"))

    v16 = bytearray(10)
    memwrite(v16, 0, (24896).to_bytes(2, "little"))
    memwrite(v16, 2, (910043961).to_bytes(4, "little"))
    memwrite(v16, 6, (1327901016).to_bytes(4, "little"))

    v11 = bytes([97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 111, 112, 113, 114, 115, 116, 117,
                118, 119, 120, 121, 122, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 65, 66, 67, 68, 69, 69, 70, 71, 77, 78])
    v2 = 3
    while True:
        v1[v2] = v11[random.randint(0, 32767) % 44]
        v2 += 1
        if v2 > 9:
            break
    v1[0] = v1[3]
    v1[1] = v1[6]
    v1[2] = v1[9]

    v7 = 7
    while True:
        v8 = v7 - 7
        if v8 >= 7:
            break

        v3[v7] = v16[v8] ^ v1[v8]

        v7 += 1
        if v7 >= 19:
            break
    v1_3.clear()
    v1_3 += v3[-2:] + v3[:18]
    return bytes(v1)


def sub_16F90(data: bytes, v1: bytearray, fix: bytes, v1_3: bytes):
    if len(v1) == 0:
        v1 += bytearray(rand_str(v1_3))

    v28 = sha256(data, fix)
    v28 += sha512(data, fix)

    return v28[:40]
