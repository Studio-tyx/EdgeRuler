import time

from taosrest import connect


class TDEngineTool:
    cursor = None

    def __init__(self):
        conn = connect(url="http://10.214.131.191:6041",
                       user="root",
                       password="taosdata",
                       database="container_log",
                       timeout=100)
        self.cursor = conn.cursor()

    def select_last_data(self, table_name, trigger_name):
        self.cursor.execute(f"SELECT LAST({trigger_name}) FROM {table_name}")
        data = self.cursor.fetchone()
        for item in data:
            data = item
        return data

    def insert_data_now(self, table_name, data):
        self.cursor.execute(f"INSERT INTO {table_name} VALUES (NOW, {data}) ")
        print(f"[TDEngine Tool] inserted trigger table:'{table_name}', data:{data}, timestamp:{time.time()}")

    def insert_data_init_rt(self, table_name, data):
        conn = connect(url="http://10.214.131.191:6041",
                       user="root",
                       password="taosdata",
                       database="container_log",
                       timeout=100)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {table_name} VALUES ('{data[0]}', {data[1]},{data[2]},"
                       f"{data[3]},{data[4]},{data[5]},{data[6]},{data[7]},{data[8]},{data[9]},"
                       f"{data[10]}) ")
        print(f"inserted time:{data[0]}")

    def select_last_data_by_time(self, timestamp, table_name, trigger_name):
        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(timestamp))
        self.cursor.execute(
            f"SELECT {trigger_name} FROM {table_name} WHERE time <= '{date_time}' ORDER BY time DESC LIMIT 1")
        data = self.cursor.fetchone()
        return data[0]

    def select_all_data(self, table_name, trigger_name):
        res_data = {}
        self.cursor.execute(f"SELECT time,{trigger_name} FROM {table_name}")
        data = self.cursor.fetchall()
        for item in data:
            timestamp = item[0].timestamp()
            res_data[timestamp] = item[1]
            # print(timestamp, item[1])
        return res_data

    def select_data_of_range(self, table_name, trigger_name, where_str):
        res_data = {}
        # print(f"SELECT time,{trigger_name} FROM {table_name} WHERE {where_str}")
        self.cursor.execute(f"SELECT time,{trigger_name} FROM {table_name} WHERE {where_str}")
        data = self.cursor.fetchall()
        for item in data:
            timestamp = item[0].timestamp()
            res_data[timestamp] = item[1]
            # print(timestamp, item[1])
        return res_data

    def select_sensor_data_by_time_former(self, table_name, trigger_name, timestamp):
        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(timestamp))
        self.cursor.execute(
            f"SELECT {trigger_name} FROM {table_name} WHERE time <= '{date_time}' ORDER BY time DESC LIMIT 1 ")
        data = self.cursor.fetchone()
        return data[0]

    def select_no_by_time(self, table_name, timestamp):
        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(timestamp))
        # print((f"SELECT time,data FROM {table_name} WHERE name = '{trigger_name}' AND {where_str}"))
        self.cursor.execute(
            f"SELECT count(*) FROM (SELECT * FROM {table_name} WHERE time <= '{date_time}' ORDER BY time desc LIMIT 1 ) ")
        data = self.cursor.fetchone()
        return data[0]

    def select_by_str(self, sql_str):
        self.cursor.execute(sql_str)
        return self.cursor.fetchall()


if __name__ == '__main__':
    td = TDEngineTool
    # print(td.select_last_data())
