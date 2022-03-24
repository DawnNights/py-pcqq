import sys
import json
import base64
import random
import socket
import asyncio
from urllib import parse

import pcqq.utils as utils
import pcqq.const as const
import pcqq.logger as logger
import pcqq.binary as binary


class AsyncTCPClient:
    def __init__(self) -> None:
        domain = random.choice([
            "tcpconn.tencent.com",
            "tcpconn2.tencent.com",
            "tcpconn3.tencent.com",
            "tcpconn4.tencent.com"
        ])
        self.host: str = socket.gethostbyname(domain)
        self.port: int = const.TCP_PORT
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

    async def init(self) -> None:
        self.writer: asyncio.StreamWriter = None
        self.reader: asyncio.StreamReader = None
        self.reader, self.writer = await asyncio.open_connection(
            host=self.host,
            port=self.port,
            loop=self.loop
        )
        logger.info(f"正在创建 TCP 连接: {self.host}:{self.port} -> 成功")

    async def send(self, data: bytes) -> None:
        size = len(data) + 2
        self.writer.write(size.to_bytes(2, "big") + data)

    async def recv(self) -> bytes:
        data = await self.reader.read(const.BUF_SIZE)
        return data[2:]


class QQStruct:
    local_ip: bytes = b''

    server_ip: bytes = b''

    uin: int = 0

    password: bytes = b''

    nickname: str = ''

    is_scancode: bool = False

    login_time: bytes = b''

    redirection_times: int = 0

    redirection_history: bytes = b''

    tgt_key: bytes = b''

    tgtgt_key: bytes = b''

    session_key: bytes = b''

    bkn: int = 0

    skey: str = ''

    cookie: str = ''

    pckey_for_0819: bytes = b''

    pckey_for_0828_send: bytes = b''

    pckey_for_0828_recv: bytes = b''

    token_by_scancode: bytes = b''

    token_0038_from_0825: bytes = b''

    token_0038_from_0818: bytes = b''

    token_0038_from_0836: bytes = b''

    token_0088_from_0836: bytes = b''

    def save_token(self, path: str):
        file = open(path, mode='wb')

        file.write(b'DawnNights'.join([
            self.server_ip,
            self.uin.to_bytes(4, 'big'),
            self.nickname.encode(),
            self.token_0038_from_0836,
            self.token_0088_from_0836,
            self.pckey_for_0828_send,
            self.pckey_for_0828_recv
        ]))

        logger.info(f'已保存登录Token至文件 {path}')
        file.close()

    def load_token(self, path: str):
        file = open(path, mode='rb')
        tokens = file.read().split(b'DawnNights')

        self.pckey_for_0828_recv = tokens.pop()
        self.pckey_for_0828_send = tokens.pop()
        self.token_0088_from_0836 = tokens.pop()
        self.token_0038_from_0836 = tokens.pop()
        self.nickname = tokens.pop().decode()
        self.uin = int.from_bytes(tokens.pop(), 'big')
        self.server_ip = tokens.pop()

        logger.info(f'尝试通过 {path} 进行重连...')
        file.close()


class HttpResponse:
    ok: bool = False
    url: str = ""
    headers: dict = {}
    content: bytes = b""
    status_code: int = 0
    links: parse.ParseResult = None

    def __repr__(self):
        return "<%s Response %d>" % (
            self.links.scheme.upper(),
            self.status_code
        )

    def json(self) -> dict:
        return json.loads(self.content)

    def base64(self) -> str:
        return base64.b64encode(self.content).decode()


class QQClient(QQStruct):
    def __init__(self) -> None:
        self.waiter: dict = {}
        self.plugins: list = []
        self.client: AsyncTCPClient = AsyncTCPClient()
        self.teaer: binary.QQTea = binary.QQTea(bytes())

        self.tgt_key = utils.randbytes(16)
        self.server_ip = socket.inet_aton(self.client.host)

        def run_until_complete(coro):
            task = self.client.loop.create_task(coro)
            self.client.loop.run_until_complete(task)
            return task.result()
        self.run = run_until_complete

        def run_coroutine_threadsafe(coro):
            return asyncio.run_coroutine_threadsafe(
                coro=coro,
                loop=self.client.loop,
            )
        self.run_future = run_coroutine_threadsafe

        self.cache: utils.SqliteDB = utils.SqliteDB("cache.db")
        if self.cache.count("ginfo") == -1:
            self.cache.create(
                "ginfo",
                "name text", "owner integer",
                "group_id integer", "board text",
                "intro text", "mem_num integer"
            )
        if self.cache.count("gmember") == -1:
            self.cache.create(
                "gmember",
                "cord text",
                "user_id integer",
                "name text",
                "group_id integer",
                "op boolen"
            )

    async def write_packet(self, cmd: str, version: str, body: bytes, sequence: bytes = utils.randbytes(2)) -> None:
        writer = binary.Writer()
        writer.write_hex(const.HEADER)

        writer.write_hex(cmd)
        writer.write(sequence)
        writer.write_int32(self.uin)
        writer.write_hex(version)

        if self.session_key:
            writer.write(self.teaer.encrypt(body))
        else:
            writer.write(body)

        writer.write_hex(const.TAIL)
        await self.client.send(writer.clear())

    async def read_packet(self) -> tuple:
        reader = binary.Reader(await self.client.recv())
        reader.read(3)  # packet header

        cmd = reader.read_hex(2)
        sequence = reader.read(2)
        uin = reader.read_int32()  # qq uin
        reader.read(3)  # unknow

        if self.session_key:
            body = self.teaer.decrypt(reader.read()[:-1])
        else:
            body = reader.read()[:-1]

        return cmd, sequence, uin, body

    async def webget(self, url: str, headers: dict = {}, **params) -> HttpResponse:
        ret = parse.urlparse(url)
        if ret.scheme == "http":
            reader, writer = await asyncio.open_connection(
                host=ret.netloc,
                port=80,
            )
        elif ret.scheme == "https":
            reader, writer = await asyncio.open_connection(
                host=ret.netloc,
                port=443,
                ssl=True,
            )

        params = parse.urlencode(params)
        url = url + "?" + params if params else url
        request = f"GET {url} HTTP/1.1\r\n"

        headers["Host"] = ret.netloc
        headers["Connection"] = "close"
        for key, value in headers.items():
            request += f"{key}: {value}\r\n"
        writer.write((request + "\r\n").encode())

        response = HttpResponse()
        response.url = url
        response.links = ret

        # Response Status
        line = await reader.readline()
        response.status_code = int(line.split(b" ")[1])
        response.ok = response.status_code == 200

        # Response Headers
        line = (await reader.readline()).replace(b"\r\n", b"").decode()
        while line:
            key, value = line.split(": ")
            response.headers[key] = value
            line = (await reader.readline()).replace(b"\r\n", b"").decode()

        # Response Data
        response.content = await reader.read()

        writer.close()
        return response

    async def webpost(self, url: str, headers: dict = {}, **params) -> HttpResponse:
        ret = parse.urlparse(url)
        if ret.scheme == "http":
            reader, writer = await asyncio.open_connection(
                host=ret.netloc,
                port=80,
            )
        elif ret.scheme == "https":
            reader, writer = await asyncio.open_connection(
                host=ret.netloc,
                port=443,
                ssl=True,
            )
        else:
            raise Exception("调用方法 webpost 时传入的 url 参数有误")

        request = f"POST {url} HTTP/1.1\r\n"
        if "data" in params and isinstance(params["data"], bytes):
            post_data = params["data"]
        else:
            post_data = parse.urlencode(params).encode()

        headers["Host"] = ret.netloc
        headers["Connection"] = "close"
        headers["Content-Length"] = len(post_data)
        for key, value in headers.items():
            request += f"{key}: {value}\r\n"

        writer.write((request + "\r\n").encode() + post_data)

        response = HttpResponse()
        response.url = url
        response.links = ret

        # Response Status
        line = await reader.readline()
        response.status_code = int(line.split(b" ")[1])
        response.ok = response.status_code == 200

        # Response Headers
        line = (await reader.readline()).replace(b"\r\n", b"").decode()
        while line:
            key, value = line.split(": ")
            response.headers[key] = value
            line = (await reader.readline()).replace(b"\r\n", b"").decode()

        # Response Data
        response.content = await reader.read()

        writer.close()
        return response


sys.modules[__name__] = QQClient()
