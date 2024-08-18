from datetime import datetime

import pika
import redis as Redis
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from edgeruler_code.utils import BaseThread


class Scheduler:
    user_info = pika.PlainCredentials('root', 'root')
    connection = pika.BlockingConnection(pika.ConnectionParameters('10.214.131.191', 5672, 'myvhost', user_info))
    scheduler = BackgroundScheduler()
    jobs = {}
    redis = Redis.Redis(host='10.214.131.191', port=6379, db=0, decode_responses=True)

    def callback(self, ch, method, properties, body):
        request = body.strip().decode('utf-8').split(',')
        timestamp = request[0]
        trigger = request[1]
        timestamp = float(timestamp)
        date_time_1 = datetime.utcfromtimestamp(timestamp)

        if trigger in self.jobs.keys():
            if self.scheduler.get_job(job_id=f'{self.jobs[trigger]}_{trigger}') != None:
                self.scheduler.remove_job(job_id=f'{self.jobs[trigger]}_{trigger}')
            self.scheduler.add_job(self.job_func, 'date', run_date=date_time_1, timezone='UTC', args=[trigger],
                                   id=f'{timestamp}_{trigger}')
            self.jobs[trigger] = timestamp
        else:
            self.scheduler.add_job(self.job_func, 'date', run_date=date_time_1, timezone='UTC', args=[trigger],
                                   id=f'{timestamp}_{trigger}')
            self.jobs[trigger] = timestamp

    def run(self):
        channel = self.connection.channel()
        self.scheduler.start()
        channel.queue_declare(queue='pre')
        channel.basic_consume(queue='pre', auto_ack=True, on_message_callback=self.callback)
        print('[scheduler run] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    def job_func(self, key):
        # TODO: send message to api gateway
        num_of_related_rules = self.redis.llen(key)  # 某个trigger对应的rules
        # rules = []
        exec_threads = []
        for i in range(num_of_related_rules):
            rid = self.redis.lindex(key, i)  # rules集合中的某条rule
            rule = self.redis.hgetall(str(rid))
            actions = rule["Actions"].split(',')
            for action in actions:
                action = action.replace('\'', '')
                t = BaseThread(target=self.send_pre, args=(action,))
                exec_threads.append(t)
                t.start()
        for t in exec_threads:
            t.join()

    def send_pre(self, func_id):
        func_id = func_id.replace(' ', '')
        function = self.redis.hgetall(func_id)
        func_name = function["name"]
        print(f'[Scheduler] pre call: {func_name}')
        # print(f'http://10.214.131.191:9211/pre/{func_name}')
        res = requests.get('http://10.214.131.191:9211/pre/{}'.format(func_name))
        # return res.text


if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.run()
