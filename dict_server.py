from socket import *  # TCP套接字
from multiprocessing import Process  # io并发
import signal  # 处理僵尸进程
import sys
from mysql import *  # 导入mysql模块中的操作数据库方法
import time

HOST = '0.0.0.0'
PORT = 8857
ADDR = (HOST, PORT)

# 建立数据库对象
db = Database(database='dict')


def do_register(connect_, data_):
    """
    服务端注册处理
    """
    tmp = data_.split(' ')
    name = tmp[1]
    passwd = tmp[2]
    # 返回True表示注册成功，False表示失败
    if db.register(name, passwd):
        connect_.send(b'OK')
    else:
        connect_.send(b'Fail')


def do_login(connect_, data_):
    """
    服务端登录处理
    """
    tmp = data_.split(' ')
    name = tmp[1]
    passwd = tmp[2]
    # 返回True表示注册成功，False表示失败
    if db.login(name, passwd):
        connect_.send(b'OK')
    else:
        connect_.send(b'Fail')


def do_history(connect_, data_):
    name = data_.split(' ')[1]
    his = db.history(name)
    if not his:
        connect_.send(b'Fail')
        return
    connect_.send(b'OK')

    for i in his:
        msg = '{}\t{}\t{}'.expandtabs(8).format(i[1],i[2],i[3])
        time.sleep(0.1)
        connect_.send(msg.encode())
    time.sleep(0.1)
    connect_.send(b'##')


def do_query(connect_, data_):
    """
    查询单词操作
    """
    tmp = data_.split(' ')
    name = tmp[1]
    word = tmp[2]

    # 插入历史记录
    db.insert_history(name, word)

    # 没找到返回None, 找到返回单词解释
    gloze = db.query(word)
    if not gloze:
        connect_.send("没有找到该单词".encode())
    else:
        msg = "%s : %s" % (word, gloze)
        connect_.send(msg.encode())


def request(connect_):
    """
    具体处理客户端请求
    """
    # 每个子进程单独生成游标操作数据库
    db.create_cursor()
    # 循环接收请求
    while True:
        data = connect_.recv(1024).decode()
        print(connect_.getpeername(), ':', data)
        if not data or data[0] == 'E':
            sys.exit("EXIT")
        elif data[0] == 'R':
            do_register(connect_, data)
        elif data[0] == 'L':
            do_login(connect_, data)
        elif data[0] == 'Q':
            do_query(connect_, data)
        elif data[0] == 'H':
            do_history(connect_, data)


def main():
    """
    创建服务端并发网络
    """

    # 创建套接字
    socket_s = socket()
    socket_s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    socket_s.bind(ADDR)
    socket_s.listen(7)

    # 处理僵尸进程
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    # 循环等待客户端连接
    print("Listen the port 8857")
    while True:
        try:
            connet, addr = socket_s.accept()
            print("Connect from ", addr)
        except KeyboardInterrupt:
            socket_s.close()
            db.close()
            sys.exit("EXIT Server")
        except Exception as e:
            print(e)
            continue

        # 为客户端创建子进程
        Process_p = Process(target=request, args=(connet,))
        Process_p.daemon = True
        Process_p.start()


if __name__ == '__main__':
    main()
