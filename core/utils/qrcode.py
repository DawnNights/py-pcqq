import os
import platform
import subprocess


class QRCode:
    def __init__(self, path: str, data: bytes, qr_len=37) -> None:
        self.path = os.path.join(path, "QrCode.jpg")
        with open(self.path, mode="wb") as f:
            f.write(data)

        self.qr_len = qr_len

    def open_in_windows(self):
        return os.startfile(self.path)

    def open_in_linux(self):
        return subprocess.call(["xdg-open", self.path])

    def open_in_macos(self):
        return subprocess.call(["open", self.path])

    def print_in_terminal(self):
        from PIL import Image

        im = Image.open(self.path)
        im = im.resize((self.qr_len, self.qr_len), Image.NEAREST)

        txt = ''
        for i in range(self.qr_len):
            for j in range(self.qr_len):
                content = im.getpixel((j, i))
                if isinstance(content, int):
                    content = (content, content, content)
                txt += rgb_to_char(*content)
            txt += '\n'
        im.close()
        print(make_qrtex(txt))

    def auto_show(self):
        system = platform.system()
        try:
            # 用系统默认程序打开图片文件
            if system == "Windows":
                self.open_in_windows()
            elif system == "Linux":
                self.open_in_linux()
            elif system == "Darwin":
                self.open_in_macos()
            else:
                raise SystemError("This device system is unknown")
        except:
            # 使用pillow库在终端上打印二维码图片
            self.print_in_terminal()


def rgb_to_char(r, g, b, alpha=256):
    if alpha == 0:
        return ' '
    gary = (2126 * r + 7152 * g + 722 * b) / 10000
    ascii_char = list("■□")
    # gary / 256 = x / len(ascii_char)
    x = int(gary / (alpha + 1.0) * len(ascii_char))
    return ascii_char[x]


def make_qrtex(QR_Tab):
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

    return print_tex
