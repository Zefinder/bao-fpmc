from math import ceil
from analyse_utils import get_variables_from_big_file

# Constants
task_to_info: dict[int, tuple[str, int]] = {
    0: ('MPEG2', 88),
    1: ('Count negative', 144),
    2: ('Binary search', 8),
    3: ('Weight average', 200)
}


def main():
    # Open result file and read line by line. 
    # 4 tasks: 
    # 0 -> MPEG2
    # 1 -> Count negative
    # 2 -> Binary search
    # 3 -> Weight average
    memory_phases = get_variables_from_big_file('max_', '../extract/bench_solo_legacy-execution-solo-24-11-13-1.py')
    
    results: dict[int, list[int]] = {}    
    results_start = 27
    with open('../bench_solo_legacy-execution-tacle-measurement-24-11-15-1.log', 'r') as file: 
        for _ in range(0, results_start):
            file.readline()
        
        line = file.readline()
        while line != '':
            # Fill dict with measured times
            info = line[12:].split(',')
            task_id = int(info[0])
            time = int(info[1])
            if task_id not in results:
                results[task_id] = [] # Skip the first result because will have extra time for nothing
            else:
                results[task_id].append(time)
            line = file.readline()
        
        # Display results
        for task_id in task_to_info:
            (task_name, prefetch_size) = task_to_info[task_id]
            times = results[task_id]
            memory_phase_time = memory_phases[f'max_{prefetch_size:d}kB_ns']
            
            max_ns = max(times)
            min_ns = min(times)
            avg_ns = sum(times) / len(times)
            print('Results for', task_name)
            print(f'\tmax: {max_ns} ns ({max_ns / 1000} µs)')
            print(f'\tmin: {min_ns} ns ({min_ns / 1000} µs)')
            print(f'\tavg: {avg_ns} ns ({avg_ns / 1000} µs)')
            print(f'\tTask characteristics: m={memory_phase_time} ns ({ceil(memory_phase_time / 1000)} µs), c={max_ns - memory_phase_time} ns ({ceil((max_ns - memory_phase_time) / 1000)} µs)')
            print()
            

if __name__ == '__main__':
    main()