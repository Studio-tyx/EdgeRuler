import time

import numpy as np
import pika
from sklearn import linear_model

from edgeruler_code.utils import TDEngineTool, RuleTool
from edgeruler_code.utils.rule_tool import merge_trigger, single_trigger_is_triggered

FIXED_PREDICT_INTERVAL = 10


class Predictor:
    trigger_name = ''
    tdengine = TDEngineTool()
    rule_tool = RuleTool()

    def __init__(self, trigger_name):
        self.trigger_name = trigger_name

    def run(self, interval):
        while True:
            self.run_single()
            time.sleep(interval)

    def run_single(self):
        where_str = f"time <= '{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}'"
        data = self.tdengine.select_data_of_range(f"polled_rt_{self.trigger_name}", "data", where_str)
        # print(data)
        result = self.predict_data(data, FIXED_PREDICT_INTERVAL)
        events = self.generate_fake_event(result)
        for event in events:
            self.publish(event)

    def predict_data(self, data, interval):
        x_train_list = []
        y_train_list = []
        for x_key in data.keys():
            x_train_list.append(x_key)
            y_train_list.append(data[x_key])
        x_train = np.array(x_train_list).reshape((len(x_train_list), 1))
        y_train = np.array(y_train_list)
        linear_regressor = linear_model.LinearRegression()
        linear_regressor.fit(x_train, y_train)
        pred_start = x_train_list[len(x_train_list) - 1]
        x_pred = np.arange(pred_start, pred_start + interval, 1).reshape((interval, 1))
        y_pred = linear_regressor.predict(x_pred).reshape((interval, 1))
        result = np.append(x_pred, y_pred, axis=1)
        # print(rt_result)
        return result

    def generate_fake_event(self, predict):
        events = []
        triggers = self.rule_tool.get_event_from_trigger_name(self.trigger_name)
        if len(triggers) != 0:
            for trigger in triggers:
                occurrence = False
                for data in predict:
                    occurred = single_trigger_is_triggered(trigger, data[1])
                    if occurred and (not occurrence):
                        occurrence = True
                        events.append(f'{data[0]},{merge_trigger(trigger)}')
                    elif (not occurrence) and occurred:
                        occurrence = False
        return events

    def publish(self, event):
        user_info = pika.PlainCredentials('root', 'root')  # 用户名和密码
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('10.214.131.191', 5672, 'myvhost', user_info))  # 连接服务器上的RabbitMQ服务
        channel = connection.channel()
        channel.queue_declare(queue='pre')
        channel.basic_publish(exchange="", routing_key='pre', body=f'{event}')
        print(f'[Predictor] now:{time.time()}, predict event:{event}')


if __name__ == "__main__":
    predictor = Predictor('out_pres')
    predictor.run(1)
