import re as _re
import zlib as _zlib
import pcqq.binary as _binary
import urllib.request as _http

def Text(msgText:str)->bytes:
    '''
    封装文本消息
    :param msgText: 文本内容
    '''
    if msgText == "":
        return b''
        
    writer = _binary.Writer()
    msg = msgText.encode()

    writer.WriteByte(0x01)
    writer.WriteShort(len(msg) + 3)
    writer.WriteHex("01")
    writer.WriteShort(len(msg))
    writer.WriteBytes(msg)

    return writer.ReadAll()

_nickNameCache = {}
def _GetNickName(qq:int)->str:
    nickname = _nickNameCache.get(qq,"")
    if nickname == "":
        with _http.urlopen("http://r.qzone.qq.com/fcg-bin/cgi_get_score.fcg?mask=7&uins="+str(qq)) as rsp:
            page = rsp.read().decode()
        nickname = page[page.find(",\"")+2:page.rfind("\",")]
    return nickname

def At(qq:int, space:bool)->bytes:
    '''
    封装艾特消息
    :param qq: 艾特对象QQ号
    :param space: 是否在艾特后封装入空格
    '''
    if qq == -1:
        return b''
    
    writer = _binary.Writer()
    if qq != 0:
        nickname = "@"+_GetNickName(qq)
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
    else:
        writer.WriteArray(1, 0, 1, 0, 13, 64, 229, 133, 168, 228, 189, 147, 230, 136, 144, 229, 145, 152, 6, 0, 13, 0, 1, 0, 0, 0, 5, 1, 0, 0, 0, 0, 0, 0)
    
    if space:
        writer.WriteBytes(Text(" "))
    
    return writer.ReadAll()
    
    
def Face(faceID:int)->bytes:
    '''
    封装表情消息
    :param faceID: 表情ID
    '''
    if faceID == -1:
        return b''
    
    writer = _binary.Writer()
    msg = faceID.to_bytes(1,"big")

    writer.WriteByte(0x02)
    writer.WriteShort(len(msg) + 3)
    writer.WriteHex("01")
    writer.WriteShort(len(msg))
    writer.WriteBytes(msg)

    return writer.ReadAll()
    
def Xml(xmlText:str)->bytes:
    '''
    封装Xml卡片消息
    :param xmlText: xml卡片代码
    '''
    if xmlText == "":
        return b''

    writer = _binary.Writer()
    msg = _zlib.compress(xmlText.encode(),-1)

    writer.WriteByte(0x14)
    writer.WriteShort(len(msg)+11)
    writer.WriteHex("01")
    writer.WriteShort(len(msg)+1)
    writer.WriteHex("01")
    writer.WriteBytes(msg)
    writer.WriteBytes(b'\x02\x00\x04\x00\x00\x00\x02')

    return writer.ReadAll()

def Json(jsonText:str)->bytes:
    '''
    封装Json卡片消息
    :param jsonText: json卡片代码
    '''
    if jsonText == "":
        return b''

    writer = _binary.Writer()
    msg = _zlib.compress(jsonText.encode(),-1)

    writer.WriteByte(0x19)
    writer.WriteShort(len(msg)+11)
    writer.WriteHex("01")
    writer.WriteShort(len(msg)+8)
    writer.WriteBytes(b'\x9a\x03\xb0\x01\n\xad\x01\x01')
    writer.WriteBytes(msg)

    return writer.ReadAll()
    
def Music(title:str, author:str, url:str, audio:str, cover:str)->bytes:
    '''
    封装自定义音乐卡片消息
    :param title: 音乐标题
    :param author: 音乐作者
    :param url: 跳转链接
    :param audio: 音频链接
    :param cover: 封面链接
    '''
    return Xml(f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><msg serviceID=\"2\" templateID=\"1\" action=\"web\" brief=\"[分享] {title}\" sourceMsgId=\"0\" url=\"{url}\" flag=\"0\" adverSign=\"0\" multiMsgFlag=\"0\"><item layout=\"2\"><audio cover=\"{cover}\" src=\"{audio}\" /><title>{title}</title><summary>{author}</summary></item><source name=\"\" icon=\"\" action=\"\" appid=\"-1\" /></msg>")

def PQCode(source:str)->bytes:
    '''
    将源文本内的文本和PQ码封装为对应消息
    :param source: 源文本
    '''
    result = b''
    elems = _re.findall('\[PQ:(.+?)\]',source)

    for elem in elems:
        idx = source.find(elem) - 4
        result += Text(source[0:idx])
        source = source[idx+len(elem)+5:]
    
        pqParams = {}
        pqType = elem[0:elem.find(",")].lower()
        if pqType == "xml":
            pqParams["file"] = elem[elem.find(",")+1:]
        else:
            for param in elem[elem.find(",")+1:].split(","):
                key = param[0:param.find("=")]
                value = param[param.find("=")+1:].replace("&#44;",",")
                pqParams[key] = value

        
        if pqType == "at":
            result += At(int(pqParams.get("qq",-1)),True)
        elif pqType == "face":
            result += Face(int(pqParams.get("id",-1)))
        elif pqType == "xml":
            result += Xml(pqParams.get("file",""))
        elif pqType == "music":
            result += Music(
                pqParams.get("title",""),
                pqParams.get("author",""),
                pqParams.get("url",""),
                pqParams.get("audio",""),
                pqParams.get("cover",""),
                )
    
    if source != "":
        result += Text(source)

    return result