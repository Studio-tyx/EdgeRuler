import pymysql
import time


# 定义一个函数
# 这个函数用来创建连接(连接数据库用）
def mysql_db():
    # 连接数据库肯定需要一些参数
    conn = pymysql.connect(
        host="192.168.31.101",
        port=3306,
        database="docker_log",
        charset="utf8",
        user="log",
        passwd="1"
    )
    try:
        with conn.cursor() as cursor:
            t=time.time()
            # 准备SQL语句
            sql = f'insert into log1 (no,sendtime) values (3,{t});';
            # 执行SQL语句
            cursor.execute(sql)
            # 执行完SQL语句后的返回结果都是保存在cursor中
            # 所以要从cursor中获取全部数据
            #datas = cursor.fetchall()
            conn.commit()
            #print("获取的数据：\n", datas)
    except Exception as e:
        print("数据库操作异常：\n", e)
    finally:
        # 不管成功还是失败，都要关闭数据库连接
        conn.close()


if __name__ == '__main__':
    mysql_db()
