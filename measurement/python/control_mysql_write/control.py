from flask import Flask
from flask import request
import time
import sys
import docker
import pymysql


app = Flask(__name__)
# 根路由，用来读取HTTP请求头数据
@app.route('/')
def index():
    # 读取HTTP请求头的User-Agent字段值
    user_agent = request.headers.get('User-Agent')
    return '<h1>Your browser is %s</h1>' % user_agent

# 用于读取GET请求数据的路由
@app.route('/sleep1000')
def time_record_1():
    t = time.time()
    no = request.args.get('no')
    client = docker.from_env()
    print(client.containers.run('sleep',command=f'python3 sleep.py --no {no}',name=f'sleep_{no}'))
    # log_write(f'receive time:{t}')
    mysql_db(no,t)
    #return
    return no

# 用于读取GET请求数据的路由
@app.route('/light')
def time_record_2():
    t = time.time()
    no = request.args.get('no')
    client = docker.from_env()
    print(client.containers.run('light_mysql',command=f'python3 turn_on_light.py --no {no}',name=f'light_{no}'))
    # log_write(f'receive time:{t}')
    mysql_db(no,t)
    #return
    return no

def mysql_db(no,t1):
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
            t=time.time()
            # 准备SQL语句
            sql = f'update log2 set recetime={t1} where no={no};';
            # sql = f'insert into log2(no,recetime) values ({no},{t1});'
            # 执行SQL语句
            cursor.execute(sql)
            # 执行完SQL语句后的返回结果都是保存在cursor中
            # 所以要从cursor中获取全部数据
            #datas = cursor.fetchall()
            conn.commit()
            print(f'update no{no}, recetime{t1}')
    except Exception as e:
        print("数据库操作异常：\n", e)
    finally:
        # 不管成功还是失败，都要关闭数据库连接
        conn.close()

__path__ = "./rece_log.txt"
def log_write(string):
    # make a copy of original stdout route
    stdout_backup = sys.stdout
    # define the log file that receives your log info
    log_file = open(__path__, "a")
    # redirect print output to log file
    sys.stdout = log_file
    print(string)
    # print("Now all print info will be written to message.log")
    # any command line that you will execute
    log_file.close()
    # restore the output to initial pattern
    sys.stdout = stdout_backup

# log_write()
def run_exe():
    time.sleep(0.01)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)

