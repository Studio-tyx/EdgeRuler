import time

import math
import statistics

from set_up import f, MAX_RESOURCE


def collect_total_data():
    from set_up import get_truth as collect
    event = collect()
    res = []
    for horizon in event:
        res.extend(horizon)
    return res


def generate_ct_ddl_for_rule(rules):
    from set_up import R_CHOICE, DDL_BASE
    cts = []
    ddls = []
    ops = []
    min_r = []
    for rule in rules:
        ops.append(rule[2])
        ddl = f(rule[2], DDL_BASE)
        cts.append(rule[4])
        ddls.append(ddl)
        allo_r = MAX_RESOURCE
        for r in R_CHOICE:
            if f(rule[2], r) <= (ddl - rule[4]):
                allo_r = r 
                break
        min_r.append(allo_r)
    return cts, ddls, ops, min_r


def on_demand_even(events, ops, cts):
    print("------------ on-demand + greedy -------------")
    from set_up import RULES
    resource = [MAX_RESOURCE] * 13000
    solutions = []
    cost = []
    for event in events:
        t1 = time.time()
        allo_r = min(resource[event[0]], MAX_RESOURCE)
        start_t = event[0]
        if allo_r == 0:
            for t in range(start_t, len(resource)):
                if resource[t] != 0:
                    allo_r = min(resource[t], MAX_RESOURCE)
                    start_t = t
                    break
        finish_t = start_t + f(ops[event[1]], allo_r)
        for t in range(start_t, math.ceil(finish_t)):
            resource[t] -= allo_r
        solutions.append([allo_r, event[0], start_t, finish_t, event[1]])
        t2 = time.time()
        cost.append(t2 - t1)
    # print(solutions)
    return solutions, cost


def evaluate_solution(solutions, ddls, cost):
    ddl_miss = {}
    latency = {}
    # print(solutions)
    total_rt = 0
    for i in range(len(ddls)):
        ddl_miss[i] = [0, 0]
        latency[i] = 0
    for solution in solutions:
        rule_id = solution[4]
        if solution[3] > ddls[rule_id] + solution[1]:
            ddl_miss[rule_id][0] += 1
        else:
            ddl_miss[rule_id][1] += 1
        latency[rule_id] += (solution[3] - solution[1])
    dmrs = []
    latencys = []
    sorted_keys = sorted(ddl_miss.keys())
    for rule in sorted_keys:
        rule_sum = ddl_miss[rule][0] + ddl_miss[rule][1]
        if rule_sum != 0:   
            dmrs.append(ddl_miss[rule][0] / rule_sum)
            latencys.append(latency[rule] / rule_sum)
    print(latencys)
    print(f'dmr: {statistics.mean(dmrs)}, {statistics.stdev(dmrs)}')
    print(f'latency: {statistics.mean(latencys)}, {statistics.stdev(latencys)}')
    # print(f'{statistics.mean(rts)}, {statistics.stdev(rts)}')
    # print(f'cost: {statistics.mean(cost)}, {statistics.stdev(cost)}')
    return statistics.mean(dmrs), statistics.mean(latencys)


def eval_resource(solutions):
    rts = []
    for solution in solutions:
        if type(solution[3]) is int:
            rts.append((solution[3] - solution[2]) * solution[0])
    print(f'r: {statistics.mean(rts)}, {statistics.stdev(rts)}')
    print()
    return statistics.mean(rts)



def run():
    from set_up import LENGTH, RULES
    length = LENGTH
    event = collect_total_data()
    # print(event)
    cts, ddls, ops, min_r = generate_ct_ddl_for_rule(RULES)
    solutions, cost = on_demand_even(event, ops, cts)
    # print(solutions)
    evaluate_solution(solutions, ddls, cost)
    eval_resource(solutions)


if __name__ == "__main__":
    run()
