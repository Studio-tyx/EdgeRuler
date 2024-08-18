


from edgeruler_code.evaluation.evaluator import Evaluator

# from memory_profiler import profile
# @profile
def run():
    e = Evaluator()
    import psutil
    mem = []
    for i in range(5):
        process = psutil.Process()
        start_memory = process.memory_info().rss
        e.callback(None, None, None, f'out_pres>1012.3, {i}, darknet'.encode('utf-8'))
        # 记录函数执行后的内存使用情况
        end_memory = process.memory_info().rss
        # 计算内存使用峰值
        memory_peak = end_memory - start_memory
        mem.append(memory_peak)
        print(start_memory, end_memory)
    print(mem)
    print(sum(mem) / len(mem))


if __name__ == "__main__":
    run()