import time

import pandas as pd

from edgeruler_code.utils import TDEngineTool

TRIGGERS_NAME = ['out_uv', 'out_ray', 'out_temp', 'out_humid', 'out_pres', 'in_uv', 'in_ray', 'in_temp', 'in_humid',
                 'in_pres']
START_TIMESTAMP_RT = pd.Timestamp('2017-04-22 00:00:00.000', freq='H').timestamp()
TIME_LENGTH = 100


class SensorPollingManager:
    trigger_name = ""
    dp = None
    now_data = 0
    start_time = 0

    def __init__(self, trigger_name):
        self.trigger_name = trigger_name
        self.tdengine = TDEngineTool()
        self.start_time = time.time()

    def run(self, interval):
        count = 0
        while count < TIME_LENGTH:
            self.now_data = self.read_data_from_tdengine()
            self.write_to_tdengine(self.trigger_name)
            time.sleep(interval)
            count += 1

    def read_data_from_tdengine(self):
        timestamp = time.time()
        timestamp_2017 = timestamp - self.start_time + START_TIMESTAMP_RT
        return self.tdengine.select_last_data_by_time(timestamp_2017, "triggers_rt", self.trigger_name)

    def write_to_tdengine(self, trigger_name):
        self.tdengine.insert_data_now(f'polled_rt_{self.trigger_name}', self.now_data)


if __name__ == "__main__":
    spm = SensorPollingManager('out_pres')
    spm.run(5)
