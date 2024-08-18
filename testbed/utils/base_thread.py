import threading


class BaseThread(threading.Thread):
    def __init__(self, target, args=()):
        super(BaseThread, self).__init__()
        self.result = None
        self.func = target
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        threading.Thread.join(self)  # 等待线程执行完毕
        try:
            return self.result
        except Exception:
            print(Exception)
