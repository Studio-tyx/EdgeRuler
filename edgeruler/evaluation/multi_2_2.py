import time
import math
import statistics
from set_up import f, R_CHOICE, MAX_RESOURCE


def collect_total_data():
    from set_up import get_truth as collect
    event = collect()
    res = []
    for horizon in event:
        res.extend(horizon)
    return res


def generate_ct_ddl_for_rule():
    from set_up import RULES, DDL_BASE
    cts = []
    ddls = []
    ops = []
    min_r = []
    for rule in RULES:
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


def on_demand_greedy(events, ops, cts):
    # print("------------ on-demand + greedy -------------")
    from set_up import MAX_CHOICE, RULES
    resource = [MAX_RESOURCE] * 13000
    solutions = []
    cost = []
    for event in events:
        t1 = time.time()
        allo_r = min(resource[event[0]], MAX_CHOICE[RULES[event[1]][2]])
        start_t = event[0]
        if allo_r == 0:
            for t in range(start_t, len(resource)):
                if resource[t] != 0:
                    allo_r = min(resource[t], MAX_CHOICE[RULES[event[1]][2]])
                    start_t = t
                    break
        finish_t = start_t + f(ops[event[1]], allo_r) + cts[event[1]]
        for t in range(start_t, math.ceil(finish_t)):
            resource[t] -= allo_r
        solutions.append([allo_r, event[0], start_t, finish_t, event[1]])
        t2 = time.time()
        cost.append(t2 - t1)
    # print(solutions)
    return solutions, cost


def on_demand_conservative(events, ops, cts, min_r):
    # print("------------ on-demand + conservative -------------")
    resource = [MAX_RESOURCE] * 13000
    solutions = []
    cost = []
    for event in events:
        t1 = time.time()
        allo_r = min_r[event[1]]
        start_t = event[0]
        if resource[event[0]] < allo_r:
            for t in range(start_t, len(resource)):
                if resource[t] >= min_r[event[1]]:
                    allo_r = min_r[event[1]]
                    start_t = t
                    break
        finish_t = start_t + f(ops[event[1]], allo_r) + cts[event[1]]
        for t in range(start_t, math.ceil(finish_t)):
            resource[t] -= allo_r
        solutions.append([allo_r, event[0], start_t, finish_t, event[1]])
        t2 = time.time()
        cost.append(t2 - t1)
    # print(solutions)
    return solutions, cost


def always_hot_greedy(events, ops, cts):
    # print("------------ always hot + greedy -------------")
    satisfied = {}
    solutions = []
    temp_r = MAX_RESOURCE
    cost = []
    from set_up import MAX_CHOICE, RULES
    last = []
    for event in events:
        if temp_r == 0:
            break
        else:
            if temp_r >= MAX_CHOICE[RULES[event[1]][2]]:
                if event[1] not in satisfied.keys():
                    satisfied[event[1]] = 0
                    temp_r -= MAX_CHOICE[RULES[event[1]][2]]
    for event in events:
        t1 = time.time()
        if event[1] in satisfied.keys():
            if satisfied[event[1]] <= event[0]:
                finish_t = math.ceil(event[0] + f(ops[event[1]],MAX_CHOICE[RULES[event[1]][2]]))
                solutions.append([MAX_CHOICE[RULES[event[1]][2]], event[0], event[0], finish_t, event[1]])
                satisfied[event[1]] = finish_t
            else:
                start_t = satisfied[event[1]]
                finish_t = math.ceil(start_t + f(ops[event[1]], MAX_CHOICE[RULES[event[1]][2]]))
                solutions.append([MAX_CHOICE[RULES[event[1]][2]], event[0], start_t, finish_t, event[1]])
                satisfied[event[1]] = finish_t
        else:
            last.append([event[0], event[1]])
        t2 = time.time()
        cost.append(t2 - t1)
    start_t = max(solutions[-1][3], events[-1][0])
    for item in last:
        finish_t = math.ceil(start_t + f(ops[item[1]], MAX_RESOURCE))
        solutions.append([MAX_RESOURCE, item[0], start_t, finish_t, item[1]])
        start_t = finish_t
    # print(solutions)
    # print("always hot + greedy:", solutions[])
    return solutions, cost



def always_hot_conservative(events, ops, cts):
    # print("------------ always hot + conservative -------------")
    satisfied = {}
    solutions = []
    temp_r = MAX_RESOURCE
    cost = []
    from set_up import DDL_BASE
    allo_r = DDL_BASE
    last = []
    for event in events:
        if temp_r == 0:
            break
        else:
            if temp_r >= allo_r:
                if event[1] not in satisfied.keys():
                    satisfied[event[1]] = 0
                    temp_r -= allo_r
    for event in events:
        t1 = time.time()
        if event[1] in satisfied.keys():
            if satisfied[event[1]] <= event[0]:
                finish_t = math.ceil(event[0] + f(ops[event[1]], allo_r))
                solutions.append([allo_r, event[0], event[0], finish_t, event[1]])
                satisfied[event[1]] = finish_t
            else:
                start_t = satisfied[event[1]]
                finish_t = math.ceil(start_t + f(ops[event[1]], allo_r))
                solutions.append([allo_r, event[0], start_t, finish_t, event[1]])
                satisfied[event[1]] = finish_t
        else:
            last.append([event[0], event[1]])
        t2 = time.time()
        cost.append(t2 - t1)
    start_t = max(solutions[-1][3], events[-1][0])
    for item in last:
        finish_t = math.ceil(start_t + f(ops[item[1]], MAX_RESOURCE))
        solutions.append([MAX_RESOURCE, item[0], start_t, finish_t, item[1]])
        start_t = finish_t
    # print(solutions)
    # print("always hot + conservative:", solutions[])
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
    # print(solutions)
    # print(latencys)
    print(f'dmr: {statistics.mean(dmrs)}, {statistics.stdev(dmrs)}')
    print(f'latency: {statistics.mean(latencys)}, {statistics.stdev(latencys)}')
    # print(f'{statistics.mean(rts)}, {statistics.stdev(rts)}')
    # print(f'cost: {statistics.mean(cost)}, {statistics.stdev(cost)}')
    return statistics.mean(dmrs), statistics.mean(latencys)


def eval_always_hot_resource(solutions):
    rts = []
    rule_list = []
    for solution in solutions:
        if solution[4] not in rule_list:
            rule_list.append(solution[4])
    resource_sum = solutions[-1][3] * MAX_RESOURCE
    for rule in rule_list:
        rts.append(resource_sum / len(rule_list))
    print(f'r: {statistics.mean(rts)}, {statistics.stdev(rts)}')
    print()
    return statistics.mean(rts)


def eval_resource(solutions):
    rts = []
    for solution in solutions:
        if type(solution[3]) is int:
            rts.append((solution[3] - solution[2]) * solution[0])
    print(f'r: {statistics.mean(rts)}, {statistics.stdev(rts)}')
    print()
    return statistics.mean(rts)



def run():
    dmrs = []
    latencys = []
    rts = []
    from set_up import LENGTH
    length = LENGTH
    event = collect_total_data()
    # print(event)

    cts, ddls, ops, min_r = generate_ct_ddl_for_rule()
    solutions, cost = on_demand_greedy(event, ops, cts)
    # print(solutions)
    d, l = evaluate_solution(solutions, ddls, cost)
    r = eval_resource(solutions)
    dmrs.append(d)
    latencys.append(l)
    rts.append(r)

    solutions, cost = on_demand_conservative(event, ops, cts, min_r)
    d, l = evaluate_solution(solutions, ddls, cost)
    r = eval_resource(solutions)
    dmrs.append(d)
    latencys.append(l)
    rts.append(r)

    solutions, cost = always_hot_greedy(event, ops, cts)
    d, l = evaluate_solution(solutions, ddls, cost)
    r = eval_always_hot_resource(solutions)
    dmrs.append(d)
    latencys.append(l)
    rts.append(r)

    solutions, cost = always_hot_conservative(event, ops, cts)
    d, l = evaluate_solution(solutions, ddls, cost)
    r = eval_always_hot_resource(solutions)
    dmrs.append(d)
    latencys.append(l)
    rts.append(r)
    return dmrs, latencys, rts


if __name__ == "__main__":
    run()
