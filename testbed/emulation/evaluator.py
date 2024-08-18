

class Evaluator:

    def latency_breakdown(self, events):
        for rules in events:
            exe_latency = 0
            create_latency = 0
            for event in rules:
                exe_latency += event["exec time"]
                create_latency += event["create time"]
            print(f'rule:{events.index(rules)}, total latency:{(exe_latency + create_latency) / len(rules)}, '
                  f'create:{create_latency / len(rules)}, execution:{exe_latency / len(rules)}')


    def ddl_miss_ratio(self, events, rules):
        for event_s, r in zip(events, rules):
            miss = 0
            for event in event_s:
                real_cost = event["create time"] + event["exec time"]
                if real_cost > r["ddl"]:
                    miss += 1
            print(f'rule:{events.index(event_s)}, miss ratio:{miss / len(event_s)}, ddl:{r["ddl"]}')


    def measure_resource(self, events):
        for rules in events:
            sum_resource = 0
            for event in rules:
                sum_resource += (event["resource"] * (event["create time"] + event["exec time"]))
            print(f'rule:{events.index(rules)}, resource cost:{sum_resource / len(rules)}')


    def emulation_evaluate(self, events, ddls):
        self.latency_breakdown(events)
        self.ddl_miss_ratio(events, ddls)
        self.measure_resource(events)
        print(f'==========================')