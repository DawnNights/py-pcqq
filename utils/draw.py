def get_char(r, g, b, alpha=256):
    """
    rbg 转字符
    :param r:
    :param g:
    :param b:
    :param alpha:
    :return:
    """
    if alpha == 0:
        return ' '
    gary = (2126 * r + 7152 * g + 722 * b) / 10000
    ascii_char = list("■□")
    # gary / 256 = x / len(ascii_char)
    x = int(gary / (alpha + 1.0) * len(ascii_char))
    return ascii_char[x]


def derw_QR(QR_Tab):
    tmp_text = ""
    print_tex = ""

    atrr = 7
    fore = 37
    back = 47
    color_block = "\x1B[%d;%d;%dm" % (atrr, fore, back)
    atrr = 0
    fore = 0
    back = 0
    color_none = "\x1B[%d;%d;%dm" % (atrr, fore, back)

    for loop in range(0, len(QR_Tab)):
        if QR_Tab[loop] == '■':
            tmp_text = "%s  \x1B[0m" % (color_block)
        elif QR_Tab[loop] == '□':
            tmp_text = "%s  \x1B[0m" % (color_none)
        else:
            tmp_text = "\n"

        print_tex = print_tex + tmp_text
    print(print_tex)


def DrawQrCode(path="Qrcode.jpg", length: int = 37):
    import PIL.Image as Image

    im = Image.open(path)
    im = im.resize((length, length), Image.NEAREST)
    txt = ''
    for i in range(length):
        for j in range(length):
            content = im.getpixel((j, i))
            if isinstance(content, int):
                content = (content, content, content)
            txt += get_char(*content)
        txt += '\n'
    derw_QR(txt)