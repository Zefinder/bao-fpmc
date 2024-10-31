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
    
    for task_number in tasks_per_processor:
        for _ in range(0, system_number * random_delta_number):
            line = result_log.read_line().split(',')
            results.append((int(line[0]), int(line[1]), float(line[2]) / task_number))
    
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
            pre_results[jobs_number] = {delta: [time]}
    
    for jobs_number in pre_results:
        result_dict[jobs_number] = []
        for delta in pre_results[jobs_number]:
            result_dict[jobs_number].append((delta, sum(pre_results[jobs_number][delta]) / len(pre_results[jobs_number][delta])))
    
    return result_dict


def generate_knapsack_performance(title: str, resultsv1: dict[int, list[tuple[int, float]]], resultsv2: dict[int, list[tuple[int, float]]]) -> None:
    jobs_numbers = list(set(resultsv1.keys()) | set(resultsv2.keys()))
    jobs_numbers.sort()
    nb_lines = ceil(len(jobs_numbers) / 3)
    _, axs = plt.subplots(nb_lines, 3, figsize=(30, 5 * nb_lines))
    
    for index in range(0, len(jobs_numbers)):
        job_number = jobs_numbers[index]
        plotx = floor(index / 3)
        ploty = index % 3
        axs[plotx, ploty].set_title(f'Job number: {job_number:d}')
        
        # Only try to plot when job number is in the dict!
        if job_number in resultsv1:
            x1 = []
            y1 = []
            for delta, time in resultsv1[job_number]:
                x1.append(delta)
                y1.append(time)
            axs[plotx, ploty].plot(x1, y1, 'o', label='classic DP')
        
        if job_number in resultsv2:
            x2 = []
            y2 = []
            for delta, time in resultsv2[job_number]:
                x2.append(delta)
                y2.append(time)
            axs[plotx, ploty].plot(x2, y2, 'o', color='tab:orange', label='improved DP')
        
        axs[plotx, ploty].legend(loc="upper left")
        
    
    plt.subplots_adjust(bottom=0.1, 
                        top=0.9, 
                        wspace=0.4, 
                        hspace=0.5)
    plt.savefig(results_directory + title + '.png')


def generate() -> None:
    if assert_existing_result_files('knapsack_perf_evaluation.log', 'knapsackv2_perf_evaluation.log'):
        # Extract data from classical knapsack
        knapsack_log = log_file_class()
        knapsack_results = knapsack_log.create_result_file('knapsack_perf_evaluation.log')
        knapsack_data = analyse_data(knapsack_results)
        knapsack_results.close()
        knapsackv1_data = create_dict_t2d(knapsack_data)
        
        # Extract data from improved knapsack
        knapsackv2_log = log_file_class()
        knapsackv2_results = knapsackv2_log.create_result_file('knapsackv2_perf_evaluation.log')
        knapsack_data = analyse_data(knapsackv2_results)
        knapsackv2_results.close()
        knapsackv2_data = create_dict_t2d(knapsack_data)
        
        # Generate graph
        generate_knapsack_performance('knapsack_perf_evaluation', knapsackv1_data, knapsackv2_data)
        
        
if __name__ == '__main__':
    exit(1)