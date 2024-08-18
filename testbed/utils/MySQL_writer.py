import pymysql


class MySQLWriter:
    port = 3306
    charset = "utf8"

    def __init__(self, host, database, user, passwd):
        self.host = host
        self.database = database
        self.user = user
        self.passwd = passwd
        self.conn = pymysql.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            charset=self.charset,
            user=self.user,
            passwd=self.passwd
        )

    def write(self, sql_str):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql_str)
                self.conn.commit()
                print("run MySQL successfully: " + sql_str)

        except Exception as e:
            print("数据库操作异常：\n", e)
        finally:
            # self.conn.close()
            return cursor.rowcount

    def close(self):
        self.conn.close()
