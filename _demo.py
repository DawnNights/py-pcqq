def isAdmin(session) -> bool:
    '''判断发送者是否为机器人管理者'''
    return session.event.UserID in session._driver_.AdminList


def isAtMe(session) -> bool:
    '''判断接收消息是否At机器人'''
    return '[PQ:at,qq=%d]' % (
        session.event.SelfID) in session.event.MessageText


def onlyGroup(session) -> bool:
    '''判断接收消息是否为群聊消息'''
    return session.event.GroupID != 0


def onlyPrivate(session) -> bool:
    '''判断接收消息是否为私聊消息'''
    return session.event.GroupID == 0


def checkUser(*userList: int):
    '''判断发送者是否在userList中'''
    def check(session):
        return session.event.UserID in userList

    return check


def checkType(*types: str):
    '''判断事件类型是否在types中'''
    def check(session):
        return session.event.EventType in types

    return check