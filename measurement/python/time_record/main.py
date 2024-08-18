import datetime
import subprocess
import json
import sys
import time

def get_time(container_name):
    cp=subprocess.run(["docker","inspect",container_name],capture_output=True,universal_newlines=True,check=True)
    # cp = subprocess.Popen("sudo  -S docker inspect ifttt-receiver-container", stdin=subprocess.PIPE,stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True,shell=True)
    js=json.loads(cp.stdout)
    dic=js[0]
    str1=dic['Created']
    str2=dic['State']['StartedAt']
    str1=str1.replace('T',' ').replace('Z','')
    str2 = str2.replace('T', ' ').replace('Z', '')
    time1=datetime.datetime.strptime(str1[0:26],'%Y-%m-%d %H:%M:%S.%f')
    time2 = datetime.datetime.strptime(str2[0:26], '%Y-%m-%d %H:%M:%S.%f')
    print(time1)
    timestamp1 = time.mktime(time1.timetuple())+time1.microsecond/1000000.0
    print(timestamp1)
    print(time2-time1)
    ret_time=time2-time1
    # log_write(f'{container_name},{time}')
    # log_write(container_name+","+time)
    return ret_time

__path__="/ifttt/log/record_time.txt"
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

def main():
    get_time(sys.argv[1])
    # print(sys.argv[1])


if __name__ == '__main__':
    main()


