from taosrest import connect


def reset(trigger_name):
    conn = connect(url="http://10.214.131.191:6041",
                   user="root",
                   password="taosdata",
                   database="container_log",
                   timeout=100)
    cursor = conn.cursor()
    res = cursor.execute(f"DELETE FROM polled_rt_{trigger_name} WHERE time < NOW")
    print(f"reset polled data:{trigger_name}, {res}")


if __name__ == "__main__":
    reset('out_pres')
