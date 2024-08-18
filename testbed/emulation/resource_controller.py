


class Resource:
    # total_resource = None
    # task_list = None
    # stepconfs = None
    # newest_container_valid_time = None
    # newest_container_resource = None


    def __init__(self, length, stepconfs):
        self.task_list = [[] for _ in range(length + 100)]
        self.total_resource = [1] * (length + 100)
        self.stepconfs = stepconfs
        self.newest_container_valid_time = [-1] * len(stepconfs)
        self.newest_container_resource = [0] * len(stepconfs)
    # def register_task(self, rule_no, ct, valid_time, exec_time):
    #     self.task_list.append({"no": rule_no, "ct": ct, "valid": valid_time, "exec": exec_time})


    def add_task(self, rule_no, current, ct, valid_time_offset):
        start = int(valid_time_offset - ct)
        for i in range(current, start):
            task_time = self.task_list[i]
            for task in task_time:
                if task["no"] == rule_no:
                    self.task_list[i].remove(task)
        find_start = start
        while find_start < len(self.total_resource):
            if self.total_resource[find_start] == 1:
                break
            find_start += 1
        # end = int(find_start + ct + exec_time)
        self.task_list[find_start].append({"no": rule_no, "valid": valid_time_offset})
        self.newest_container_valid_time[rule_no] = valid_time_offset


    def find_full_resource(self, current, length):
        find_time = current
        while find_time < len(self.total_resource):
            lst = self.total_resource[find_time: int(find_time + length + 1)]
            if all(elem == 1 for elem in lst) and len(lst) == int(length + 1):
                return find_time
            else:
                find_time += 1
        # print(current, length, self.total_resource)
        return -1


    def add_task_hard(self, rule_id, find_time, resource, ct, exec_time):
        # print("add hard task", rule_id, resource, find_time, ct, exec_time)
        # print(self.total_resource)
        for f_time in range(find_time, int(find_time + ct + exec_time) + 1):
            self.total_resource[f_time] -= resource
        # print(self.total_resource)
        self.newest_container_valid_time[rule_id] = int(find_time + ct)
        self.newest_container_resource[rule_id] = resource
        # return each_resource

    # def has_valid_container(self, current, rule_no):

    def get_valid_time(self, rule_no):
        return self.newest_container_valid_time[rule_no]

    def set_invalid(self, rule_no):
        self.newest_container_valid_time[rule_no] = -1

    def get_valid_resource(self, rule_no):
        return self.newest_container_resource[rule_no]

    # def get_max_task_time(self, current):
    #     max_task_cost = 0
    #     for task in self.task_list[current]:
    #         cost = task[""]
    #         if max_task_cost <= task[]

    def flash(self, current):
        # if current <= 20:
        #     print(f'current:{current}, task list:{self.task_list}')
        #     print(f'resource:{self.total_resource}')
        if len(self.task_list[current]) != 0:
            each_resource = 1 / len(self.task_list[current])
            exec_times = []
            for task in self.task_list[current]:
                task["resource"] = each_resource
                self.newest_container_resource[task["no"]] = each_resource
                exec_time = self.stepconfs[task["no"]].get_static_exe_time(each_resource)
                exec_times.append(exec_time)
            find_time = self.find_full_resource(current, max(exec_times))

            each_resource = 1 / len(self.task_list[current])
            if find_time == -1:
                print(f'predict error of find no time: current:{current}')
                return
            for exec_time in exec_times:
                for time in range(find_time, min(int(find_time + exec_time), len(self.total_resource)) + 1):
                    # print(f'current:{time}, resource:{self.total_resource[time]}, minus:{each_resource}')
                    self.total_resource[time] -= each_resource

    def get_total_resource_list(self):
        return self.total_resource

if __name__ == "__main__":
    r = Resource(6, [1])
    r.total_resource = [1, 1, 1, 1, 1, 0]
    print(r.find_full_resource(0, 2.5))
