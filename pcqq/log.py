import time

def Println(message:str):
    '''打印普通日志'''
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print(f'[pcqq] time="{now}" level=INFO msg="{message}"')

def Fatalln(exception:str):
    '''打印异常日志'''
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print(f'[pcqq] time="{now}" level=WARNING msg="{exception}"')

def Panicln(error:str):
    '''打印错误日志并退出程序'''
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print(f'[pcqq] time="{now}" level=ERROR msg="{error}"')
    input(); exit()