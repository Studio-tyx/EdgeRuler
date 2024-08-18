from flask import Flask
from flask import request
import time
import sys
import docker
import pymysql

no = 22221119

app = Flask(__name__)
# 根路由，用来读取HTTP请求头数据
@app.route('/')
def index():
    print("touch index")
    # log_write("index")
    return "hello, world!"

@app.route('/test_get')
def test_get():
    str = request.args.get('id')
    # print("hey this is test_get")
    print(f'get {str}')
    id = int(str)
    # log_write(str)
    res = ""
    if id > 2:
        res = "id > 2"
    else:
        res = "id <= 2"
    print(res)
    return res
    # 读取HTTP请求头的User-Agent字段值
    # user_agent = request.headers.get('User-Agent')
    # return '<h1>Your browser is %s</h1>' % user_agent
    #return no

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

