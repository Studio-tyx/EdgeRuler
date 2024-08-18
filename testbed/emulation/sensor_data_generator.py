import numpy as np

from edgeruler_code.utils import TDEngineTool


def generate_data_from_interval(range, interval):
    tdengine = TDEngineTool()
    trigger_name = 'out_temp'
    table_name = 'triggers_rt'
    data_count = {}
    raw_data = tdengine.select_by_str(f'SELECT {trigger_name} FROM {table_name} LIMIT {range}')
    for i in range(len(raw_data)):
        if raw_data[i][1] in data_count:
            data_count[raw_data[i][1]].append(raw_data[i][0])
        else:
            data_count[raw_data[i][1]] = [raw_data[i][0]]
    trigger_interval = []
    for i in data_count.keys():
        lst = data_count[i]
        gaps = [lst[i + 1] - lst[i] for i in range(len(lst) - 1)]
        average_gap = sum(gaps) / len(gaps)
        trigger_interval.append([i, average_gap])
    arr = np.array(trigger_interval)
    idx = (np.abs(arr[:, 1] - interval)).argmin()
    return trigger_interval[idx][0], raw_data


if __name__ == "__main__":
    generate_data_from_interval(100000, 30)