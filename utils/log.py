import time

def Println(msg:str):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print(f"[{now} pcqq] INFO: {msg}")

def Panicln(err:str):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print(f"[{now} pcqq] WARNING: {err}")

def Fatalln(err:str):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print(f"[{now} pcqq] ERROR: {err}")
    input(); exit()