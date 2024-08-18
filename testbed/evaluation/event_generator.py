import time

import pika

from edgeruler_code.utils import RuleTool, TDEngineTool, MySQLWriter, FileWriter
from edgeruler_code.utils.rule_tool import single_trigger_is_triggered

TRIGGERS_NAME = ['out_uv', 'out_ray', 'out_temp', 'out_humid', 'out_pres', 'in_uv', 'in_ray', 'in_temp', 'in_humid',
                 'in_pres']
EVENT_GENERATE_INTERVAL = 1


class EventGenerator:
    trigger_name = ""
    rule_tool = None
    tdengine = None
    no = 0

    def __init__(self, trigger_name):
        self.trigger_name = trigger_name
        self.rule_tool = RuleTool()
        self.tdengine = TDEngineTool()
        self.writer = FileWriter('../../data/0516/http_breakdown/temp.txt', 'a')

    def run(self, interval):
        return
        # while True:
        #     self.publish('out_pres>1012.3')
        #     time.sleep(interval)

    def actual_run(self, interval):
        print(f'[Event Generator] start running...')
        # interval = 0
        occurrence = False
        triggers = self.rule_tool.get_event_from_trigger_name(self.trigger_name)
        occurrence_dict = {}
        last_time = 0
        while True:
            for trigger in triggers:
                trigger_str = trigger.get("trigger_str")
                current_data = self.tdengine.select_last_data(f'polled_rt_{self.trigger_name}', 'data')
                this_time = self.tdengine.select_last_data(f'polled_rt_{self.trigger_name}', 'time')
                if this_time == last_time: continue
                last_time = this_time
                occurred = single_trigger_is_triggered(trigger, current_data)
                if occurrence_dict.get(trigger_str) is None:
                    occurrence_dict[trigger_str] = False
                else:
                    occurrence = occurrence_dict.get("trigger_str")
                if occurred and (not occurrence):
                    occurrence_dict[trigger_str] = True
                    self.publish(trigger_str)
                elif (not occurrence) and occurred:
                    occurrence_dict[trigger_str] = False
            time.sleep(interval)

    def publish(self, event):
        user_info = pika.PlainCredentials('root', 'root')  # 用户名和密码
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('10.214.131.191', 5672, 'myvhost', user_info))  # 连接服务器上的RabbitMQ服务
        channel = connection.channel()
        channel.queue_declare(queue='event')
        channel.basic_publish(exchange="", routing_key='event', body=f'{event},{self.no}, {time.time()}')
        self.writer.write(f'{{0:{time.time()}', end=',')
        self.no += 1

        print(f'[Event Generator] publish: {event}')


if __name__ == "__main__":
    event = EventGenerator('out_pres')
    event.run(1)
