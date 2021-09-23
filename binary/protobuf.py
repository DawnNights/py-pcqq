def varInt(num: int) -> bytes:
    bin = bytes()
    while num > 127:
        bin += (0x80 | num & 0x7F).to_bytes(1, 'big')
        num = num >> 7
    bin += num.to_bytes(1, 'big')
    return bin


def toBytes(num: int) -> bytes:
    size = 1
    while num >= int.from_bytes(b'\xff' * size, 'big'):
        size += 1
    return num.to_bytes(size, 'big')

def protobufInt(v:int, mark:int)->bytes:
    return toBytes(8 * mark) + toBytes(v)

def protobufBytes(bin:bytes, mark:int)->bytes:
    return toBytes(2 + mark * 8) + toBytes(len(bin)) + bin

def protobufLongInt(v:int, mark:int)->bytes:
    return mark.to_bytes(1,'big') + varInt(v)