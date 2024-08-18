import csv
import time

import numpy as np
from taosrest import connect


class RawDataGenerator:
    length = 0
    data = {}

    def __init__(self, length):
        self.length = length

    def generate_incremental_to_td(self):
        current_data = 149.0
        for i in range(self.length):
            # current_data = random.random() * self.length + current_data
            self.data[int(time.time())] = current_data
            time.sleep(0.5)
            # print(current_data+i/5)
            self.poll_data_to_tdengine(current_data + i / 5)

    def generate_incremental_simu_time(self):
        current_data = 0
        current_time = int(time.time())
        for i in np.arange(0, self.length, 0.5):
            current_data = current_data + 1
            # current_data = int(random.random() * self.length + current_data)
            self.data[current_time + i] = current_data
            # self.poll_data_to_tdengine(current_data)
            # time.sleep(1)

    def poll_data_to_tdengine(self, data):
        conn = connect(url="http://10.214.131.191:6041",
                       user="root",
                       password="taosdata",
                       database="container_log",
                       timeout=30)
        cursor = conn.cursor()
        # insert data
        cursor.execute(f"INSERT INTO triggers VALUES (NOW, 'temp',{data}) ")
        print("inserted row count:", data)

    def save_to_csv(self, string):
        f = open(string, 'w', encoding='utf-8', newline='')
        csv_writer = csv.writer(f)
        for key, value in self.data.items():
            csv_writer.writerow([key, value])
        f.close()


TIME_LENGTH = 100
if __name__ == '__main__':
    rdg = RawDataGenerator(TIME_LENGTH)
    # rdg.generate_incremental_simu_time()
    rdg.generate_incremental_to_td()
    # rdg.save_to_csv("../../data/raw_data.csv")
