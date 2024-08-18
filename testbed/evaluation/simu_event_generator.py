import random
import time

import pika

from edgeruler_code.utils import FileWriter, DebugWriter


class SimuEventGenerator:
    # 确实应该要有valid time，但是这个东西和trigger generator本身无关，是和trigger相关的信息
    triggers = {1: {"name": "camera", "exe_time": 1, "valid_time": 1},
                2: {"name": "temperature", "exe_time": 0, "valid_time": 1},
                3: {"name": "humid", "exe_time": 0, "valid_time": 1},
                4: {"name": "psphinx", "exe_time": 3, "valid_time": 1},
                5: {"name": "simu_trigger1", "exe_time": 0, "valid_time": 1},
                6: {"name": "simu_trigger2", "exe_time": 0, "valid_time": 1},
                7: {"name": "simu_trigger3", "exe_time": 0, "valid_time": 1}}
    time_length = 0
    time = []
    total_length = 0

    def __init__(self, time_length):
        self.time_length = time_length
        self.total_length = time_length + 3
        for i in range(self.total_length):
            self.time.append("")

    '''
    distribute_type:
        AVG: average distribute     .#.#.#.#
        RAN: random distribute      .#####.#.
        CEN: central distribute     ###...###
    '''

    def generate_trigger(self, trigger_id, count, distribute_type):
        if trigger_id not in self.triggers:
            return
        else:
            if count > self.time_length:
                count = self.time_length
            trigger = self.triggers.get(trigger_id)
            if distribute_type == "AVG":
                interval = self.time_length // count
                time_point = 0
                i_count = 0
                while time_point < self.time_length and i_count < count:
                    if self.time[time_point].find(trigger.get("name")) == -1:
                        self.time[time_point + trigger.get("exe_time")] += (trigger.get("name") + ",")
                    time_point += interval
                    i_count += 1
            elif distribute_type == "RAN":
                i = 0
                while i < count:
                    time_point = random.randint(0, self.time_length) + trigger.get("exe_time")
                    if self.time[time_point].find(trigger.get("name")) == -1:
                        self.time[time_point] += (trigger.get("name") + ",")
                        i += 1
            elif distribute_type == "CEN":
                start = self.time_length // 2 - count // 2
                for i in range(count):
                    time_point = start + i + trigger.get("exe_time")
                    if self.time[time_point].find(trigger.get("name")) == -1:
                        self.time[time_point] += (trigger.get("name") + ",")

    def generate_single_event(self, trigger_time, trigger):
        if trigger_time > self.time_length:
            trigger_time = self.time_length
        self.time[trigger_time] = trigger

    def show_console(self):
        for i in range(self.total_length):
            print(str(i) + "," + self.time[i])

    def write_to_txt(self):
        file = FileWriter("./trigger_trace.txt", 'a')
        for i in range(self.total_length):
            file.write(str(i) + "," + self.time[i])

    def publish_to_rabbitmq(self, start_req_no):
        user_info = pika.PlainCredentials('root', 'root')  # 用户名和密码
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('10.214.131.191', 5672, 'myvhost', user_info))  # 连接服务器上的RabbitMQ服务

        channel = connection.channel()
        channel.queue_declare(queue='trigger')
        # start_req_no = 350
        # writer = MySQLWriter("10.214.131.191", "docker_log", "log", "1")
        writer = DebugWriter()
        for i in range(self.total_length):
            if self.time[i] != "":
                # TODO: trigger polling
                now = time.time()
                print(f'{now},{self.time[i]}')
                writer.write(f'update triggers set time={now},valid = 1 where name = "{self.time[i]}"')

                # TODO: add valid time to TDEngine
                t = time.time()
                writer.write(f'insert into latency (req_no,rabbit_send) values ({start_req_no},{t});')
                channel.basic_publish(exchange="", routing_key='trigger', body=f'{self.time[i]},{start_req_no}')
                start_req_no += 1
                # self.write_to_txt(f'{t},{self.time[i]}')
            time.sleep(1)

        writer.write(f'update triggers set valid = 0 where name != ""')
        writer.close()
