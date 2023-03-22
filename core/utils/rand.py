import random
import socket


def rand_bytes(size: int):
    return bytes([random.randint(0, 255) for _ in range(size)])


def rand_tcp_host():
    host = random.choice([
        "tcpconn.tencent.com",
        "tcpconn2.tencent.com",
        "tcpconn3.tencent.com",
        "tcpconn4.tencent.com"
    ])
    
    return socket.gethostbyname(host)


def rand_udp_host():
    host = random.choice([
        "sz.tencent.com",
        "sz2.tencent.com",
        "sz3.tencent.com",
        "sz4.tencent.com",
        "sz5.tencent.com",
        "sz6.tencent.com",
        "sz7.tencent.com",
        "sz8.tencent.com",
        "sz9.tencent.com",
    ])
    
    return socket.gethostbyname(host)