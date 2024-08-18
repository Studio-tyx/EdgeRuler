import redis as Redis

LOGIC_OP = {'>=', '<=', '==', '>', '<'}
MISS_RATE = 0.1


def separate_trigger_logic(trigger_str):
    op = ""
    for i_op in LOGIC_OP:
        if trigger_str.find(i_op) != -1:
            op = i_op
            break
    if op != "":
        trigger_str_split = trigger_str.split(op)
        trigger_value = float(trigger_str_split[1].strip())
        trigger = {"trigger_str": trigger_str, "trigger_name": trigger_str_split[0].strip(), "op": op,
                   "trigger_value": trigger_value}
    else:
        trigger = {"trigger_str": trigger_str, "trigger_name": trigger_str}
    return trigger


def merge_trigger(trigger):
    if trigger["op"] != None:
        return f'{trigger["trigger_name"]}{trigger["op"]}{trigger["trigger_value"]}'
    else:
        return trigger["trigger_name"]


# 检验单个trigger是否被触发
def single_trigger_is_triggered(trigger, data):
    op = trigger["op"]
    if op == ">=":
        return data >= trigger["trigger_value"]
    elif op == "<=":
        return data <= trigger["trigger_value"]
    elif op == "==":
        return data == trigger["trigger_value"]
    elif op == "<":
        return data < trigger["trigger_value"]
    elif op == ">":
        return data > trigger["trigger_value"]
    return False


class RuleTool:
    redis = Redis.Redis(host='10.214.131.191', port=6379, db=0, decode_responses=True)

    # tdengine = TDEngineTool()

    def get_rules(self, trigger_name):
        keys = self.redis.keys()
        trigger_strs_diff_rule = []
        for item in keys:
            if item.find(trigger_name) != -1:  # temp
                trigger_strs_diff_rule.append(item)  # temp<150
        rules = []
        for trigger_strs_single_rule in trigger_strs_diff_rule:  # temp<130 temp>150
            number_of_rules = self.redis.llen(trigger_strs_single_rule)
            for i_index_rules in range(number_of_rules):  # if t1 then a1 if t1 then a2
                rid = self.redis.lindex(trigger_strs_single_rule, i_index_rules)  # rules集合中的某条rule
                rule_dict = self.redis.hgetall(str(rid))
                actions_hash = rule_dict["Actions"].split("\', \'")
                actions = []
                for action_hash in actions_hash:  # "'hash_1', 'hash_2'"
                    action_hash = action_hash.replace("\'", "")
                    # print(self.redis.hgetall(action_hash))
                    actions.append(self.redis.hgetall(action_hash)["name"])
                condition_dict = rule_dict["Conditions"]  # 1) "src" 2) "c1" 3) "op" 4) ">" 5) "target" 6) "d1"

                multi_trigger_strs = rule_dict["Triggers"].split(',')
                triggers = []
                for trigger_str in multi_trigger_strs:
                    triggers.append(separate_trigger_logic(trigger_str))
                rule = {"rule": rule_dict, "mutli_trigger": rule_dict["Triggers"],
                        "triggers": triggers, "condition": condition_dict, "actions": actions, "miss_ratio": MISS_RATE}
                rules.append(rule)
        return rules

    # temp => temp < 130
    def get_event_from_trigger_name(self, trigger_name):
        keys = self.redis.keys()
        trigger_strs_diff_rule = []
        for item in keys:
            if item.find(trigger_name) != -1:  # temp
                trigger_strs_diff_rule.append(item)  # temp<150
        triggers = []
        for trigger_str in trigger_strs_diff_rule:
            trigger = separate_trigger_logic(trigger_str)
            triggers.append(trigger)
        return triggers

    def get_triggered_event_from_trigger_name(self, trigger_name, current_data):
        events = []
        triggers = self.get_event_from_trigger_name(trigger_name)
        for trigger in triggers:
            if single_trigger_is_triggered(trigger, current_data): events.append(trigger["trigger_str"])
        return events

    # def valid_rule(self, rule):
    #     for trigger in rule["triggers"]:
    #         data = self.tdengine.select_last_data('triggers', trigger["trigger_name"])
    #         if single_trigger_is_triggered(trigger, data) is not True:
    #             return False
    #     return True

    def get_all_triggers_name(self):
        triggers_name = []
        keys = self.redis.keys()
        for trigger_str in keys:
            triggers_name.append(separate_trigger_logic(trigger_str)["trigger_name"])
        return triggers_name


if __name__ == '__main__':
    rt = RuleTool()
    rules = rt.get_rules("temp")
    # for rule in rules:
    #     print(rule)
    #     print(rule["mutli_trigger"], rt.valid_rule(rule))
    print(rt.get_all_triggers_name())
