import sys


class FileWriter:
    def __init__(self, path, patten):
        self.path = path
        self.pattern = patten

    def write(self, string):
        stdout_backup = sys.stdout
        log_file = open(self.path, self.pattern)
        sys.stdout = log_file
        print(string)
        log_file.close()
        sys.stdout = stdout_backup
