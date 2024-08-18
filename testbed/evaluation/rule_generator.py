import argparse
import hashlib
import re
import sys

import redis


def maketheparser():
    parser = argparse.ArgumentParser(description=__doc__, add_help=True)
    parser.add_argument("-a", "--add", default=None, type=str,
                        help="Add an IFTTT rule like \"IF trigger1[, trigger2, ...] [WHEN condition1, condition2, ...] THEN action1[,action2, ...]\".")
    parser.add_argument("-t", "--test", default=False, action="store_true", help="Test connection to the Redis server.")
    parser.add_argument("-r", "--reset", default=False, action="store_true", help="Reset the db.")
    parser.add_argument("--debug", default=False, action="store_true", help="Print debug info.")
    return parser


def main(args=None):
    P = maketheparser()
    A = P.parse_args(args=args)

    r = redis.Redis(host='10.214.131.191', port=6379, db=0,
                    decode_responses=True)  # decode_responses=True: 控制redis存数据是string格式

    # md5encoder = hashlib.md5()

    if A.reset:
        print("Removing db...")
        r.flushdb()
    if A.test:
        r.ping()
        print("Add a key:test, value:runoob")
        r.set('test', 'runoob')
        print("Get the key:test from Redis")
        print(r.get('test'))
        print("Delete the key:test from Redis")
        r.delete('test')
        print("Get the key:test from Redis")
        print(r.get('test'))
    if A.add is not None:
        trigger_loc = A.add.find("IF")
        condition_loc = A.add.find("WHEN")
        action_loc = A.add.find("THEN")
        if trigger_loc == -1 or action_loc == -1:
            print("Invalid rule.")
        else:
            if condition_loc != -1:
                triggers = A.add[trigger_loc + 2: condition_loc]
                conditions = A.add[condition_loc + 5: action_loc]
            else:
                triggers = A.add[trigger_loc + 2: action_loc]
                conditions = ""
            actions = A.add[action_loc + 5:]

            # add conditions to the Redis
            conditions = conditions.split(',')
            op_pattern = '[">", "<", "==", ">=", "<=", "!="]'
            condition_ids = []
            for condition in conditions:
                src, target = re.split(op_pattern, condition.strip())
                op = condition.strip()[len(src):-len(target)].strip()
                tmp_dict = {"src": src, "op": op, "target": target}
                md5encoder = hashlib.new('md5')
                md5encoder.update(str(tmp_dict).encode('utf-8'))
                cid = md5encoder.hexdigest()
                r.hmset(cid, tmp_dict)
                condition_ids.append(cid)

            # add actions to the Redis
            actions = actions.split(',')
            action_ids = []
            ## TODO: preprocess action, match action and function id (that can directly call a container)
            for action in actions:
                md5encoder = hashlib.new('md5')
                md5encoder.update(action.strip().encode('utf-8'))
                fid = md5encoder.hexdigest()
                r.hmset(fid, {"name": action.strip()})
                action_ids.append(fid)

            # add the rule to the Redis
            tmp_dict = {"Triggers": str(triggers).strip(), "Conditions": str(condition_ids)[1:-1],
                        "Actions": str(action_ids)[1:-1]}
            md5encoder = hashlib.new('md5')
            md5encoder.update(str(tmp_dict).encode('utf-8'))
            rid = md5encoder.hexdigest()
            r.hmset(rid, tmp_dict)

            # add triggers to the Redis
            triggers = triggers.split(',')
            for trigger in triggers:
                r.rpush(trigger.strip(), rid)

            if A.debug:
                print("Triggers: ", triggers)
                print("Conditions: ", conditions)
                print("Actions: ", actions)

                print("Rule store in Redis:")
                print(r.hgetall(str(rid)))

                print("Triggers store in Redis:")
                for trigger in triggers:
                    print(trigger)
                    print("Trigger {}:".format(trigger.strip()))
                    list_len = r.llen(trigger.strip())
                    for index in range(list_len):
                        print(r.lindex(trigger.strip(), index))

                print("Conditions store in Redis:")
                for cid in condition_ids:
                    print(r.hgetall(cid))

                print("Actions store in Redis:")
                for fid in action_ids:
                    print(r.hgetall(fid))

    return 0


if __name__ == '__main__':
    sys.exit(main())
