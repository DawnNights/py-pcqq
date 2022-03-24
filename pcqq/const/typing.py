MSG_TEXT = 0x01  # 纯文本
MSG_FACE = 0x02  # 表情
MSG_IMAGE_GROUP = 0X03  # 群聊图片
MSG_IMAGE_FRIEND = 0X06  # 私聊图片
MSG_XML = 0x14  # XML卡片
MSG_JSON = 0x25  # JSON卡片

STATE_ONLINE = 10   # 上线
STATE_LEAVE = 30    # 离开
STATE_INVISIBLE = 40    # 隐身
STATE_BUSY = 50  # 忙碌
STATE_CALLME = 60   # Q我吧
STATE_UNDISTURB = 70    # 请勿打扰

EVENT_GROUP_MSG = "0052"    # 群消息
EVENT_FRIEND_MSG = "00A6"   # 好友消息
EVENT_TEMP_MSG = "008D"  # 临时会话消息
EVENT_GROUP_INCREASE = "0021"   # 群人数增加
EVENT_GROUP_DECREASE = "0022"  # 群人数减少
EVENT_OTHRE = "02DC"  # 禁言、匿名等事件
