import threading
import time

import docker
from flask import Flask, request

from edgeruler_code.execution import get_time
from edgeruler_code.utils import MySQLWriter, FileWriter


app = Flask(__name__)
self_containers = {}


@app.route('/')
def liveness_probe():
    return "server is alive."


@app.route('/pre/<string:func_id>')
def pre_func(func_id):
    if func_id == 'stress':
        print(f'pre:{self_containers.get("stress")}')
        container_list = self_containers.get("stress")
        flag = False
        if container_list is not None:
            if len(container_list) != 0:
                flag = True
        if flag is False:
            client = docker.from_env()
            self_containers["stress"] = []
            container = client.containers.run('leon/stress-ng-alpine:latest', stdin_open=True, detach=True,
                                              command='sh')
            print(f'{time.time()}create stress pre-warm successfully')
            self_containers["stress"].append(container)
            time.sleep(5)
            print(f'remove pre-warm container')
            self_containers["stress"].remove(container)
            container.remove(force=True)
    else:
        print("not stress")
    return "function {} is pre warmed".format(func_id)

client = docker.from_env()

@app.route('/func/<string:func_id>')
def call_func(func_id):
    writer = FileWriter('../../data/0516/http_breakdown/temp.txt', 'a')
    writer.write(f'3:{time.time()}', end=',')
    # mysql = MySQLWriter("10.214.131.191", "docker_log", "log", "1")
    req_no = request.args.get('req_no')
    # gate = time.time()

    # thread = threading.currentThread().ident
    # print(f'thread:{thread}')
    # print(func_id)
    if func_id == 'http':
        acc = time.time()
        client.containers.run('http:1.0', name=f'http_{req_no}')
        create_time, start_time, finish_time = get_time(container_name=f'http_{req_no}')
        container = client.containers.get(f'http_{req_no}')
        container.remove(force=True)
        print(f'{func_id} done!{finish_time - start_time}')
    elif func_id == 'http':
        acc = time.time()
        client.containers.run('darknet:1.0', command=f'../scripts/execute.sh 0 0', name=f'darknet_{req_no}',
                                          mounts=[docker.types.Mount(target="/mnt",
                                                                     source="/ifttt/utils/DeFog/DeFog",
                                                                     type='bind'),
                                                  docker.types.Mount(target="/log", source="/repos/edgeruler_evaluation/data/0516/darknet_log",
                                                                     type='bind')])
        create_time, start_time, finish_time = get_time(container_name=f'darknet_{req_no}')
        container = client.containers.get(f'darknet_{req_no}')
        container.remove(force=True)
        print(f'{func_id} done!{finish_time - start_time}')
    elif func_id == 'darknet':
        acc = time.time()
        client.containers.run('aeneas:1.0', command=f'../scripts/execute.sh 2 0', name=f'aeneas_{req_no}',
                              mounts=[docker.types.Mount(target="/mnt",
                                                         source="/ifttt/utils/DeFog/DeFog",
                                                         type='bind'),
                                      docker.types.Mount(target="/log",
                                                         source="/repos/edgeruler_evaluation/data/0516/darknet_log",
                                                         type='bind')])
        create_time, start_time, finish_time = get_time(container_name=f'aeneas_{req_no}')
        container = client.containers.get(f'aeneas_{req_no}')
        container.remove(force=True)
        print(f'{func_id} done!{finish_time - start_time}')
    else:
        print(func_id)
    writer.write(f'4:{acc}, 5:{acc + start_time - create_time}, 6:{acc + finish_time - create_time}}}', end=',')


    # # if func_id == 'sleep':
    # #     container = client.containers.run('sleep:1.0', command=f'python3 sleep.py --no {req_no}',
    # #                                       name=f'sleep_{req_no}')
    # # elif func_id == 'sleep1':
    # #     container = client.containers.run('sleep100:1.0', command=f'python3 sleep.py --no {req_no}',
    # #                                       name=f'{func_id}_{req_no}')
    # # elif func_id == 'sleep2':
    # #     container = client.containers.run('sleep100:1.1', command=f'python3 sleep.py --no {req_no}', name=f'{thread}')
    # # elif func_id == 'sleep3':
    # #     container = client.containers.run('sleep20:1.0', command=f'python3 sleep.py --no {req_no}', name=f'{thread}')
    # # elif func_id == 'sleep4':
    # #     container = client.containers.run('sleep20:1.0', command=f'python3 sleep.py --no {req_no}', name=f'{thread}')
    # # elif func_id == 'sleep5':
    # #     container = client.containers.run('sleep20:1.0', command=f'python3 sleep.py --no {req_no}', name=f'{thread}')
    # # elif func_id == 'sleep6':
    # #     container = client.containers.run('sleep20:1.0', command=f'python3 sleep.py --no {req_no}', name=f'{thread}')
    # # elif func_id == 'sleep7':
    # #     container = client.containers.run('sleep20:1.0', command=f'python3 sleep.py --no {req_no}', name=f'{thread}')
    # # elif func_id == 'darknet':
    # #     container = client.containers.run('darknet:1.0', command=f'../scripts/execute.sh 0 0', name=f'darknet_{req_no}',
    # #                                       mounts=[docker.types.Mount(target="/mnt",
    # #                                                                  source="/repos/ilm_execution/DeFog/DeFog",
    # #                                                                  type='bind'),
    # #                                               docker.types.Mount(target="/log", source="/repos/ilm_execution/log",
    # #                                                                  type='bind')])
    # # elif func_id == 'lamp':
    # #     container = client.containers.run('lamp:1.1', command=f'python3 turn_on_light.py --no {req_no}',
    # #                                       name=f'lamp_{req_no}')
    # # elif func_id == 'aeneas':
    # #     container = client.containers.run('aeneas:1.1', command=f'../scripts/execute.sh 2 0', name=f'aeneas_{req_no}',
    # #                                       mounts=[docker.types.Mount(target="/mnt",
    # #                                                                  source="/repos/ilm_execution/DeFog/DeFog",
    # #                                                                  type='bind'),
    # #                                               docker.types.Mount(target="/log", source="/repos/ilm_execution/log",
    # #                                                                  type='bind')])
    # # elif func_id == 'foglamp':
    # #     container = client.containers.run('foglamp:1.2', command=f'../scripts/execute.sh 3 0', name=f'foglamp_{req_no}',
    # #                                       mounts=[docker.types.Mount(target="/mnt",
    # #                                                                  source="/repos/ilm_execution/DeFog/DeFog",
    # #                                                                  type='bind'),
    # #                                               docker.types.Mount(target="/log", source="/repos/ilm_execution/log",
    # #                                                                  type='bind')])
    # # elif func_id == 'psphinx':
    # #     container = client.containers.run('psphinx:1.1', command=f'../scripts/execute.sh 1 0', name=f'psphinx_{req_no}',
    # #                                       mounts=[docker.types.Mount(target="/mnt",
    # #                                                                  source="/repos/ilm_execution/DeFog/DeFog",
    # #                                                                  type='bind'),
    # #                                               docker.types.Mount(target="/log", source="/repos/ilm_execution/log",
    # #                                                                  type='bind')])
    # # elif func_id == 'stress':
    # #     create_time = 0
    # #     start_time = 0
    # #     finish_time = 0
    # #     container_list = self_containers.get("stress")
    # #     print(f'call:{container_list}')
    # #     flag = False
    # #     if container_list is not None:
    # #         if len(container_list) != 0:
    # #             flag = True
    # #     if flag is True:
    # #         container = container_list[0]
    # #         start_time = time.time()
    # #         exec_output = container.exec_run('timeout -s KILL 0.8s stress-ng --cpu 1')
    # #         finish_time = time.time()
    # #         # container.remove(force=True)
    # #     else:
    # #         create_time = time.time()
    # #         container = client.containers.run('leon/stress-ng-alpine:latest', stdin_open=True, detach=True,
    # #                                           command='sh')
    # #         start_time = time.time()
    # #         exec_output = container.exec_run('timeout -s KILL 0.8s stress-ng --cpu 1')
    # #         finish_time = time.time()
    # #         container.remove(force=True)
    # print(f'create:{create_time}, start:{start_time}, finish:{finish_time}')
    # mysql.sql_exe(
    #     f'update latency_1 set gateway_func={gate}, create_ac={create_time}, start_ac={start_time}, finish_ac={finish_time} where req_no = {req_no};')

    # acc,acs,acf=get_time(container_name=f'{thread}')
    # # print(client.containers)

    # container = client.containers.get(f'{thread}')
    # print(container.remove(force=True))

    # args = {"gateway": f'{gate}', "ac_c":{acc},"ac_s":{acs},"ac_f":{acf}}
    # res = requests.get('http://10.214.131.119:9211/test', params=args)

    return "function {} is called".format(func_id)


if __name__ == '__main__':
    import os
    process_id = os.getpid()
    print(process_id)
    app.run(host='0.0.0.0', port=9211, threaded=True)
