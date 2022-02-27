import sys
import threading

import pcqq.utils as utils
import pcqq.const as const
import pcqq.binary as binary
import pcqq.logger as logger


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

    httper: utils.Httper = None

    waiter: utils.Waiter = utils.Waiter()

    pckey_for_0819: bytes = b''

    pckey_for_0828_send: bytes = b''

    pckey_for_0828_recv: bytes = b''

    token_by_scancode: bytes = b''

    token_0038_from_0825: bytes = b''

    token_0038_from_0818: bytes = b''

    token_0038_from_0836: bytes = b''

    token_0088_from_0836: bytes = b''

    def __init__(self, cli: utils.Client) -> None:
        self.cli = cli
        self.server_ip = self.cli.inet
        self.tgt_key = utils.randbytes(16)

        self.tea: binary.QQTea = None
        logger.info(f"正在创建 {cli.kind} 网络通讯 -> {cli.host}")

    def run_thread(self, target, *args) -> None:
        thread = threading.Thread(target=target, args=args)
        thread.start()

    def send_packet(self, cmd: str, version: str, *bins: bytes, sequence:bytes=utils.randbytes(2)) -> None:
        writer = binary.Writer()
        writer.write_hex(const.HEADER)

        writer.write_hex(cmd)
        writer.write(sequence)
        writer.write_int32(self.uin)
        writer.write_hex(version)

        if self.session_key:
            writer.write(self.tea.encrypt(b''.join(bins)))
        else:
            writer.write(b''.join(bins))

        writer.write_hex(const.TAIL)
        self.cli.send(writer.clear())

    def save_token(self, path: str = 'session.token'):
        with open(path, mode='wb') as f:
            f.write(b'DawnNights'.join([
                self.server_ip,
                self.uin.to_bytes(4, 'big'),
                self.nickname.encode(),
                self.token_0038_from_0836,
                self.token_0088_from_0836,
                self.pckey_for_0828_send,
                self.pckey_for_0828_recv
            ]))
        logger.info(f'已保存登录Token至文件 {path}')

    def load_token(self, path: str = 'session.token'):
        with open(path, mode='rb') as f:
            tokens = f.read().split(b'DawnNights')

        self.server_ip = tokens.pop(0)
        self.uin = int.from_bytes(tokens.pop(0), 'big')
        self.nickname = tokens.pop(0).decode()
        self.token_0038_from_0836 = tokens.pop(0)
        self.token_0088_from_0836 = tokens.pop(0)
        self.pckey_for_0828_send = tokens.pop(0)
        self.pckey_for_0828_recv = tokens.pop(0)
        logger.info(f'尝试通过 {path} 进行重连...')


try:
    sys.modules[__name__] = QQStruct(utils.TCPClient())  # 使用 TCP 客户端
    # sys.modules[__name__] = QQStruct(utils.UDPClient()) # 使用 UDP 客户端
except:
    sys.exit("ERROR: 客户端连接超时, 请检查网络环境并重新运行")
