import pcqq.client as cli
import pcqq.network as net
import pcqq.message as msg
import pcqq.logger as logger
# cli = cli.QQClient()


class Session:
    msg_id: int = 0
    timestamp: int = 0

    self_id: int = 0
    user_id: int = 0
    group_id: int = 0
    target_id: int = 0

    matched = None
    message: str = ""
    event_type: str = ""
    raw_message: list = []

    async def send_msg(self, *message):
        if self.group_id:
            await self.send_group_msg(self.group_id, *message)
        else:
            await self.send_friend_msg(self.user_id, *message)

    async def send_group_msg(self, group_id, *message):
        data = b""
        escape = ""
        has_image = False

        for seg in message:
            if isinstance(seg, str):
                escape += seg
                data += msg.text(seg)

            if isinstance(seg, dict) and "type" in seg:
                if seg["type"] == "at" and "qq" in seg:
                    data += await msg.at(int(seg["qq"]), group_id)
                    escape += f"[PQ:at,qq={seg['qq']}]"

                elif seg["type"] == "face" and "id" in seg:
                    data += msg.face(int(seg["id"]))
                    escape += f"[PQ:face,qq={seg['id']}]"
                elif seg["type"] == "xml" and "code" in seg:
                    data += msg.xml(seg["code"])
                    escape += f"[PQ:xml,code={seg['code']}]"
                elif seg["type"] == "music":
                    if "keyword" in seg:
                        data += await msg.qqmusic(str(seg["keyword"]))
                        escape += f"[PQ:music,keyword={seg['keyword']}]"
                    else:
                        del seg["type"]
                        data += msg.music(**seg)
                        escape += f"[PQ:music,{','.join([k+'='+v for k,v in seg.items()])}]"
                elif seg["type"] == "image":
                    if "data" in seg and isinstance(seg["data"], bytes):
                        image = msg.Image(seg["data"])

                    elif "url" in seg and seg["url"].startswith("http"):
                        image = msg.Image((await cli.webget(seg["url"])).content)
                    else:
                        continue

                    data += await msg.image_group(group_id, image)
                    escape += f"[PQ:image,file={image.hash.hex().upper()}]"
                    has_image = True

        await net.send_group_msg(group_id, data, has_image)
        logger.info(f"发送群消息: %s -> %s(%d)" % (
            escape, await net.get_group_cache(group_id), group_id
        ))

    async def send_friend_msg(self, user_id, *message):
        data = b""
        escape = ""
        has_image = False
        for seg in message:
            if isinstance(seg, str):
                escape += seg
                data += msg.text(seg)

            if isinstance(seg, dict) and "type" in seg:
                if seg["type"] == "face" and "id" in seg:
                    data += msg.face(int(seg["id"]))
                    escape += f"[PQ:face,qq={seg['id']}]"
                elif seg["type"] == "xml" and "code" in seg:
                    data += msg.xml(seg["code"])
                    escape += f"[PQ:xml,code={seg['code']}]"
                elif seg["type"] == "music":
                    if "keyword" in seg:
                        data += await msg.qqmusic(str(seg["keyword"]))
                        escape += f"[PQ:music,keyword={seg['keyword']}]"
                    else:
                        del seg["type"]
                        data += msg.music(**seg)
                        escape += f"[PQ:music,{','.join([k+'='+v for k,v in seg.items()])}]"
                elif seg["type"] == "image":
                    if "data" in seg and isinstance(seg["data"], bytes):
                        image = msg.Image(seg["data"])

                    elif "url" in seg and seg["url"].startswith("http"):
                        image = msg.Image((await cli.webget(seg["url"])).content)
                    else:
                        continue

                    data += await msg.image_friend(user_id, image)
                    escape += f"[PQ:image,file={image.hash.hex().upper()}]"
                    has_image = True

        await net.send_friend_msg(user_id, data, has_image)
        logger.info(f"发送好友消息: %s -> %s(%d)" % (
            escape, await net.get_user_cache(user_id), user_id
        ))
