import time
from set_up import f

MAX = 10000000

def find_start(r, c, s, op, r_horizon):
    t_pred = c[1]
    t_pred_ct = c[0]
    ddl = c[3]
    ct = c[2]
    lbd = c[6]
    for t in range(t_pred_ct, min(lbd + 1, len(r_horizon))):
        if r <= r_horizon[t]:
            end = t + f(op, r) + ct
            if r <= min(r_horizon[t: end]) and end <= t_pred + ddl:
                return t
    return MAX


def find_ddl_delta(r, c, s, op, r_horizon):
    t_pred = c[1]
    t_pred_ct = c[0]
    ddl = c[3]
    ct = c[2]
    lbd = c[6]
    for t in range(t_pred_ct):
        if r <= r_horizon[t]:
            if t + f(op, r) + ct <= t_pred + ddl:
                return t
    return MAX


def find_start_ignore_ddl(r, c, s, op, r_horizon):
    t_pred = c[1]
    t_pred_ct = c[0]
    # ddl = c[3]
    ct = c[2]
    lbd = c[6]
    exe_time = f(op, r) + ct
    for t in range(t_pred_ct, len(r_horizon)):
        if r <= min(r_horizon[t:t + exe_time]):
            # print(r, t, r_horizon[:30])
            return t
    return MAX


def find_exe(solution):
    # print(solution)
    return max([row[1] for row in solution])

# solution: [[2.0, 12, 42], ...
# resource, finish, rt


def find_level(solution, t):
    i = 0
    for i in range(len(solution)):
        if solution[i][1] > t: break
    return i


def find_sum_by_level(solution, level):
    s = 0
    for i in range(len(solution)):
        if i < level:
            s += solution[i][3]
    return s


def merge(c, next_t):
    # print("in:", c, next_t)
    before_s = []
    res_dict = {}
    min_ddl = MAX
    find_solution = False
    for i in range(len(c)):
        for j in range(len(c[i])):
            if c[i][j] == MAX or c[i][j] is None: continue
            if type(c[i][j]) == int:
                if c[i][j] < 0:
                    if abs(c[i][j]) <= abs(min_ddl):
                        min_ddl = c[i][j]
                    continue
            find_solution = True
            exe = find_exe(c[i][j])
            if exe <= next_t:
                if len(before_s) == 0:
                    before_s = [[c[i][j], 0, find_sum_by_level(c[i][j], len(c[i][j]))]]
                else:
                    if find_sum_by_level(c[i][j], len(c[i][j])) < before_s[0][2]:
                        before_s = [[c[i][j], 0, find_sum_by_level(c[i][j], len(c[i][j]))]]
            else:
                if exe not in res_dict.keys():
                    level = find_level(c[i][j], next_t)
                    res_dict[exe] = [[c[i][j], level, find_sum_by_level(c[i][j], level)]]
                else:
                    level = find_level(c[i][j], next_t)
                    s = find_sum_by_level(c[i][j], level)
                    find = False
                    for other in range(len(res_dict[exe])):
                        flag = False
                        if level == res_dict[exe][other][1]:
                            for l in range(level, len(c[i][j])):
                                if c[i][j][l] != res_dict[exe][other][0][l]:
                                    flag = True
                                    break
                            if res_dict[exe][other][2] > s and flag is False:
                                res_dict[exe][other] = [c[i][j], level, s]
                                find = True
                    if find is not True:
                        res_dict[exe].append([c[i][j], level, s])
    if len(before_s) != 0:
        res_dict[next_t] = before_s
    # print("merge", res_dict)
    res = []
    for t in res_dict.keys():
        if len(res_dict[t]) == 1:
            res.append(res_dict[t][0][0])
        else:
            for d in res_dict[t]:
                res.append(d[0])
    if find_solution is False: 
        # print("min_ddl:", min_ddl)
        return min_ddl
    return res


def find_last_min(c, containers):
    rt_min = MAX
    s_min = []
    for i in range(len(c)):
        for j in range(len(c[i])):
            if c[i][j] == MAX: continue
            if type(c[i][j]) == int: continue
            # print([row[3] for row in c[i][j]])
            rt = sum([row[3] for row in c[i][j]])
            if rt_min > rt:
                rt_min = rt
                s_min = c[i][j]
            # print(rt, [row[3] for row in c[i][j]])
    res = []
    for c in s_min:
        # [r, t_find, exe, rule_id, pred]
        res.append([c[0], c[6], c[1], c[4], c[2]])
    return rt_min, res


def greedy_run(ddls, t_preds, cts, ops, choice_r, r_horizon, rule_ids, delta_t):
    containers = []
    for i in range(len(t_preds)):
        if t_preds[i] < cts[i]:
            containers.append([0, t_preds[i], cts[i], ddls[i], rule_ids[i], ops[i], (t_preds[i] + delta_t[i])])
        else:
            containers.append([t_preds[i] - cts[i], t_preds[i], cts[i], ddls[i], rule_ids[i], ops[i], (t_preds[i] + delta_t[i])])
    containers.sort(key=lambda x: x[0])
    ops = [item[5] for item in containers]
    cts = [item[2] for item in containers]
    pre_exe = [0]
    for i in range(len(containers)):
        c = [[MAX] * len(choice_r) for i in range(len(pre_exe))]
        copy_c = [[MAX] * len(choice_r) for i in range(len(pre_exe))]
        # print("before", pre_exe)
        for solution in pre_exe:
            for r in choice_r:
                # if f(ops[i], r) > containers[i][3]: continue
                if r > max(r_horizon): continue
                if solution == 0: r_former = r_horizon
                else: r_former = solution[-1][5]
                # print("b", r_former)
                t_find = find_start(r, containers[i], solution, ops[i], r_former.copy())
                # print("t find:", t_find, containers[i][0], r)
                if t_find < 0:
                    delta_ddl = find_ddl_delta(r, containers[i], solution, ops[i], r_former.copy())
                    c[pre_exe.index(solution)][choice_r.index(r)] = delta_ddl
                    if delta_ddl != MAX:
                        continue
                if t_find + f(ops[i], r) + cts[i] > containers[i][1] + containers[i][3]:
                    t_find = MAX
                if 0 <= t_find < MAX:
                    exe = t_find + containers[i][2] + f(ops[i], r)
                    # print("t_find", t_find, "exe", exe, "solution", solution)
                    r_now = solution_r_iter(r_former.copy(), t_find, exe, r)
                    #  containers.append([t_preds[i] - cts[i], t_preds[i], cts[i], ddls[i], rule_ids[i], ops[i], (t_preds[i] + delta_t[i])])
                    if solution == 0:
                        # print(c)
                        c[pre_exe.index(solution)][choice_r.index(r)] = [[r, exe, containers[i][1], (exe - t_find), containers[i][4], r_now, t_find]]
                    else:
                        c[pre_exe.index(solution)][choice_r.index(r)] = solution + [[r, exe, containers[i][1], (exe - t_find), containers[i][4], r_now, t_find]]
                        # print("single", c[pre_exe.index(solution)][RESOURCE.index(r)])
        if i != len(containers) - 1:
            pre_exe = merge(c, containers[i + 1][0])
            # print("pre", pre_exe, containers[i + 1][0])
        # print(" ")
        if type(pre_exe) == int:
            # print("need to be dbp", [[containers[i][4], containers[i][1], pre_exe]])
            return MAX, [[containers[i][4], containers[i][1], pre_exe]]
    return find_last_min(c, containers)


def ignore_ddl_greedy(ddls, t_preds, cts, ops, choice_r, r_horizon, rule_ids, delta_t):
    containers = []
    for i in range(len(t_preds)):
        if t_preds[i] < cts[i]:
            containers.append([0, t_preds[i], cts[i], ddls[i], rule_ids[i], ops[i], (t_preds[i] + delta_t[i])])
        else:
            containers.append([t_preds[i] - cts[i], t_preds[i], cts[i], ddls[i], rule_ids[i], ops[i], (t_preds[i] + delta_t[i])])
    containers.sort(key=lambda x: x[0])
    ops = [item[5] for item in containers]
    cts = [item[2] for item in containers]
    pre_exe = [0]
    for i in range(len(containers)):
        c = [[MAX] * len(choice_r) for i in range(len(pre_exe))]
        copy_c = [[MAX] * len(choice_r) for i in range(len(pre_exe))]
        # print("before", pre_exe)
        for solution in pre_exe:
            for r in choice_r:
                # if f(ops[i], r) > containers[i][3]: continue
                if r > max(r_horizon): continue
                if solution == 0: r_former = r_horizon
                else: r_former = solution[-1][5]
                # print("r_former", r_former[:30])
                t_find = find_start_ignore_ddl(r, containers[i], solution, ops[i], r_former.copy())
                # print("t_find:", r_former.copy()[0:30], t_find, containers[i][0], r)
                if 0 <= t_find < MAX:
                    exe = t_find + containers[i][2] + f(ops[i], r)
                    # print("solution", solution)
                    # print(f'r:{r}, t_find:{t_find}, finish:{exe}, exe:{f(ops[i], r)}, ct:{containers[i][2]}')
                    r_now = solution_r_iter(r_former.copy(), t_find, exe, r)
                    #  containers.append([t_preds[i] - cts[i], t_preds[i], cts[i], ddls[i], rule_ids[i], ops[i], (t_preds[i] + delta_t[i])])
                    # print("r_latter", r_now[:30])
                    extra = 0
                    if exe > containers[i][1] + containers[i][3]:
                        extra = exe - containers[i][1] - containers[i][3]
                    if solution == 0:
                        # print(c)
                        c[pre_exe.index(solution)][choice_r.index(r)] = [[r, exe, containers[i][1], extra, containers[i][4], r_now, t_find]]
                    else:
                        c[pre_exe.index(solution)][choice_r.index(r)] = solution + [[r, exe, containers[i][1], extra, containers[i][4], r_now, t_find]]
                        # print("single", c[pre_exe.index(solution)][RESOURCE.index(r)])
        if i != len(containers) - 1:
            pre_exe = merge(c, containers[i + 1][0])
    return find_last_min(c, containers)


def solution_r_iter(r_former, t_start, exe, r):
    for t in range(t_start, min(exe, len(r_former))):
        r_former[t] -= r
    return r_former




if __name__ == "__main__":
    prepare_P()
    r_now = [6.0] * 50
    s_min, solution = greedy_run([2, 2, 2], [0, 4, 8], [1, 1, 1], [2000, 2000, 2000], [1.0, 2.0, 4.0], r_now, [4, 2, 1], [0, 0, 0])
    
    print(solution)
    print(s_min)

    s_min, solution = ignore_ddl_greedy([5, 5, 5], [0, 4, 8], [1, 1, 1], [2000, 2000, 2000], [1.0, 2.0, 4.0], r_now, [4, 2, 1], [0, 0, 0])
    
    print(solution)
    print(s_min)