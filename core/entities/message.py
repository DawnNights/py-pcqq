from typing import List, Union
from dataclasses import dataclass
from abc import ABCMeta, abstractmethod

from core import utils


class BaseNode(metaclass=ABCMeta):
    @abstractmethod
    def format(self) -> str:
        """将该 Node 格式化为字符串"""
        pass

    @abstractmethod
    def encode(self) -> bytes:
        """将该 Node 编码成对应的协议源数据"""
        pass

    @abstractmethod
    def from_raw(self, raw_data: bytes):
        """解析协议源数据并返回对应的 Node 对象"""
        pass


@dataclass
class TextNode(BaseNode):
    text: str

    def format(self) -> str:
        return self.text

    def encode(self) -> bytes:
        stream = utils.Stream()
        body = self.text.encode()

        stream.write_byte(0x01)
        stream.write_int16(len(body) + 3)
        stream.write_byte(0x01)
        stream.write_int16(len(body))
        stream.write(body)

        return stream.read_all()

    def from_raw(raw_data: bytes):
        stream = utils.Stream(raw_data)
        text = stream.del_left(1).read_token().decode()

        if len(stream._raw) > 0:
            return AtNode.from_raw(raw_data)

        return TextNode(text)


@dataclass
class AtNode(BaseNode):
    uin: int
    name: str

    def format(self) -> str:
        return f"[PQ:at,qq={self.uin},name={self.name}]"

    def encode(self) -> bytes:
        stream = utils.Stream()
        name = "@" + self.name

        stream.write_hex("00 01 00 00")
        stream.write_int16(len(name))
        stream.write_hex("00")
        stream.write_int32(self.uin)
        stream.write_hex("00 00")
        body = stream.read_all()

        name = name.encode()
        stream.write_byte(0x01)
        stream.write_int16(len(name))
        stream.write(name)
        stream.write_byte(0x06)
        stream.write_int16(len(body))
        stream.write(body)
        body = stream.read_all()

        stream.write_byte(0x01)
        stream.write_int16(len(body))
        stream.write(body)

        return stream.read_all()

    def from_raw(raw_data: bytes):
        stream = utils.Stream(raw_data)

        stream.del_left(1)
        name = stream.read_token().decode()[1:]

        stream.del_left(10)
        uin = stream.read_int32()

        return AtNode(uin, name)


@dataclass
class FaceNode(BaseNode):
    id: int

    def format(self) -> str:
        return f"[PQ:face,id={self.id}]"

    def encode(self) -> bytes:
        stream = utils.Stream()

        stream.write_byte(0x02)
        stream.write_int16(1 + 3)
        stream.write_byte(0x01)
        stream.write_int16(1)
        stream.write_byte(self.id)

        return stream.read_all()

    def from_raw(raw_data: bytes):
        stream = utils.Stream(raw_data)
        face_id = stream.del_left(3).read_byte()

        return FaceNode(face_id)


@dataclass
class ImageNode(BaseNode):
    hash: str

    def format(self) -> str:
        return f"[PQ:image,url=https://gchat.qpic.cn/gchatpic_new/0/0-0-{self.hash}/0?term=3]"

    def encode(self) -> bytes:
        return b''

    def from_raw(raw_data: bytes):
        stream = utils.Stream(raw_data)

        stream.del_left(1)
        uuid = stream.read_token().decode().strip(" {}")
        hash = uuid.replace("-", "").upper()[:32]

        return ImageNode(hash)


MessageNode = Union[TextNode, AtNode, FaceNode, ImageNode]


class Message:
    def __init__(self):
        self.__nodes: List[MessageNode] = []

    def add(self, node: MessageNode):
        if isinstance(node, TextNode):
            pass
        elif isinstance(node, AtNode):
            pass
        elif isinstance(node, FaceNode):
            pass
        elif isinstance(node, ImageNode):
            pass
        else:
            raise ValueError("Message 添加的元素不是 MessageNode 包括的类型")

        self.__nodes.append(node)
        return self

    def format(self):
        format = ""

        for node in self.__nodes:
            format += node.format()
        return format
    
    def encode(self):
        raw_data = b''
        for node in self.__nodes:
            raw_data += node.encode()
        return raw_data

    def from_raw(raw_data: bytes):
        message = Message()
        stream = utils.Stream(raw_data)

        while len(stream._raw) > 3:
            node_type = stream.read_byte()
            node_raw = stream.read_token()

            if node_type == 0x01:  # 文本消息
                message.add(TextNode.from_raw(node_raw))
            elif node_type == 0x02:  # 表情消息
                message.add(FaceNode.from_raw(node_raw))
            elif node_type == 0x03:  # 群图片消息
                message.add(ImageNode.from_raw(node_raw))
            elif node_type == 0x06:  # 私聊图片消息
                message.add(ImageNode.from_raw(node_raw))

        return message