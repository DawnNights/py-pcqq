from dataclasses import dataclass

from core import croto

@dataclass
class QQStruct:
    addr: tuple = ()

    local_ip: bytes = b''

    server_ip: bytes = b''

    uin: int = 0

    password: bytes = b''

    nickname: str = ''

    is_scancode = True

    is_running = False

    login_time: bytes = b''

    ecdh: croto.ECDH = None
    
    path: str = ""

    redirection_times: int = 0

    redirection_history: bytes = b''

    tgt_key: bytes = b''

    tgtgt_key: bytes = b''

    session_key: bytes = b''

    offical: bytes = b''

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