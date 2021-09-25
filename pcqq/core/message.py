import re
import zlib
import pcqq.binary as binary

from .api import *

class MessageSegment(binary.Writer):
    def __init__(self, source='') -> None:
        super().__init__()
        self.source = ''

        if source:
            self.AddPQCode(source)

    def AddText(self, text: str):
        self.source += text
        msg = text.encode()

        self.WriteByte(0x01)
        self.WriteShort(len(msg) + 3)
        self.WriteHex("01")
        self.WriteShort(len(msg))
        self.WriteBytes(msg)

    def AddFace(self, id: int):
        self.source += f'[PQ:face,id={id}]'

        self.WriteByte(0x02)
        self.WriteShort(1 + 3)
        self.WriteHex('01')
        self.WriteShort(1)
        self.WriteBytes(id.to_bytes(1, 'big'))

    def AddAt(self, qq: int, nickname: str = ""):
        qq = int(qq)
        self.source += f'[PQ:at,qq={qq}]'
        if not nickname:
            nickname = GetNickName(qq)
        nickname = '@' + nickname

        writer = binary.Writer()
        writer.WriteBytes(b'\x00\x01\x00\x00')
        writer.WriteShort(len(nickname))
        writer.WriteBytes(b'\x00')
        writer.WriteInt(qq)
        writer.WriteBytes(b'\x00\x00')
        body = writer.ReadAll()

        nickname = nickname.encode()
        writer.WriteBytes(b'\x01')
        writer.WriteShort(len(nickname))
        writer.WriteBytes(nickname)
        writer.WriteBytes(b'\x06')
        writer.WriteShort(len(body))
        writer.WriteBytes(body)
        body = writer.ReadAll()

        writer.WriteByte(0x01)
        writer.WriteShort(len(body))
        writer.WriteBytes(body)

        self.WriteBytes(writer.ReadAll())
        self.AddText(' ')

    def AddXML(self, data: str):
        self.source += data

        body = zlib.compress(
            data.replace("&", "&amp;").replace("&#44;", ",").encode(), -1)

        self.WriteByte(0x14)
        self.WriteShort(len(body) + 11)
        self.WriteHex('01')
        self.WriteShort(len(body) + 1)
        self.WriteHex('01')
        self.WriteBytes(body)
        self.WriteArray(2, 0, 4, 0, 0, 0, 2)

    def AddJson(self, data: str):
        self.source += data

        body = zlib.compress(
            data.replace("&", "&amp;").replace("&#44;", ",").encode(), -1)

        self.WriteByte(0x25)
        self.WriteShort(len(body) + 11)
        self.WriteHex('01')
        self.WriteShort(len(body) + 8)
        self.WriteArray(154, 3, 176, 1, 10, 173, 1, 1)
        self.WriteBytes(body)

    def AddCustomMusic(self,
                       title: str = "",
                       content: str = "",
                       url: str = "",
                       audio: str = "",
                       cover: str = ""):
        self.AddXML(
            f'<?xml version=\'1.0\' encoding=\'UTF-8\' standalone=\'yes\' ?><msg serviceID="2" templateID="1" action="web" brief="[分享] {title}" sourceMsgId="0" url="{url}" flag="0" adverSign="0" multiMsgFlag="0"><item layout="2"><audio cover="{cover}" src="{audio}" /><title>{title}</title><summary>{content}</summary></item><source name="" icon="" action="" appid="-1" /></msg>'
        )

    def AddPQCode(self, source):
        matchReg = re.findall(r'\[PQ:\w+?.*?]', source)

        for matched in matchReg:
            idx = source.find(matched)
            self.AddText(source[0:idx])
            source = source[idx + len(matched):]

            pqtype = matched[4:matched.find(',')].lower()
            pqparams = dict(re.findall(r',([\w\-.]+?)=([^,\]]+)', matched))

            if pqtype == "face":
                self.AddFace(**pqparams)
            elif pqtype == "at":
                self.AddAt(**pqparams)
            elif pqtype == "xml":
                self.AddXML(**pqparams)
            elif pqtype == "json":
                self.AddJson(**pqparams)
            elif pqtype == "music":
                if pqparams.get('type', ''):
                    func = {'kuwo':kuwo, 'kugou':kugou, 'qqmusic': qqmusic, 'cloud163':cloud163}.get(pqparams['type'], None)
                    if func:
                        self.AddCustomMusic(**func(pqparams.get('keyword', '空')))
                else:
                    self.AddCustomMusic(**pqparams)

        if source:
            self.AddText(source)