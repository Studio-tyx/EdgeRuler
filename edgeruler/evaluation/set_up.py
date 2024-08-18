import argparse
import math
import pandas as pd

DELTA = 10
SINGLE_RULES = [[0, 4.0, 1000, DELTA, 1], [1, 50000, 1000, DELTA, 1], 
         [2, 30.0, 2000, DELTA, 2], [3, 29, 2000, DELTA, 2], [4, 1012.90, 2000, DELTA, 2], 
         [3, 32, 3000, DELTA, 3], [2, 31, 3000, DELTA, 3], [5, 0.04, 3000, DELTA, 3], [6, 1150, 3000, DELTA, 3], 
         [8, 1011.8, 1000, DELTA, 1], [8, 1011.8, 1000, DELTA, 1], [8, 1011.8, 1000, DELTA, 1], 
        #  [8, 1011.8, 1000, DELTA, 1], 
         ]

MULTI_RULES = [[7, 30.2, 1000, DELTA, 1], [8, 1012.2, 1000, DELTA, 1], [0, 4.0, 1000, DELTA, 1], [1, 50000, 1000, DELTA, 1], 
         [2, 30.0, 2000, DELTA, 2], [3, 23.8, 2000, DELTA, 2], [3, 29, 2000, DELTA, 2], 
        #  [4, 1012.90, 2000, DELTA, 2], 
         [3, 32, 3000, DELTA, 3], [2, 31, 3000, DELTA, 3], [5, 0.04, 3000, DELTA, 3], 
        #  [6, 1150, 3000, DELTA, 3], 
         [7, 31.8, 4000, DELTA, 4], [8, 1011.8, 4000, DELTA, 4],
         ]

MULTI_RULES = [[7, 30.2, 1000, DELTA, 1], [8, 1012.2, 1000, DELTA, 1], [0, 4.0, 1000, DELTA, 1], [1, 50000, 1000, DELTA, 1], 
         [2, 30.0, 2000, DELTA, 2], [3, 23.8, 2000, DELTA, 2], [3, 29, 2000, DELTA, 2], 
        #  [4, 1012.90, 2000, DELTA, 2], 
         [3, 32, 3000, DELTA, 3], [2, 31, 3000, DELTA, 3], [5, 0.04, 3000, DELTA, 3], 
        #  [6, 1150, 3000, DELTA, 3], 
         [8, 1011.8, 1000, DELTA, 1], [8, 1011.8, 1000, DELTA, 1],
         ]


RULE_FILE_NAME = ['IndoorHumidity_pct-30.2.txt', 'IndoorPressure_hPa-1012.2.txt', 'OutdoorUV-4.txt',
'OutdoorVisibleRay_Lux-50000.txt', 'OutdoorTemperature_C-30.txt', 'OutdoorHumidity_pct-23.8.txt',
'OutdoorHumidity_pct-29.txt', 
'OutdoorHumidity_pct-32.txt', 'OutdoorTemperature_C-31.txt', 'IndoorUV-0.04.txt', 
'IndoorPressure_hPa-1011.8.txt', 'IndoorPressure_hPa-1011.8.txt']


LENGTH = 1000
HORIZON_LENGTH = 10
SINGLE = False
if SINGLE is True:
    HORIZON_INTERVAL = 5
    MAX_EVENT_PER_HORIZON = 3
    RULES = MULTI_RULES
else:
    HORIZON_INTERVAL = 0
    MAX_EVENT_PER_HORIZON = 3
    RULES = MULTI_RULES
SENSOR_NAME = ['OutdoorUV', 'OutdoorVisibleRay_Lux', 'OutdoorTemperature_C', 'OutdoorHumidity_pct',
               'OutdoorPressure_hPa', 'IndoorUV', 'IndoorVisibleRay_Lux',
               'IndoorHumidity_pct', 'IndoorPressure_hPa']

MAX_RESOURCE = 16.0
DDL_BASE = 4.0
R_CHOICE = [4.0, 6.0, 8.0, 12.0, 16.0]
MAX_CHOICE = {1000: 9.0, 2000: 10.0, 3000: 10.0, 4000: 15.0, 5000: 13.0, 6000: 12.0, 7000: 16.0, 8000: 14.0, 9000: 14.0, 10000: 16.0}

P = {1000:{1.0: 1.48, 2.0: 0.692, 3.0: 0.511, 4.0: 0.372, 5.0: 0.301, 6.0: 0.259, 7.0: 0.225, 8.0: 0.203, 9.0: 0.1989, 10.0: 0.195, 11.0: 0.1911, 12.0: 0.1872, 13.0: 0.1835, 14.0: 0.1798, 15.0: 0.1762, 16.0: 0.1727},
    2000:{1.0: 3.018, 2.0: 1.361, 3.0: 0.985, 4.0: 0.739, 5.0: 0.684, 6.0: 0.525, 7.0: 0.483, 8.0: 0.416, 9.0: 0.4077, 10.0: 0.3995, 11.0: 0.3915, 12.0: 0.3837, 13.0: 0.376, 14.0: 0.3685, 15.0: 0.3611, 16.0: 0.3539},
    3000:{1.0: 4.514, 2.0: 2.025, 3.0: 1.512, 4.0: 1.097, 5.0: 1.056, 6.0: 0.767, 7.0: 0.741, 8.0: 0.613, 9.0: 0.6007, 10.0: 0.5887, 11.0: 0.577, 12.0: 0.5654, 13.0: 0.5541, 14.0: 0.543, 15.0: 0.5322, 16.0: 0.5215},
    4000:{1.0: 6.059, 2.0: 2.685, 3.0: 1.951, 4.0: 1.442, 5.0: 1.383, 6.0: 1.018, 7.0: 0.971, 8.0: 0.803, 9.0: 0.7869, 10.0: 0.7712, 11.0: 0.7558, 12.0: 0.7407, 13.0: 0.7258, 14.0: 0.7113, 15.0: 0.6971, 16.0: 0.6832},
    5000:{1.0: 7.568, 2.0: 3.355, 3.0: 2.414, 4.0: 1.802, 5.0: 1.676, 6.0: 1.262, 7.0: 1.223, 8.0: 0.992, 9.0: 0.9722, 10.0: 0.9527, 11.0: 0.9337, 12.0: 0.915, 13.0: 0.8967, 14.0: 0.8788, 15.0: 0.8612, 16.0: 0.844},
    6000:{1.0: 8.94, 2.0: 4.067, 3.0: 2.981, 4.0: 2.183, 5.0: 2.089, 6.0: 1.523, 7.0: 1.478, 8.0: 1.189, 9.0: 1.1652, 10.0: 1.1419, 11.0: 1.1191, 12.0: 1.0967, 13.0: 1.0748, 14.0: 1.0533, 15.0: 1.0322, 16.0: 1.0116},
    7000:{1.0: 10.19, 2.0: 4.743, 3.0: 3.451, 4.0: 2.532, 5.0: 2.464, 6.0: 1.774, 7.0: 1.697, 8.0: 1.385, 9.0: 1.3573, 10.0: 1.3302, 11.0: 1.3036, 12.0: 1.2775, 13.0: 1.2519, 14.0: 1.2269, 15.0: 1.2024, 16.0: 1.1783},
    8000:{1.0: 11.64, 2.0: 5.398, 3.0: 3.972, 4.0: 2.875, 5.0: 2.797, 6.0: 2.021, 7.0: 1.926, 8.0: 1.577, 9.0: 1.5455, 10.0: 1.5146, 11.0: 1.4843, 12.0: 1.4546, 13.0: 1.4255, 14.0: 1.397, 15.0: 1.369, 16.0: 1.3417},
    9000:{1.0: 13.21, 2.0: 6.077, 3.0: 4.408, 4.0: 3.245, 5.0: 3.075, 6.0: 2.265, 7.0: 2.19, 8.0: 1.773, 9.0: 1.7375, 10.0: 1.7028, 11.0: 1.6687, 12.0: 1.6354, 13.0: 1.6027, 14.0: 1.5706, 15.0: 1.5392, 16.0: 1.5084},
    10000:{1.0: 14.41, 2.0: 6.742, 3.0: 5.039, 4.0: 3.598, 5.0: 3.477, 6.0: 2.535, 7.0: 2.433, 8.0: 1.974, 9.0: 1.9345, 10.0: 1.8958, 11.0: 1.8579, 12.0: 1.8208, 13.0: 1.7843, 14.0: 1.7487, 15.0: 1.7137, 16.0: 1.6794}}


def f(op, r):
    if r < 1 or r > 16:
        print("unvalid r")
    return math.ceil(P[op][int(r)] * 10)


def sensor_data_filter(trigger_name, length):
    df = pd.read_csv('../../dataset/sensor_data/er_raw_data.csv', header=0, nrows=length)
    df = df.rename(columns={df.columns[0]: 'time'})
    lst = [[int(row[0]), row[1]] for row in df[['time', trigger_name]].values]
    return lst


def get_triggered_time(data, target):
    times = []
    former = True
    for line in data:
        if former is False and line[1] >= target:
            times.append(line[0])
        if line[1] >= target:
            former = True
        else:
            former = False
    return times


def get_event_optimal():
    event = []
    dataset = []
    for rule in RULES:
        triggered_time = get_triggered_time(sensor_data_filter(SENSOR_NAME[rule[0]], LENGTH), rule[1])
        # print(SENSOR_NAME[rule[0]], len(triggered_time))
        dataset.append([RULES.index(rule), triggered_time])
    for i in range(LENGTH):
        for d in range(len(dataset)):
            if i in dataset[d][1]:
                event.append([i, dataset[d][0]])
    return event


def get_event_dbp():
    sensor_events = []
    for file_name in RULE_FILE_NAME:
        data = []
        events = []
        with open(f'../../dataset/dbp/{file_name}', 'r') as file:
            lines = file.readlines()
            for line in lines:
                data.append(int(eval(line)))
        for i in range(len(data) - 1):
            if data[i + 1] == 1 and data[i] == 0:
                events.append(i + 1)
        sensor_events.append([RULE_FILE_NAME.index(file_name), events])
        # print(file_name, len(events))
    res = []
    length = 1000
    for i in range(length):
        for d in range(len(sensor_events)):
            if i in sensor_events[d][1]:
                res.append([i, sensor_events[d][0]])
    # print(res)
    return res


def get_truth():
    event = get_event_optimal()
    current = 0
    i = 0
    real_events = []
    real_event = []
    while current < event[len(event) - 1][0]:
        if i < len(event) and current <= event[i][0] < current + HORIZON_LENGTH:
            real_event.append(event[i])
            i += 1
        else:
            current += HORIZON_LENGTH
            if len(real_event) > MAX_EVENT_PER_HORIZON: real_event = real_event[:2]
            if len(real_events) == 0:
                real_events.append(real_event)
            else:
                if len(real_events[-1]) ==0 or abs(real_events[-1][-1][0] - current) > HORIZON_INTERVAL:
                    real_events.append(real_event)

            real_event = []
    # [[time, rule_id], ..]
    return real_events


def get_dbp_predict():
    event = get_event_dbp()
    current = 0
    i = 0
    real_events = []
    real_event = []
    while current < event[len(event) - 1][0]:
        if i < len(event) and current <= event[i][0] < current + HORIZON_LENGTH:
            real_event.append(event[i])
            i += 1
        else:
            current += HORIZON_LENGTH
            if len(real_event) > MAX_EVENT_PER_HORIZON: real_event = real_event[:2]
            if len(real_events) == 0:
                real_events.append(real_event)
            else:
                if len(real_events[-1]) ==0 or abs(real_events[-1][-1][0] - current) > HORIZON_INTERVAL:
                    real_events.append(real_event)

            real_event = []
    # [[time, rule_id], ..]
    return real_events


# def collect_total_data(event, args):
#     current = 0
#     i = 0
#     real_events = []
#     real_event = []
#     while current < event[len(event) - 1][0]:
#         if i < len(event) and current <= event[i][0] < current + HORIZON_LENGTH:
#             real_event.append(event[i])
#             i += 1
#         else:
#             current += HORIZON_LENGTH
#             if len(real_event) > args: real_event = real_event[:2]
#             if len(real_events) == 0:
#                 real_events.append(real_event)
#             else:
#                 if len(real_events[-1]) ==0 or abs(real_events[-1][-1][0] - current) > HORIZON_INTERVAL:
#                     real_events.append(real_event)

#             real_event = []
#     # [[time, rule_id], ..]
#     return real_events


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--event', type=bool)
    args = parser.parse_args()
    if args.event == True:
        events = collect_total_data()
        for horizon in events:
            print(horizon)
    else:
        print("undefined!")