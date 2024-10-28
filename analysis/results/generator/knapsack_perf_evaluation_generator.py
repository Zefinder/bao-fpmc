from math import ceil, floor
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
from results.generator.generator_utils import *
from utils.log_utils import *
from utils.generate_prem import interval

# Constants
system_number = 10000
processor_number = 1
tasks_per_processor = [4, 6, 8, 10, 12]
period_interval = interval(100, 1000)
random_delta_number = 5


# Functions
def analyse_data(result_log: log_results) -> list[tuple[int, int, float]]:
    results: list[tuple[int, int, float]] = []
    
    # for _ in range(0, system_number * len(tasks_per_processor) * random_delta_number):
    for _ in range(0, system_number * random_delta_number): # TODO Remove when real tests
        line = result_log.read_line().split(',')
        results.append((int(line[0]), int(line[1]), float(line[2])))
    
    return results


# {2, {100, 0.5}} for 2 tasks, one entry is delta = 100 with time 0.5
def create_dict_t2d(results: list[tuple[int, int, float]]) -> dict[int, list[tuple[int, float]]]: # Task number to delta
    result_dict: dict[int, list[tuple[int, float]]] = {}
    pre_results: dict[int, dict[int, list[float]]] = {}
    
    for result in results:
        jobs_number = result[0]
        delta = result[1]
        time = result[2]
        
        if jobs_number in pre_results:
            if delta in pre_results[jobs_number]:
                pre_results[jobs_number][delta].append(time)
            else:
                pre_results[jobs_number][delta] = [time]
        else:
            if jobs_number < 57: # TODO Remove when real tests
                pre_results[jobs_number] = {delta: [time]}
    
    for jobs_number in pre_results:
        result_dict[jobs_number] = []
        for delta in pre_results[jobs_number]:
            result_dict[jobs_number].append((delta, sum(pre_results[jobs_number][delta]) / len(pre_results[jobs_number][delta])))
    
    return result_dict


def create_dict_d2t(): # Delta to task number
    pass
    

def generate_knapsack_performance(resultsv1: dict[int, list[tuple[int, float]]], resultsv2: dict[int, list[tuple[int, float]]]):
    jobs_numbers = list(resultsv1.keys())
    jobs_numbers.sort()
    fig, axs = plt.subplots(ceil(len(jobs_numbers) / 3), 3, figsize=(30, 50))
    
    for index in range(0, len(jobs_numbers)):
        job_number = jobs_numbers[index]
        plotx = floor(index / 3)
        ploty = index % 3
        
        x1 = []
        y1 = []
        for delta, time in resultsv1[job_number]:
            x1.append(delta)
            y1.append(time)
            
        x2 = []
        y2 = []
        for delta, time in resultsv2[job_number]:
            x2.append(delta)
            y2.append(time)
        
        axs[plotx, ploty].set_title(f'Job number: {job_number:d}')
        axs[plotx, ploty].plot(x1, y1)
        axs[plotx, ploty].plot(x2, y2)
    
    plt.subplots_adjust(bottom=0.1, 
                        top=0.9, 
                        wspace=0.4, 
                        hspace=0.5
                        )
    plt.savefig(results_directory + 'test.png')

def generate() -> None:
    if assert_existing_result_files('knapsack_perf_evaluation.log', 'knapsackv2_perf_evaluation.log'):
        # Read classic log
        knapsack_log = log_file_class()
        knapsack_results = knapsack_log.create_result_file('knapsack_perf_evaluation.log')
        knapsack_data = analyse_data(knapsack_results)
        knapsack_results.close()
        knapsackv1_data = create_dict_t2d(knapsack_data)
        keys = list(knapsackv1_data.keys())
        keys.sort()
        print(keys)

        # Read knapsack log
        knapsackv2_log = log_file_class()
        knapsackv2_results = knapsackv2_log.create_result_file('knapsackv2_perf_evaluation.log')
        knapsack_data = analyse_data(knapsackv2_results)
        knapsackv2_results.close()
        knapsackv2_data = create_dict_t2d(knapsack_data)
        keys = list(knapsackv2_data.keys())
        keys.sort()
        print(keys)
        
        generate_knapsack_performance(knapsackv1_data, knapsackv2_data)
        
        


if __name__ == '__main__':
    exit(1)