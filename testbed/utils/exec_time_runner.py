import docker
import time as Time
import numpy as np

from edgeruler_code.utils.file_writer_bak import FileWriter

CYCLE = 10


class ExecTimeRunner:
    def test_container(self, image_name, ops):
        cpus = []
        memories = []

        # generate training set: 0.02, 0.04, ..., 0.1, 0.2, 0.4, ..., 1
        # for i in np.arange(0.02, 0.1, 0.02):
        #     cpus.append(int(i * 1000000 * 2))  # max cpu_quota: 1 * 2 vCPU
        #     memories.append(f'{i * 1769 * 2}m')  # max memory: 1769 * 2MB
        for i in np.linspace(0.1, 1, 10):
            cpus.append(int(i * 100000 * 2))
            memories.append(f'{i * 1769 * 2}m')

        total_ct = 0
        client = docker.from_env()
        total_times = []
        delta = 0
        for cpu, memory in zip(cpus, memories):
            total_time = 0
            print(f'measuring:{cpu / 100000 / 2}')
            for j in range(CYCLE):
                t1 = Time.time()
                # pre-warm stress container
                container = client.containers.run('leon/stress-ng-alpine:latest', cpu_quota=cpu, stdin_open=True,
                                                  mem_limit=memory, detach=True, command='sh', name='stress')
                t2 = Time.time()
                # run stress container
                exec_output = container.exec_run(f'stress-ng --cpu 10 --cpu-ops {ops}')
                container.remove(force=True)

                # get exec time from debug log
                output_str = exec_output[1].decode('utf-8')
                index = output_str.find("completed in")
                if index == -1:
                    continue
                exec_time = float(output_str[index + 13:index + 17])
                total_time += exec_time
                total_ct += (t2 - t1)
            delta = 1 / (total_time / CYCLE)
            total_times.append(total_time / CYCLE)  # calculate average execution time

        # you can change file name to separate test case to calculate accuracy
        file = FileWriter(f'../../data/image_config/model_data/{image_name}_{ops}_data.csv', 'a')  # write test log
        for cpu, time in zip(cpus, total_times):
            # print(f'm_i:{cpus[i]/1000000/2}, time:{total_times[i]}')
            print(f'{cpu / 100000 / 2}, {time}')
            file.write(f'{cpu / 100000 / 2}, {time}')

        file = FileWriter(f'../../data/image_config/model_ct_delta/{image_name}_{ops}_data.csv', 'w')  # write test log
        file.write(f'{total_ct / (CYCLE * len(cpus))}, {delta}')
        print(f'create time:{total_ct / (CYCLE * len(cpus))}, delta:{delta}')



if __name__ == "__main__":
    etr = ExecTimeRunner()
    # 10000, 20000, 50000, 100000, 200, 500, 1000, 2000, 5000, 8000
    # etr.test_container('stress', 10000)
    # etr.test_container('stress', 20000)
    # etr.test_container('stress', 50000)
    # etr.test_container('stress', 100000)
    # etr.test_container('stress', 200)
    # etr.test_container('stress', 500)
    # etr.test_container('stress', 1000)
    # etr.test_container('stress', 2000)
    etr.test_container('stress', 5000)
    # etr.test_container('stress', 8000)