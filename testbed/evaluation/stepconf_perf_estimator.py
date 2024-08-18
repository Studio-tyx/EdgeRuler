import cvxpy as cp
import docker
import numpy as np
import pandas as pd
from scipy import optimize
import matplotlib.pyplot as plt

from edgeruler_code.utils import FileWriter

CYCLE = 10

CONFIGURATIONS = [0.05, 0.1, 0.15, 0.2, 0.4, 0.6, 0.8, 1]   # relative memory configuration, system max memory: 1769*2MB
# 1769MB => 1 vCPU
# https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html


# cost = sum(predict_t - real_t) ** 2
def cost(x, data):
    sum = 0
    for i in range(len(data)):
        sum += ((data[i][1] - x[2]) * (5.29 * data[i][0] + x[1]) - x[0]) ** 2   # 5.29 => 1 / best performance (max memory)
    return sum


# time model according to StepConf
def cal_t(x, m):
    return x[0] / (5.29 * m + x[1]) + x[2]


class StepConfPerEsti:
    def test_container(self, image_name, ops):
        cpus = []
        memories = []

        # generate training set: 0.02, 0.04, ..., 0.1, 0.2, 0.4, ..., 1
        for i in np.arange(0.02, 0.1, 0.02):
            cpus.append(int(i * 1000000 * 2))   # max cpu_quota: 1 * 2 vCPU
            memories.append(f'{i * 1769 * 2}m')   # max memory: 1769 * 2MB
        for i in np.arange(0.2, 1, 0.2):
            cpus.append(int(i * 1000000 * 2))
            memories.append(f'{i * 1769 * 2}m')

        client = docker.from_env()
        total_times = []
        for cpu, memory in zip(cpus, memories):
            total_time = 0
            print(f'measuring:{cpu / 1000000 / 2}')
            for j in range(CYCLE):
                # pre-warm stress container
                container = client.containers.run('leon/stress-ng-alpine:latest', cpu_quota=cpu, stdin_open=True,
                                                  mem_limit=memory, detach=True, command='sh', name='stress')
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
            total_times.append(total_time / CYCLE)  # calculate average execution time

        # you can change file name to separate test case to calculate accuracy
        file = FileWriter(f'../../data/image_config/model_data/{image_name}_{ops}_test_data.csv', 'a')  # write test log
        for cpu, time in zip(cpus, total_times):
            # print(f'm_i:{cpus[i]/1000000/2}, time:{total_times[i]}')
            print(f'{cpu / 1000000 / 2}, {time}')
            file.write(f'{cpu / 1000000 / 2}, {time}')

    '''
    use scipy.optimize.minimize for solution
    min sum(t * x)
    s.t. sum(m * x) <= M
        for any i sum(x) = 1
    (if you're still confused, please ask me for note)
    '''
    def min_resource(self, image_list):
        n = (len(image_list), 8)    # kind of container images
        x = cp.Variable(n, boolean=True)    # x[i, j] of 0-1 variables to decide i_th container whether choose j_th memory configuration
        t_list = self.read_param(image_list)
        t = np.array(t_list)    # t[i, j] execution time of i_th container calculated by StepConf, using j_th configuration in CONFIGURATIONS
        m = np.array(CONFIGURATIONS).reshape([8, 1])    # configurations, to satisfy the constraint of total memory size
        M = self.get_curr_memory()  # now is a constant of 1

        prob = cp.Problem(cp.Minimize(cp.sum(cp.sum(cp.multiply(t, x), axis=1), axis=0)),
                          [cp.sum(x @ m) <= M,
                           cp.sum(x, axis=1) == 1])

        ans = prob.solve(solver=cp.GLPK_MI)     # to get the optimized solution of memory allocation
        print("min time: ", ans)
        for i in range(len(image_list)):
            for j in range(len(CONFIGURATIONS)):
                if x.value[i, j] == 1:
                    print(f'{image_list[i]}, memory resource:{CONFIGURATIONS[j]}, cost time:{t[i][j]}')


    # read the param of alpha, beta, phi, for calculating exec time
    def read_param(self, image_list):
        res = []
        for image in image_list:
            csv_data = pd.read_csv(f'../../data/image_config/model_para/{image}_para.csv', header=None)
            model_param = list(np.array(csv_data)[0])
            pred_t_list = []
            for m in CONFIGURATIONS:
                t = cal_t(model_param, m)
                pred_t_list.append(t)
            res.append(pred_t_list)
        return res

    # now is a fixed value of full memory
    def get_curr_memory(self):
        return 1.0

    # calculate the model param (alpha, beta, phi) using test data of containers
    # calculate the error and accuracy
    def get_model_para(self, image_name):
        csv_data = pd.read_csv(f'../../data/image_config/model_data/{image_name}_data.csv')
        test_data = np.array(csv_data)
        print(test_data)
        cons = []

        # (t - phi) * (5.29 * m + beta) - alpha = 0
        # constraints: t > 0
        for i in range(len(test_data)):
            cons.append({'type': 'ineq', 'fun': lambda x: x[0] / (5.29 * test_data[i][0] + x[1]) + x[2]})

        # constraints: 0 < m < 1
        for i in range(len(test_data)):
            cons.append({'type': 'ineq', 'fun': lambda x: 1 - (x[0] / (test_data[i][1] - x[2]) - x[1]) / 5.29})
        result = optimize.minimize(cost, x0=[1, 1, 1], constraints=cons, args=test_data)
        error = 0

        # test set of data, differ from train set of data
        csv_data = pd.read_csv(f'../../data/image_config/model_data/{image_name}_test_data.csv')
        data = np.array(csv_data)
        print(data)

        # calculate error
        for i in range(len(data)):
            predict = result.x[0] / (5.29 * data[i][0] + result.x[1]) + result.x[2]
            error += abs(predict - data[i][1])
            print(f'{data[i][0]}, real:{data[i][1]}, predict: {predict}, abs: {abs(predict - data[i][1])}')
        print(f'error:{error / len((data))}')

        # save model param
        file = FileWriter(f'../../data/image_config/model_para/{image_name}_para.csv', 'w')
        file.write(f'{result.x[0]}, {result.x[1]}, {result.x[2]}')
        self.draw_pic(data, result.x)

    def draw_pic(self, real, param):
        x = np.linspace(0.03,1,1000)
        y = param[0] / (5.29 * x + param[1]) + param[2]
        plt.plot(x,y,linestyle='-',linewidth=2, label='predict')
        x_list = []
        y_list = []
        for i in range(len(real)):
            x_list.append(real[i][0])
            y_list.append(real[i][1])
        x = np.array(x_list)
        y = np.array(y_list)
        plt.scatter(x, y, color='red', marker='+', label='real')

        plt.legend()
        plt.title("StepConf Performance Estimator")
        plt.ylabel("time(s)")
        plt.xlabel("relative resource")
        plt.show()



if __name__ == "__main__":
    scpe = StepConfPerEsti()
    # scpe.test_container('stress', 500)
    # scpe.test_container('stress', 1000)
    scpe.test_container('stress', 100)
    # scpe.test_container('stress', 2000)
    # scpe.test_container('stress', 200)
    # scpe.get_model_para('stress_500')
    # scpe.get_model_para('stress_1000')
    # scpe.get_model_para('stress_100')
    # scpe.get_model_para('stress_2000')
    # scpe.get_model_para('stress_200')
    # scpe.min_resource(['stress_500', 'stress_1000', 'stress_100', 'stress_2000', 'stress_200'])
    # scpe.get_model_para('stress_1000')