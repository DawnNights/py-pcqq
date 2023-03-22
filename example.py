"""
Created on Wed Mar 2 at 22:14 2023

联系方式:
@QQ: 2224825532
@Github: https://github.com/DawnNights

"""

import default as pcqq

@pcqq.on_message()
async def speak(session: pcqq.Session):
    if session.message == "复读":
        sentence = await session.aget("请输入要复读的话")
        await session.send_msg(sentence)

pcqq.run_bot()
dict.setdefault