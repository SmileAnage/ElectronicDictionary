"""
数据库操作模块

分析：
将数据库操作封装一个类，将dict_server需要的数据库操作功能分别写入
方法，在dict_server中实例化对象,需要什么直接调用
"""
import pymysql
# 对密码进行加密处理
import hashlib

# md5加盐操作
SALT = '#!Ai'


class Database:
    """
    自定义数据库类
    """

    def __init__(self, host='localhost', port=3306, user='root', password='123456', charset='utf8', database=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.charset = charset
        self.database = database
        # 连接数据库
        self.connect_database()

    def connect_database(self):
        """
        连接数据库
        """
        self.db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                  charset=self.charset, database=self.database)

    def close(self):
        """
        关闭数据库连接
        """
        self.db.close()

    def create_cursor(self):
        """
        创建游标
        """
        self.cur = self.db.cursor()

    def register(self, name_, passwd_):
        """
        注册操作
        """
        sql = 'select * from user where name = "%s";' % name_
        self.cur.execute(sql)
        # 返回结果
        result = self.cur.fetchone()
        # 查找到则用户存在
        if result:
            return False

        # 密码加密存储处理
        hash = hashlib.md5((name_ + SALT).encode())  # 加盐处理
        hash.update(passwd_.encode())  # 算法加密
        passwd_ = hash.hexdigest()  # 加密后的密码

        # 插入数据库
        sql = 'insert into user (name, passwd) values (%s, %s);'
        try:
            self.cur.execute(sql, [name_, passwd_])
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def login(self, name_, passwd_):
        """
        登录处理
        """
        # 密码加密存储处理
        hash = hashlib.md5((name_ + SALT).encode())  # 加盐处理
        hash.update(passwd_.encode())  # 算法加密
        passwd_ = hash.hexdigest()  # 加密后的密码

        # 数据库比对
        sql = 'select * from user where name = "%s" and passwd = "%s"' % (name_, passwd_)
        self.cur.execute(sql)
        result = self.cur.fetchone()
        # 有数据则允许登录
        if result:
            return True
        else:
            return False

    def query(self, word_):
        """
        单词查询
        """
        sql = 'select gloze from words where word="%s";' % word_
        self.cur.execute(sql)
        result = self.cur.fetchone()
        # 如果找到 result --> gloze
        if result:
            return result[0]

    def history(self, name_):
        sql = 'select * from history where name="%s" order by time desc limit 10;' % name_
        self.cur.execute(sql)
        return self.cur.fetchall()
        
    def insert_history(self, name_, word_):
        """
        插入历史记录
        """
        sql = 'insert into history (name, word) values (%s, %s);'
        try:
            self.cur.execute(sql, [name_, word_])
            self.db.commit()
        except Exception:
            self.db.rollback()
