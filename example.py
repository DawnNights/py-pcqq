import pcqq


@pcqq.on_full("测试")
def TestPlugin(session: pcqq.Session):
    session.send_msg("这是一条测试消息")


@pcqq.on_fulls(["hello", "你好"])
def Hello(session: pcqq.Session):
    session.send_msg("你也好呀")


@pcqq.on_command("复读", prompt="请告诉我要复读的内容")
def Reread(session: pcqq.Session):
    session.send_msg(session.matched)


@pcqq.on_regex(r"^禁言\[PQ:at,qq=(\d{6,11})\] (\d{2,7})$")
def shutup(session: pcqq.Session):
    uid, time = session.matched[0]
    pcqq.set_group_shutup(session.group_id, int(uid), int(time))


pcqq.run_bot()
# pcqq.run_bot(uin=123456,password="123456")
# 如果选择账密登录就在传参中填入账号密码
# 无论是扫码登录还是账密登录，完成后都会保留登录token用于下次登录
