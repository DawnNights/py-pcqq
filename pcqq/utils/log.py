import time

def _print(msg:str, level:str):
    print(f'[pcqq] time="{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}" level={level} msg="{msg}"')

def debug(msg):
    _print(msg,"DEBUG")

def info(msg):
    _print(msg,"INFO")

def warning(msg):
    _print(msg,"WARNING")

def error(msg):
    _print(msg,"ERROR")
    input("\n")
    exit()