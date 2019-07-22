"""
client

功能：根据用户输入发送请求，得到结果
"""
from socket import socket
import sys
# 让密码不可见
from getpass import *

# 创建tcp套接字
HOST = '127.0.0.1'
PORT = 8857
ADDR = (HOST, PORT)
socket_s = socket()
socket_s.connect(ADDR)


def do_query(name_):
    """
    单词查询
    """
    while True:
        word = input("单词:")
        # 输入##结束单词查询
        if word == '##':
            break
        msg = 'Q %s %s' % (name_, word)
        socket_s.send(msg.encode())
        data = socket_s.recv(2048).decode()
        print(data)


def do_history(name_):
    msg = 'H %s' % name_
    socket_s.send(msg.encode())
    data = socket_s.recv(128).decode()
    if data == 'OK':
        while True:
            data = socket_s.recv(1024).decode()
            if data == '##':
                break
            print(data)
    else:
        print("没有历史记录")


def login(name_):
    """
    二级界面，登录后的状态
    """
    while True:
        print("""
            **************Statement**************
            ****1.查单词   2.历史记录   3.注销****
            *************************************
        """)
        cmd = input("Please enter:")
        if int(cmd) == 1:
            do_query(name_)
        elif int(cmd) == 2:
            do_history(name_)
        elif int(cmd) == 3:
            return
        else:
            print("清输入正确的指令~~~")


def do_register():
    """
    注册信息
    """
    while True:
        name = input('User:')
        passwd = getpass()
        passwd1 = getpass('Again:')

        if passwd != passwd1:
            print("两次密码不一致~~~")
            continue
        # 判断用户名和密码是否有空格
        if ' ' in name or ' ' in passwd:
            print("用户名和密码不能有空格~~~")
            continue

        # 让消息前面加上请求数据类型
        msg = "R %s %s" % (name, passwd)
        # 将消息发送服务端
        socket_s.send(msg.encode())
        # 接受服务端反馈结果
        data = socket_s.recv(128).decode()
        if data == 'OK':
            print("注册成功")
        else:
            print("注册失败")
            # 注册失败原因
            print(data.encode())
        return


def do_login():
    """
    登录信息
    """
    name = input("User:")
    passwd = getpass()
    msg = "L %s %s" % (name, passwd)
    # 发送请求
    socket_s.send(msg.encode())
    # 接收服务端反馈信息
    data = socket_s.recv(128).decode()
    if data == 'OK':
        print("登录成功")
        login(name)
    else:
        print("登录失败")


def main():
    """
    客户端接口
    :return:
    """
    while True:
        print("""
            ************Welcome************
            ****1.注册   2.登录   3.退出****
            *******************************
        """)
        cmd = input("Please enter:")
        if int(cmd) == 1:
            do_register()
        elif int(cmd) == 2:
            do_login()
        elif int(cmd) == 3:
            socket_s.send(b'E')
            sys.exit("EXIT")
        else:
            print("清输入正确的指令~~~")


if __name__ == '__main__':
    main()
