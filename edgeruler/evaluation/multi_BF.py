import math
import time

import pandas as pd

from bruce_force_n import bf_run_all
from bruce_force_n import ignore_ddl_bf


def organize_time(event, horizon, length):
    current = 0
    horizon_time = []
    i = 0
    time_set = []
    while current < length:
        if i < len(event) and current <= event[i][0] < current + horizon:
            time_set.append(event[i])
            i += 1
        else:
            horizon_time.append(time_set)
            current += horizon
            time_set = []
    return horizon_time


def generate_ct_ddl():
    from set_up import f, RULES, DDL_BASE
    cts = []
    ddls = []
    for rule in RULES:
        cts.append(rule[4])
        ddls.append(f(rule[2], DDL_BASE))
    return cts, ddls


def partition_by_horizon(cts, ddls, t, current, horizon):
    horizon_cts = []
    horizon_t = []
    horizon_ddls = []
    horizon_p = []
    horizon_ids = []
    horizon_delta = []
    from set_up import RULES
    # print(current, len(t))
    for event in t[int(current / horizon)]:
        horizon_t.append(event[0] - current)
        horizon_ddls.append(ddls[event[1]])
        horizon_cts.append(cts[event[1]])
        horizon_p.append(RULES[event[1]][2])
        horizon_ids.append(event[1])
        horizon_delta.append(RULES[event[1]][3])
    return horizon_cts, horizon_ddls, horizon_t, horizon_p, horizon_ids, horizon_delta


from set_up import MAX_RESOURCE


def compare_run():
    from set_up import LENGTH, HORIZON_LENGTH, R_CHOICE, get_truth
    length = LENGTH
    horizon = HORIZON_LENGTH
    true_event = get_truth()
    pred_t = true_event
    cts, ddls = generate_ct_ddl()
    print("--------calculating, format:[r, t_find, exe, rule_id, pred]---------")
    current = 0
    h_r = [MAX_RESOURCE] * int(length * 5)
    solutions = []
    cost = []
    for i in range(len(true_event)):
        if len(true_event[i]) == 0:
            current += horizon
            continue
        horizon_cts, horizon_ddl, horizon_t, horizon_p, horizon_ids, horizon_delta = partition_by_horizon(cts, ddls,
                                                                                                    pred_t, current, horizon)
        horizon_r = h_r[current:]

        t1 = time.time()
        if len(horizon_t) == 0:
            solution = []
        else:
            no_solution = False  
            
            s_min, solution = bf_run_all(horizon_ddl, horizon_t, horizon_cts, horizon_p, R_CHOICE, horizon_r, horizon_ids)
            if s_min == 100000000:
                no_solution = True
                s_min, solution = ignore_ddl_bf(horizon_ddl, horizon_t, horizon_cts, horizon_p, R_CHOICE, horizon_r, horizon_ids)
            
        t2 = time.time()
        solution, h_r = r_iteration_with_add(solution, h_r, current, horizon, cts, R_CHOICE, true_event[i])
        if no_solution is True: 
            print(f'calculate:{current}, ddl-latency:{s_min}, cost:{round((t2 - t1), 2)}, solution:{solution}')
        else:
            print(f'calculate:{current}, s_min:{s_min}, cost:{round((t2 - t1), 2)}, solution:{solution}')

        cost.append(t2 - t1)
        solutions.append(solution)
        current += horizon
    # print(solutions)
    print(f'-------------result of horizon:{horizon}--------------')
    evaluate_new(solutions, ddls, true_event, horizon, cost)
    # print(f'avg cost:{round(sum(cost) / len(cost), 2)}, list:{cost}')
    # print(absolute_preds)
    # print(cost)


def delta_t_repredict(s_min, solution):
    return s_min, solution


def add_container(h_r, t_pred, op, ct, rule_id, want_r):
    from greedy_min_latency import f
    solution = None
    if h_r[t_pred] >= want_r:
        exe_time = int(t_pred + ct + f(op, want_r))
        for i_t in range(t_pred, exe_time):
            h_r[i_t] -= want_r
        solution = [want_r, t_pred, exe_time, rule_id]
    else:
        next_t = t_pred
        while next_t < len(h_r):
            if h_r[next_t] >= want_r:
                exe_time = int(next_t + ct + f(op, want_r))
                for i_t in range(t_pred, exe_time):
                    h_r[i_t] -= want_r
                solution = [want_r, t_pred, exe_time, rule_id]
                break
            next_t += 1
    return solution


def r_iteration_with_add(solution, h_r, current, horizon, cts, r_choice, real_events):
    if len(solution) == 0 or len(solution[0]) == 3: solution = []
    min_r_choice = min(r_choice)
    pred_id = [item[3] for item in solution]
    lost_solutions = []
    for s in solution:
        s[1] += current
        s[2] += current
        for t in range(s[1], s[2]):
            if (t - current) >= len(h_r):
                for i in range(t - current - len(h_r) + 1):
                    h_r.append(MAX_RESOURCE)
            h_r[t] -= s[0]
            if h_r[t] < 0: print(f't:{t}, solution:{solution}')
    for event in real_events:
        if event[1] not in pred_id:
            new_solution = add_container(h_r, event[0], RULES[event[1]][2], cts[event[1]], event[1], min_r_choice)
            lost_solutions.append(new_solution)
        else:
            pred_id.remove(event[1])
    solution.extend(lost_solutions)
    return solution, h_r


def evaluate_new(solutions, ddls, true_event, horizon, cost):
    exe_times = [[] for _ in range(len(ddls))]
    rts = []
    ddl_miss = [0] * len(ddls)
    rule_event = [0] * len(ddls)
    latency = [0] * len(ddls)
    for i in range(len(solutions)):
        for j in range(len(solutions[i])):
            rule_id = solutions[i][j][3]
            rt = ((solutions[i][j][2] - solutions[i][j][1]) * solutions[i][j][0])
            exe_times[rule_id].append(solutions[i][j][2])
            rts.append(rt)
    for i in range(len(ddls)):
        rule_exe_time = exe_times[i]
        rule_exe_time.sort()
        exe_times[i] = rule_exe_time
    for h_event in true_event:
        for event in h_event:
            rule_id = event[1]
            if len(exe_times[rule_id]) == 0:
                print("len(exe_times[rule_id]) == 0: ", rule_id)
            for i in range(len(exe_times[rule_id])):
                if exe_times[rule_id][0] >= event[0]:break
                else:
                    exe_times[rule_id].remove(exe_times[rule_id][0])
            recent_exe = exe_times[rule_id][0]
            if event[0] + ddls[rule_id] < recent_exe:
                ddl_miss[rule_id] += 1
            latency[rule_id] += (recent_exe - (event[0]))
            exe_times[rule_id].remove(recent_exe)
            rule_event[rule_id] += 1
    for rule in range(len(ddls)):
        if rule_event[rule] == 0: continue
        ddl_miss[rule] = ddl_miss[rule] / rule_event[rule]
        latency[rule] = latency[rule] / rule_event[rule]
        print(f'dmr rule {rule}:{ddl_miss[rule]}')
    print("latency", latency)
    import statistics
    print(f'{horizon}, {statistics.mean(ddl_miss)}, {statistics.stdev(ddl_miss)}')
    print(f'{horizon}, {statistics.mean(latency)}, {statistics.stdev(latency)}')
    print(f'{horizon}, {statistics.mean(rts)}, {statistics.stdev(rts)}')
    print(f'{horizon}, {statistics.mean(cost)}, {statistics.stdev(cost)}')
    



if __name__ == "__main__":
    compare_run()


