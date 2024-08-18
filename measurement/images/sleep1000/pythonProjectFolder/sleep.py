import sys
import time

import click
import pymysql

__path__ = "./rece_log.txt"


def log_write(string):
    # make a copy of original stdout route
    stdout_backup = sys.stdout
    # define the log_1 file that receives your log_1 info
    log_file = open(__path__, "a")
    # redirect print output to log_1 file
    sys.stdout = log_file
    print(string)
    # print("Now all print info will be written to message.log_1")
    # any command line that you will execute
    log_file.close()
    # restore the output to initial pattern
    sys.stdout = stdout_backup


def mysql_db(no, t1, t2):
    # 连接数据库肯定需要一些参数
    conn = pymysql.connect(
        host="10.214.131.191",
        port=3306,
        database="docker_log",
        charset="utf8",
        user="log",
        passwd="1"
    )
    try:
        with conn.cursor() as cursor:
            t = time.time()
            # 准备SQL语句
            sql = f'update latency set first_line={t1}, last_line={t2} where req_no={no};';
            # 执行SQL语句
            cursor.execute(sql)
            # 执行完SQL语句后的返回结果都是保存在cursor中
            # 所以要从cursor中获取全部数据
            # datas = cursor.fetchall()
            conn.commit()
            # print("获取的数据：\n", datas)
    except Exception as e:
        print("数据库操作异常：\n", e)
    finally:
        # 不管成功还是失败，都要关闭数据库连接
        conn.close()


@click.command()
@click.option('--no', default=0, type=int)
def run(no):
    t1 = time.time()
    time.sleep(1)
    t2 = time.time()
    mysql_db(no, t1, t2)
    # log_write(f'starttime:{t1},endtime:{t2}')


if __name__ == '__main__':
    run()

