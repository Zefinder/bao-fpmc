from math import ceil, floor
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from results.generator.generator_utils import *
from utils.log_utils import *


# Constants
system_number = 10000
processor_number = 1
tasks_per_processor = [4, 6, 8, 10, 12]
random_delta_number = 5

knapsack_file = 'greedy_perf_evaluation/knapsack_perf_evaluation.log'
greedy_file = 'greedy_perf_evaluation/greedy_perf_evaluation.log'
greedyv2_file = 'greedy_perf_evaluation/greedyv2_perf_evaluation.log'


# Functions
def analyse_data(result_log: log_results) -> list[tuple[int, int, int]]:
    results: list[tuple[int, int, int]] = []
    
    for task_number in tasks_per_processor:
        for _ in range(0, system_number * random_delta_number):
            line = result_log.read_line().split(',')
            results.append((int(line[0]), int(line[1]), int(line[2])))
    
    return results


def create_dict_t2d(results: list[tuple[int, int, int]]) -> dict[int, dict[int, list[int]]]: # Task number to delta
    result_dict: dict[int, dict[int, list[int]]] = {}
    
    for result in results:
        jobs_number = result[0]
        delta = result[1]
        result = result[2]
        
        if jobs_number in result_dict:
            if delta in result_dict[jobs_number]:
                result_dict[jobs_number][delta].append(result)
            else:
                result_dict[jobs_number][delta] = [result]
        else:
            result_dict[jobs_number] = {delta: [result]}
    
    return result_dict


def generate_knapsack_performance(title: str, base_results: dict[int, dict[int, list[int]]], resultsv1: dict[int, dict[int, list[int]]], resultsv2: dict[int, dict[int, list[int]]]) -> None:
    jobs_numbers = list(set(resultsv1.keys()) | set(resultsv2.keys()))
    jobs_numbers.sort()
    nb_lines = ceil(len(jobs_numbers) / 3)
    _, axs = plt.subplots(nb_lines, 3, figsize=(30, 5 * nb_lines))
    
    for index in range(0, len(jobs_numbers)):
        job_number = jobs_numbers[index]
        plotx = floor(index / 3)
        ploty = index % 3
        axs[plotx, ploty].set_title(f'Job number: {job_number:d}')
        
        # Compute the accuracy of the result for both greedy
        base = base_results[job_number]
        greedy = resultsv1[job_number]
        greedyv2 = resultsv2[job_number]
        x1 = []
        y1 = []
        x2 = []
        y2 = []
        for delta in base.keys():
            greedy_percentage = 0
            greedyv2_percentage = 0
            for result_index in range(0, len(base[delta])):
                greedy_percentage += (abs(base[delta][result_index] - greedy[delta][result_index])) / ((base[delta][result_index] + greedy[delta][result_index]) / 2)
                greedyv2_percentage += (abs(base[delta][result_index] - greedyv2[delta][result_index])) / ((base[delta][result_index] + greedyv2[delta][result_index]) / 2)
                
            greedy_percentage /= len(base[delta])
            greedyv2_percentage /= len(base[delta])

            x1.append(delta)
            y1.append(greedy_percentage)
            x2.append(delta)
            y2.append(greedyv2_percentage)
        
        axs[plotx, ploty].plot(x1, y1, 'o', label='Greedy knapsack v1')
        axs[plotx, ploty].plot(x2, y2, 'o', color='tab:orange', label='Greedy knapsack v2')
        axs[plotx, ploty].set_xlabel('Interval size')
        axs[plotx, ploty].set_ylabel('Percentage difference with\nexact resolution')
        axs[plotx, ploty].legend(loc="upper left")
        axs[plotx, ploty].yaxis.set_major_formatter(mtick.PercentFormatter(1.00))
        
    
    plt.subplots_adjust(bottom=0.1, 
                        top=0.9, 
                        wspace=0.4, 
                        hspace=0.5)
    plt.savefig(results_directory + title + '.png')


def generate() -> None:
    if assert_existing_result_files(knapsack_file, greedy_file, greedyv2_file):
        # Extract data from classical knapsack
        knapsack_log = log_file_class()
        knapsack_results = knapsack_log.create_result_file(knapsack_file)
        knapsack_data = analyse_data(knapsack_results)
        knapsack_results.close()
        knapsackv1_data = create_dict_t2d(knapsack_data)
        
        # Extract data from both greedy
        greedy_log = log_file_class()
        greedy_results = greedy_log.create_result_file(greedy_file)
        knapsack_data = analyse_data(greedy_results)
        knapsack_results.close()
        greedyv1_data = create_dict_t2d(knapsack_data)
        
        greedyv2_log = log_file_class()
        greedyv2_results = greedyv2_log.create_result_file(greedyv2_file)
        knapsack_data = analyse_data(greedyv2_results)
        knapsack_results.close()
        greedyv2_data = create_dict_t2d(knapsack_data)
        
        # Generate graph
        generate_knapsack_performance('greedy_perf_evaluation', knapsackv1_data, greedyv1_data, greedyv2_data)
        
        
if __name__ == '__main__':
    exit(1)