import time

import pika
import redis as Redis
import requests

from edgeruler_code.utils import BaseThread, MySQLWriter, FileWriter


class Evaluator:
    writer = FileWriter('../../data/0516/http_breakdown/temp.txt', 'a')
    redis = None
    connection = None
    data = []

    def __init__(self):
        self.redis = Redis.Redis(host='10.214.131.191', port=6379, db=0, decode_responses=True)
        user_info = pika.PlainCredentials('root', 'root')
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('10.214.131.191', 5672, 'myvhost', user_info))

    def run(self):
        channel = self.connection.channel()
        channel.queue_declare(queue='event')
        channel.basic_consume(queue='event', auto_ack=True, on_message_callback=self.callback)
        print('[Evaluator] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    def check_valid(self, trigger, rule):
        triggers = rule["Triggers"].split(',')
        triggers.remove(trigger)  # 去除掉当前valid的trigger
        for t in triggers:
            sql = f'select * from triggers where name = "{t}" and valid = 1;'
            # print(sql)
            self.writer = MySQLWriter("192.168.31.191", "docker_log", "log", "1")
            res = self.writer.write(sql)
            if res == 0:
                return False
        # TODO: add item to TDEngine
        # TODO: check condition
        return True

    def actuate_func(self, func_id, req_no, event_gene, rabbit_consume):
        # if req_no > 10:
        #     writer = FileWriter(f'../../data/test_multi_rule/multi_action_10.csv', 'a')
        #     for item in self.data:
        #         writer.write(f'{item[0]},{item[1]},{item[2]}')
        #     print("----------------------------------------------------------------------------------------------")
        #     print("-------------------------------------------------------------------------------------------------")
        func_id = func_id.replace(' ', '')
        function = self.redis.hgetall(func_id)
        func_name = function["name"]
        t = time.time()
        # writer = MySQLWriter("10.214.131.191", "docker_log", "log", "1")
        # writer.write(
        #     f'insert into latency_1 (req_no,event_generate,rabbit_consume,call_func) values ({req_no},{event_gene},{rabbit_consume},{t});')
        # print(f'insert into latency_1 (req_no,event_generate,rabbit_consume,call_func) values ({req_no},{event_gene},{rabbit_consume},{t});')
        self.data.append([event_gene, rabbit_consume, t])
        args = {"req_no": f'{req_no}'}
        print(f'[Evaluator] call: {func_name}')
        self.writer.write(f'2:{time.time()}', end=',')
        # res = requests.get('http://10.214.131.191:9211/func/{}'.format(func_name), params=args)
        # return res.text

    # from memory_profiler import profile
    # @profile
    # body: basic_publish发送的消息
    def callback(self, ch, method, properties, body):
        self.writer.write(f'1:{time.time()}', end=',')
        request = body.strip().decode('utf-8').split(',')
        print(f'[Evaluator] request:{request}')
        key = request[0]
        event_generate = request[2]
        no = int(request[1])
        consume_t = time.time()
        num_of_related_rules = self.redis.llen(key)  # 某个trigger对应的rules
        check_threads = []
        rules = []
        exec_threads = []
        for i in range(num_of_related_rules):
            rid = self.redis.lindex(key, i)  # rules集合中的某条rule
            rule = self.redis.hgetall(str(rid))
            t = BaseThread(target=self.check_valid, args=(key, rule,))
            check_threads.append(t)
            rules.append(rule)
            t.start()
        for i in range(num_of_related_rules):
            check_threads[i].join()
            if check_threads[i].get_result():
                actions = rules[i]["Actions"].split(',')
                for action in actions:
                    action = action.replace('\'', '')
                    t = BaseThread(target=self.actuate_func, args=(action, no, event_generate, consume_t,))
                    exec_threads.append(t)
                    t.start()
        for t in exec_threads:
            t.join()
            # TODO: use rabbitMQ to return the actuation id back to the user


