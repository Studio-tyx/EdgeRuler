import time

import numpy as np

from set_up import f

def cartesian_power(lst, n):
    if n == 0:
        return [()]
    else:
        result = []
        for x in lst:
            for y in cartesian_power(lst, n - 1):
                result.append((x,) + y)
        return result


def check(rs, start, real_ddls, cts, n, s_min, p_op, max_start, resource, preds):
    # resource = [max_r] * (max_start * 2)
    s_sum = 0
    for i in range(n):
        if int(start[i] + cts[i] + f(p_op[i], rs[i])) > real_ddls[i]: return -1
        if start[i] + cts[i] < preds[i]: return -1
        j = start[i]
        while j < int(start[i] + cts[i] + f(p_op[i], rs[i])):
            # if j > real_ddls[i]: return -1
            # print(j, len(resource), i, len(rs))
            if resource[j] < rs[i]: return -1
            resource[j] -= rs[i]
            j += 1
        s_sum += (cts[i] + f(p_op[i], rs[i]))
    if s_sum < s_min:
        return s_sum
    else:
        return -1


def check_no_ddl(rs, start, real_ddls, cts, n, s_min, p_op, max_start, resource, preds):
    # resource = [max_r] * (max_start * 2)
    s_sum = 0
    for i in range(n):
        exe = int(start[i] + cts[i] + f(p_op[i], rs[i]))
        if start[i] + cts[i] < preds[i]: return -1
        j = start[i]
        while j < exe:
            # if j > real_ddls[i]: return -1
            # print(j, len(resource), i, len(rs))
            if resource[j] < rs[i]: return -1
            resource[j] -= rs[i]
            j += 1
        if exe > real_ddls[i]: 
            s_sum += exe - real_ddls[i]
        else:
            s_sum += 0
    return s_sum


def bf_run_all(ddls, preds, cts, ops, r_choice, max_r, rule_ids):
    n = len(ddls)
    max_start = max([x + y for x, y in zip(preds, ddls)])
    choose_r = cartesian_power(r_choice, n)
    choose_t = cartesian_power(np.arange(0, max_start), n)
    # print(len(choose_r) * len(choose_t))
    s_min = 100000000
    solution = []
    count = 0
    for r in choose_r:
        for t in choose_t:
            # if count % 1000000 == 0: print(f'{count}/{len(choose_r) * len(choose_t)}')
            res = check(r, t, [x + y for x,y in zip(preds, ddls)], cts, n, s_min, ops, max_start, max_r.copy(), preds)
            if res != -1:
                s_min = res
                solution = [r, t]
            count += 1
    new_solution = []
    if len(solution) == 0: return s_min, solution
    for i in range(len(solution[0])):
        new_solution.append([solution[0][i], solution[1][i], solution[1][i] + cts[i] + f(ops[i], solution[0][i]), rule_ids[i]])
    return s_min, new_solution


def ignore_ddl_bf(ddls, preds, cts, ops, r_choice, max_r, rule_ids):
    n = len(ddls)
    total_exe = 0
    for op in ops:
        total_exe += f(op, max(r_choice))
    for i in range(len(max_r)):
        if max_r[i] >= max(r_choice):
            break
    max_start = i + total_exe
    max_start_ddl = max([x + y for x, y in zip(preds, ddls)])
    max_start = max(max_start, max_start_ddl)
    choose_r = cartesian_power(r_choice, n)
    choose_t = cartesian_power(np.arange(0, max_start), n)
    # print(len(choose_r) * len(choose_t))
    s_min = 100000000
    solution = []
    count = 0
    for r in choose_r:
        for t in choose_t:
            # if count % 1000000 == 0: print(f'{count}/{len(choose_r) * len(choose_t)}')
            res = check_no_ddl(r, t, [x + y for x,y in zip(preds, ddls)], cts, n, s_min, ops, max_start, max_r.copy(), preds)
            if res != -1 and res < s_min:
                s_min = res
                solution = [r, t]
            count += 1
    new_solution = []
    if len(solution) == 0: return s_min, solution
    for i in range(len(solution[0])):
        new_solution.append([solution[0][i], solution[1][i], solution[1][i] + cts[i] + f(ops[i], solution[0][i]), rule_ids[i]])
    return s_min, new_solution



def t_pred_run(n, preds, ddls, cts, r_choice, ops, max_r):
    choose_r = cartesian_power(r_choice, n)
    max_start = max([x + y for x, y in zip(preds, ddls)])
    s_min = 100000000
    solution = []
    for r in choose_r:
        for t_1 in range(preds[0] - cts[0], preds[0] + 1):
            if n == 1:
                res = check(r, [t_1], ddls, cts, n, s_min, ops, max_start, max_r)
                if res != -1:
                    s_min = res
                    solution = [r, [t_1]]
            else:
                for t_2 in range(preds[1] - cts[1], preds[1] + 1):
                    if n == 2:
                        res = check(r, [t_1, t_2], ddls, cts, n, s_min, ops, max_start, max_r)
                        if res != -1:
                            s_min = res
                            solution = [r, [t_1, t_2]]
                    else:
                        for t_3 in range(preds[2] - cts[2], preds[2] + 1):
                            if n == 3:
                                res = check(r, [t_1, t_2, t_3], ddls, cts, n, s_min, ops, max_start, max_r)
                                if res != -1:
                                    s_min = res
                                    solution = [r, [t_1, t_2, t_3]]
                            else:
                                for t_4 in range(preds[3] - cts[3], preds[3] + 1):
                                    if n == 4:
                                        res = check(r, [t_1, t_2, t_3, t_4], ddls, cts, n, s_min, ops, max_start, max_r)
                                        if res != -1:
                                            s_min = res
                                            solution = [r, [t_1, t_2, t_3, t_4]]
                                    else:
                                        for t_5 in range(preds[4] - cts[4], preds[4] + 1):
                                            if n == 5:
                                                res = check(r, [t_1, t_2, t_3, t_4, t_5], ddls, cts, n, s_min, ops, max_start, max_r)
                                                if res != -1:
                                                    s_min = res
                                                    solution = [r, [t_1, t_2, t_3, t_4, t_5]]
                                            else:
                                                for t_6 in range(preds[5] - cts[5], preds[5] + 1):
                                                    if n == 6:
                                                        res = check(r, [t_1, t_2, t_3, t_4, t_5, t_6], ddls, cts, n,
                                                                    s_min, ops, max_start, max_r)
                                                        if res != -1:
                                                            s_min = res
                                                            solution = [r, [t_1, t_2, t_3, t_4, t_5, t_6]]
                                                    else:
                                                        for t_7 in range(preds[6] - cts[6], preds[6] + 1):
                                                            if n == 7:
                                                                res = check(r, [t_1, t_2, t_3, t_4, t_5, t_6, t_7],
                                                                            ddls, cts, n, s_min, ops, max_start, max_r)
                                                                if res != -1:
                                                                    s_min = res
                                                                    solution = [r, [t_1, t_2, t_3, t_4, t_5, t_6, t_7]]
                                                            else:
                                                                for t_8 in range(preds[7] - cts[7], preds[7] + 1):
                                                                    if n == 8:
                                                                        res = check(r,
                                                                                    [t_1, t_2, t_3, t_4, t_5, t_6, t_7,
                                                                                     t_8], ddls, cts, n, s_min, ops, max_start, max_r)
                                                                        if res != -1:
                                                                            s_min = res
                                                                            solution = [r, [t_1, t_2, t_3, t_4, t_5, t_6, t_7, t_8]]
                                                                    else:
                                                                        for t_9 in range(preds[8] - cts[8],
                                                                                         preds[8] + 1):
                                                                            if n == 9:
                                                                                res = check(r, [t_1, t_2, t_3, t_4, t_5,
                                                                                                t_6, t_7, t_8, t_9],
                                                                                            ddls, cts, n, s_min, ops, max_start, max_r)
                                                                                if res != -1:
                                                                                    s_min = res
                                                                                    solution = [r, [t_1, t_2, t_3, t_4, t_5, t_6, t_7, t_8, t_9]]
                                                                            else:
                                                                                for t_10 in range(preds[9] - cts[9],
                                                                                                  preds[9] + 1):
                                                                                    if n == 10:
                                                                                        res = check(r,
                                                                                                    [t_1, t_2, t_3, t_4,
                                                                                                     t_5, t_6, t_7, t_8,
                                                                                                     t_9, t_10], ddls,
                                                                                                    cts, n, s_min, ops, max_start, max_r)
                                                                                        if res != -1:
                                                                                            s_min = res
                                                                                            solution = [r, [t_1, t_2, t_3, t_4,
                                                                                                     t_5, t_6, t_7, t_8,
                                                                                                     t_9, t_10]]
                                                                                    else:
                                                                                        print("error")
                                                                                        return
    return s_min, solution


if __name__ == "__main__":
    # from edgeruler_code.test.macro_benchmark.main import prepare_P
    # t1 = time.time()
    # # s_min, solution = t_pred_run(4, [2, 20, 30, 50], [20, 20, 15, 20], [2, 2, 2, 2])
    # s_min, solution = run_all(3, [2, 20, 30], [20, 20, 15], [2, 2, 2])
    # t2 = time.time()
    # print(solution)
    # print(s_min)
    # print(t2 - t1)
    # res = check([2.0, 2.0, 2.0], [0, 18, 30], [20, 20, 15], [2, 2, 2], 3, 1000)
    # print(res)
    # prepare_P()
    # s_min, solution = bf_run_all([10, 3, 7], [0, 2, 3], [2, 2, 2],
    #                              [1000, 1000, 1000], [2.0, 4.0], 4.0, 3)
    # print(solution)
    # print(s_min)
    resource = [4.0] * 60
    s_min, solution = bf_run_all([2], [8], [4], [2000], [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], resource, [4])
    print(s_min, solution)
    s_min, solution = ignore_ddl_bf([2], [8], [4], [2000], [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], resource, [4])
    print(s_min, solution)