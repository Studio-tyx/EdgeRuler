import random
import time

import numpy
import math
import pandas as pd
import matplotlib.pyplot as plt

from edgeruler_code.comp.stepconf_single import StepConfPerEsti
from edgeruler_code.emulation import Evaluator, Resource

from edgeruler_code.event_predictor import OnDemandPred, LinearPred, RTPred
from edgeruler_code.utils import TDEngineTool


def import_data(rules_number, events_number):
    triggers_value = []
    random.seed(329)
    trigger_name = 'out_temp'
    table_name = 'triggers_rt'
    tdengine = TDEngineTool()
    model_data = []
    t = 0
    raw_data = tdengine.select_by_str(f'SELECT {trigger_name} FROM {table_name} WHERE time <= "2017-04-22 08:00:00.000"')
    while t < len(raw_data):
        model_data.append([t, raw_data[t][0]])
        t += 1
    max_data = tdengine.select_by_str(f'SELECT MAX({trigger_name}) FROM {table_name} WHERE time >= "2017-04-23 08:00:00.000" and time <= "2017-04-23 09:00:00.000"')
    min_data = tdengine.select_by_str(f'SELECT MIN({trigger_name}) FROM {table_name} WHERE time >= "2017-04-23 08:00:00.000" and time <= "2017-04-23 09:00:00.000"')
    i = 0
    # print(f'min:{min_data}, max:{max_data}')
    while i < rules_number:
        trigger_value = random.uniform(min_data[0][0], max_data[0][0])
        trigger_value = round(trigger_value, 1)
        if trigger_value in triggers_value:
            continue
        triggers_value.append(trigger_value)
        i += 1
    print(triggers_value)
    trigger_points = [[] for _ in range(rules_number)]
    sensor_values = []
    raw_data = tdengine.select_by_str(f'SELECT {trigger_name} FROM {table_name} WHERE time >= "2017-04-23 07:30:00.000"')
    events_finish = [False] * rules_number
    j = 0
    while True:
        sensor_value = raw_data[j][0]
        sensor_values.append([t, sensor_value])
        for i in range(rules_number):
            if sensor_value >= triggers_value[i] and events_finish[i] is False:
                if t == len(model_data):
                    trigger_points[i].append(t)
                else:
                    if sensor_values[j - 1][1] < triggers_value[i] <= sensor_value:
                        trigger_points[i].append(t)
            if len(trigger_points[i]) >= events_number:
                events_finish[i] = True
        if all(events_finish) is True:
            break
        j += 1
        t += 1
    # draw_pic(model_data, sensor_values, triggers_value)
    return model_data, sensor_values, trigger_points, triggers_value


def draw_pic(model_data, sensor_value, triggers_value):
    # model_np = numpy.array(model_data)
    model_np = numpy.array(model_data[-1000:])
    plt.plot(model_np[:, 0], model_np[:, 1], label='RT dataset 0')
    sensor_np = numpy.array(sensor_value)
    plt.plot(sensor_np[:, 0] + 10, sensor_np[:, 1], label='testset')
    for trigger_value in triggers_value:
        plt.axhline(y=trigger_value, color='r')
    plt.legend()
    plt.show()


def generate_rules(rules_number, trigger_point, trigger_value):
    actions = [200, 500, 1000, 2000, 5000, 500, 1000, 2000, 5000, 8000]  # TODO
    # actions = [10000, 20000, 50000, 100000, 200, 500, 1000, 2000, 5000, 8000]  # TODO
    rules = []
    stepconfs = []
    for i in range(rules_number):
        stepconf = StepConfPerEsti()
        ct = stepconf.prepare_data(f'stress_{actions[i]}')
        rules.append({"ct": ct, "ddl": stepconf.get_ddl_static(actions[i]), "target": trigger_value[i],
                      "trigger_points": trigger_point[i], "no": i, "stepconf_single": stepconf})
        stepconfs.append(stepconf)
    return rules, stepconfs


def get_triggered_events_now(rules, current_time, len, resource):
# def get_triggered_events_now(rules, current_time):
    oot_triggered_events = []
    it_triggered_events = []
    for rule in rules:
        if (current_time + len) in rule["trigger_points"]:
            if resource.get_valid_time(rule["no"]) < 0 or resource.get_valid_time(rule["no"]) > current_time + rules[rule["no"]]["ct"]:
                oot_triggered_events.append({"rule": rule["no"], "triggered time": current_time,
                                         "create time": rule["ct"], "exec time": -1, "resource": -1})
                rule["trigger_points"].remove((current_time + len))
            elif resource.get_valid_time(rule["no"]) >= current_time:
                it_triggered_events.append({"rule": rule["no"], "triggered time": current_time,
                                            "create time": (resource.get_valid_time(rule["no"]) - current_time),
                                            "exec time": rule["stepconf_single"].get_static_exe_time(resource.get_valid_resource(rule["no"])),
                                            "resource": resource.get_valid_resource(rule["no"])})
                rules[rule["no"]]["trigger_points"].remove((current_time + len))
            else:  # 启完容器之后直接销毁？
                # TODO:我现在是什么都没做，因为判断的频率已经是最高了，不可能miss event
                # 论理应该是以event去反着找有没有合适的时间
                oot_triggered_events.append({"rule": rule["no"], "triggered time": current_time,
                                            "create time": rules[rule["no"]]["ct"], "exec time": -1, "resource": -1})
                rules[rule["no"]]["trigger_points"].remove((current_time + len))
                resource.set_invalid(rule["no"])
    return oot_triggered_events, it_triggered_events


# TODO: exec_time会有偏移, 偏移和实际值是不一样的
def fill_oot_event_resource(oot_events, rules, current_time_offset, resource):
    each_resource = 1 / len(oot_events)
    exec_times = []
    for event in oot_events:
        event["resource"] = each_resource
        exec_time = rules[event["rule"]]["stepconf_single"].get_static_exe_time(each_resource)
        event["exec time"] = exec_time
        exec_times.append(exec_time)
    full_resource_time = resource.find_full_resource(current_time_offset, max(exec_times))
    for event in oot_events:
        if full_resource_time == -1:
            event["exec time"] += (len(resource.get_total_resource_list()) - current_time_offset)
            continue
        else:
            event["exec time"] += (full_resource_time - current_time_offset)
            offset = full_resource_time - current_time_offset
            if offset != 0:
                print(f'current:{current_time_offset}, offset:{offset}, slice:{resource.get_total_resource_list()[current_time_offset: full_resource_time]}')
                # print(f'resource:{resource.get_total_resource_list()}')
        # event["exec time"] += (full_resource_time - current_time_offset)
        resource.add_task_hard(event["rule"], full_resource_time, each_resource, event["create time"], event["exec time"])
        # resource.set_invalid(event["rule"])


def organize_event(oot_events, it_events, res_events):
    for event in oot_events:
        res_events[event["rule"]].append(event)
    for event in it_events:
        res_events[event["rule"]].append(event)


def finish_release_believe_freshest_scheduler(create_predictor, len_model_data, sensor_value, rules, stepconfs):
    current_time = sensor_value[0][0]
    res_events = [[] for _ in range(len(rules))]
    predict_cost = 0
    predict_cost_count = 0
    resource = Resource(len(sensor_value), stepconfs)
    while current_time <= sensor_value.copy().pop()[0]:
        # print(current_time)
        if current_time % 1000 == 0: print(f'current:{current_time}, total:{sensor_value.copy().pop()[0]}')
    # while current_time <= sensor_value[0][0] + 20:
        resource.flash(current_time - len_model_data)
        # 先判断当前有没有事件发生
        oot_triggered_events, it_triggered_events = get_triggered_events_now(rules, current_time - len_model_data, len_model_data, resource)
        # 如果有来不及的，当场分配资源
        if len(oot_triggered_events) != 0:
            # print(current_time, len_model_data, current_time - len_model_data, len(total_resource))
            # print(total_resource)
            fill_oot_event_resource(oot_triggered_events, rules, current_time - len_model_data, resource)
        organize_event(oot_triggered_events, it_triggered_events, res_events)
        # 以当前的数据预测接下来的情况
        for rule in rules:
            t1 = time.time()
            triggered_time = create_predictor.predict_triggered_time(sensor_value[: current_time - len_model_data + 1], 1,
                                                                     rule["target"], rule["ct"])
            t2 = time.time()
            predict_cost += (t2 - t1)
            predict_cost_count += 1
            if triggered_time != -1:
                # predict_events.append({"id": rule["no"], "ct": rule["ct"], "valid time": triggered_time})
                # if triggered_time not in predict_events:
                #     predict_events[triggered_time] = [{"id": rule["no"], "ct": rule["ct"]}]
                # else:
                #     predict_events[triggered_time].append({"id": rule["no"], "ct": rule["ct"]})
                resource.add_task(rule["no"], current_time - len_model_data, rule["ct"], triggered_time - len_model_data)

        current_time += 1
    print(resource.get_total_resource_list())
    print(res_events)
    return res_events


# # TODO: 没改呢
# def always_hot_even():
#     rules_number = 1
#     events_number = 2
#     sensor_value, trigger_point, triggers_value = import_data(rules_number, events_number)  # 每个每个数据取，
#     sc_models, rules = generate_rules(rules_number, trigger_point, triggers_value)
#
#     current_time = 0
#     res_events = [[] for _ in range(len(rules))]
#     while current_time <= sensor_value.copy().pop()[0]:
#         if current_time % 10000 == 0:
#             print(f'current:{current_time}, total:{len(sensor_value)}')
#         triggered_events = []
#         for i in range(len(rules)):
#             if current_time in rules[i]["trigger_points"]:
#                 triggered_events.append({"rule": i, "triggered time": current_time,"create time": 0,
#                                          "exec time": -1, "resource": 1 / len(rules)})
#         if len(triggered_events) != 0:
#             for i in range(len(triggered_events)):
#                 exec_time = sc_models[triggered_events[i]["rule"]].get_static_exe_time(triggered_events[i]["resource"])
#                 triggered_events[i]["exec time"] = exec_time
#             res_events[triggered_events[i]["rule"]].append(triggered_events[i])
#         current_time += 1
#     return res_events, rules


def run(create_predictor, resource, scheduler):
    rules_number = 5

    events_number = 2
    # sensor_value = [[0, 11], [1, 11], [2, 12], [3, 12], [4, 14], [5, 15], [6, 16], [7, 11], [8, 12], [9, 15], [10, 9],
    #                 [11, 12]]
    # rules_number = 3
    # triggers_value = [12, 15, 10]
    # trigger_point = [[0, 11], [2, 8, 11], [5, 9]]
    model_data, sensor_value, trigger_point, triggers_value = import_data(rules_number, events_number) # 每个每个数据取，
    create_predictor.train(model_data, 1000)
    # print(triggers_value)
    print(trigger_point)
    rules, stepconfs = generate_rules(rules_number, trigger_point, triggers_value)
    print('after generate')
    res_events = finish_release_believe_freshest_scheduler(create_predictor, len(model_data), sensor_value, rules, stepconfs)
    return res_events, rules



if __name__ == "__main__":
    evaluator = Evaluator()
    for predict in RTPred(2), RTPred(1), LinearPred(), OnDemandPred():
        print(predict.get_pred_name())
        events, rules = run(predict, None, None)
        evaluator.emulation_evaluate(events, rules)

    # events, rules = always_hot_even()
    # emulation_evaluate(events, rules)
    # import_data(2, 1)

    # predict = RTPred()
    # events, rules = run(predict, None, None)
    # print(f'events:{events}')
    # emulation_evaluate(events, rules)
