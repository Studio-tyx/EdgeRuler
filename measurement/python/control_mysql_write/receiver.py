from flask import Flask
from flask import request
import time
import sys
app = Flask(__name__)
# 根路由，用来读取HTTP请求头数据
@app.route('/')
def index():
    # 读取HTTP请求头的User-Agent字段值
    user_agent = request.headers.get('User-Agent')
    return '<h1>Your browser is %s</h1>' % user_agent

# 用于读取GET请求数据的路由
@app.route('/time_record')
def time_record():
    # 读取GET请求中的arg字段值
    no = request.args.get('no')
    run_exe()
    t = time.time()
    log_write(f'{t},{no}')
    return no

__path__ = "/ifttt/log/rece_log.txt"
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
    app.run(host='192.168.31.101',port=5000)
