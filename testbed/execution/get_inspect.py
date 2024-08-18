import datetime
import json
import subprocess
import sys
import time

import pymysql


def get_time(container_name):
    cp = subprocess.run(["docker", "inspect", container_name], capture_output=True, universal_newlines=True, check=True)
    # cp = subprocess.run(["docker", "inspect", "ifttt-receiver-container"], capture_output=True, universal_newlines=True,check=True)
    # cp = subprocess.Popen("sudo  -S docker inspect ifttt-receiver-container", stdin=subprocess.PIPE,stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True,shell=True)
    js = json.loads(cp.stdout)
    dic = js[0]
    str1 = dic['Created']
    str2 = dic['State']['StartedAt']
    str3 = dic['State']['FinishedAt']
    str1 = str1.replace('T', ' ').replace('Z', '')
    str2 = str2.replace('T', ' ').replace('Z', '')
    str3 = str3.replace('T', ' ').replace('Z', '')
    time1 = datetime.datetime.strptime(str1[0:26], '%Y-%m-%d %H:%M:%S.%f')
    timestamp1 = time.mktime(time1.timetuple()) + time1.microsecond / 1000000.0
    time2 = datetime.datetime.strptime(str2[0:26], '%Y-%m-%d %H:%M:%S.%f')
    timestamp2 = time.mktime(time2.timetuple()) + time2.microsecond / 1000000.0
    time3 = datetime.datetime.strptime(str3[0:26], '%Y-%m-%d %H:%M:%S.%f')
    timestamp3 = time.mktime(time3.timetuple()) + time3.microsecond / 1000000.0
    # print(time.mktime(time2.timetuple()) + time1.microsecond / 1000000.0)
    # ▒~E~H import time ▒~D▒▒~P~N int(time.mktime(time.strptime('YYYY-MM-DD HH:MM:SS', '%Y-%m-%d %H:%M:%S')))
    # print(time2 - time1)
    res = time2 - time1
    # log_write(f'{container_name},{time}')
    # log_write(container_name+","+time)
    # underline_index = container_name.index('_')
    # no = int(container_name[underline_index + 1:])
    # log_write(f'{container_name},{timestamp1},{timestamp2},{container_name}')

    # mysql_db(no,timestamp1,timestamp2,timestamp3)
    # return res
    return timestamp1, timestamp2, timestamp3


__path__ = "/go/src/log/inspect_log.txt"


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


def mysql_db(no, t1, t2, t3):
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
            sql = f'update latency set create_ac={t1},start_ac={t2}, finish_ac={t3} where req_no={no};';
            cursor.execute(sql)
            # datas = cursor.fetchall()
            conn.commit()
            print(f'update no{no}, recetime{t1}')
    except Exception as e:
        print("▒~U▒▒~M▒▒~S▒~S~M▒~\▒~B常▒~Z\n", e)
    finally:
        conn.close()


def main():
    get_time(sys.argv[1])


if __name__ == '__main__':
    main()
