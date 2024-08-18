import sys


class FileWriter:
    def __init__(self, path, patten):
        self.path = path
        self.pattern = patten

    def write(self, string, end="*"):
        stdout_backup = sys.stdout
        log_file = open(self.path, self.pattern)
        sys.stdout = log_file
        if end == "*":
            print(string)
        else:
            print(string, end=end)
        log_file.close()
        sys.stdout = stdout_backup
