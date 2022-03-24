from typing import Any, List, Dict, Union


class Session:
    msg_id: int 
    timestamp: int

    self_id: int
    user_id: int
    group_id: int
    target_id: int

    matched: Any
    event_type: str
    message: str
    raw_message: List[Union[str, Dict[str, Any]]]

    async def send_msg(self, *message: Union[str, Dict[str, Any]]):
        """
        向事件来源发送消息, 发送文本消息直接传入字符串即可，特殊消息则需要使用 Dict 来表示

        :param message: 发送的消息(消息段以可变参数的形式传入)

        At -> {"type": "at", "qq": 被At人的账号}

        表情 -> {"type": "face", "id": 表情ID}

        卡片 -> {"type": "xml", "code": XML卡片代码}

        图片 -> {"type": "image", "data": 图片数据}

        网络图片 -> {"type": "image", "url": 图片直链}

        QQ音乐 -> {"type": "music", "keyword": 搜索关键词}

        自定义音乐 -> {"type": "music", "title": 音乐标题, "content": 音乐作者, "url": 跳转链接, "audio": 音频直链, "cover": 封面直链}

        """
    async def send_group_msg(self, group_id: int, *message: Union[str, Dict[str, Any]]):
        """
        发送群消息, 发送文本消息直接传入字符串即可，特殊消息则需要使用 Dict 来表示

        :param group_id: 指定群号

        :param message: 发送的消息(消息段以可变参数的形式传入)

        At -> {"type": "at", "qq": 被At人的账号}

        表情 -> {"type": "face", "id": 表情ID}

        卡片 -> {"type": "xml", "code": XML卡片代码}

        图片 -> {"type": "image", "data": 图片数据}

        网络图片 -> {"type": "image", "url": 图片直链}

        QQ音乐 -> {"type": "music", "keyword": 搜索关键词}

        自定义音乐 -> {"type": "music", "title": 音乐标题, "content": 音乐作者, "url": 跳转链接, "audio": 音频直链, "cover": 封面直链}

        """

    async def send_friend_msg(self, user_id: int, *message: Union[str, Dict[str, Any]]):
        """
        发送好友消息, 发送文本消息直接传入字符串即可，特殊消息则需要使用 Dict 来表示

        :param group_id: 好友账号

        :param message: 发送的消息(消息段以可变参数的形式传入)

        表情 -> {"type": "face", "id": 表情ID}

        卡片 -> {"type": "xml", "code": XML卡片代码}

        图片 -> {"type": "image", "data": 图片数据}

        网络图片 -> {"type": "image", "url": 图片直链}

        QQ音乐 -> {"type": "music", "keyword": 搜索关键词}

        自定义音乐 -> {"type": "music", "title": 音乐标题, "content": 音乐作者, "url": 跳转链接, "audio": 音频直链, "cover": 封面直链}

        """
