# Imports 
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
from results.generator.generator_utils import *
from utils.log_utils import *

# Constants
task_sets_per_cpu = 5000
processor_numbers = [4, 8, 16]
utilisation = 0.6


# Functions
def generate_schedulability_improvement_graph(classic_results: log_results, knapsack_results: log_results) -> None:
    # No contention based schedulability, so only N = 16 is important
    processor_number = 16

    # Read entries that are not 16
    for _ in range(0, task_sets_per_cpu * (len(processor_numbers) - 1)):
        classic_results.read_entry()
        knapsack_results.read_entry()

    # As long as we are under 15000 tests, we can continue
    # Analyse schedulability of each processor, according to its priority
    # Array of number of CPU for classic and knapsack, if schedulable +1 else +0
    # Analyse total schedulability
    classic_total_array = [0] * processor_number
    classic_schedulable_array = [0] * processor_number
    knapsack_total_array = [0] * processor_number
    knapsack_schedulable_array = [0] * processor_number
    
    for _ in range(0, task_sets_per_cpu):
        # Get system from classic and knapsack results
        classic_system_result = classic_results.read_entry()
        knapsack_system_result = knapsack_results.read_entry()

        classic_processors = classic_system_result.processors()
        for processor_index in range(0, processor_number):
            classic_total_array[processor_index] += 1
            if classic_processors[processor_index].is_schedulable():
                classic_schedulable_array[processor_index] += 1

        knapsack_processors = knapsack_system_result.processors()
        for processor_index in range(0, processor_number):
            knapsack_total_array[processor_index] += 1
            if knapsack_processors[processor_index].is_schedulable():
                knapsack_schedulable_array[processor_index] += 1

    # Make ratio between schedulable and total
    schedulability_results_system_classic = []
    schedulability_results_system_knapsack = []
    for processor_index in range(0, processor_number):
        schedulability_results_system_classic.append(classic_schedulable_array[processor_index] / classic_total_array[processor_index])
        schedulability_results_system_knapsack.append(knapsack_schedulable_array[processor_index] / knapsack_total_array[processor_index])
    
    # Prepare for drawing graph
    plt.figure(figsize=(12, 12))
    x = [*range(1, processor_number + 1)]
    plt.plot(x, schedulability_results_system_classic, '-x', label='Classic PREM analysis')
    plt.plot(x, schedulability_results_system_knapsack, '-o', label='Knapsack analysis')
    
    plt.title('Processor schedulability for N=16 and 8 tasks per processor')
    plt.xticks(x)  
    plt.xlabel('Processor priority')  
    plt.ylabel('Schedulable processors')
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    plt.legend()
    plt.savefig(results_directory + 'schedulability_per_priority.png')

    plt.figure(figsize=(12, 12))
    improved_schedulability = []
    for processor_index in range(0, processor_number):
        improved_schedulability.append((knapsack_schedulable_array[processor_index] / knapsack_total_array[processor_index]) - (classic_schedulable_array[processor_index] / classic_total_array[processor_index]))
    
    plt.plot(x, improved_schedulability, '-o')

    plt.title('Schedulability improvement per processor for N=16 and 8 tasks per processor')
    plt.xticks(x)  
    plt.xlabel('Processor priority')  
    plt.ylabel('Schedulability')
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    plt.savefig(results_directory + 'schedulability_improvement.png')


def generate() -> None:
    # Read classic log
    classic_log = log_file_class()
    classic_results = classic_log.create_result_file('schedulability_rta_evaluation_prem.log')

    # Read knapsack log
    knapsack_log = log_file_class()
    knapsack_results = knapsack_log.create_result_file('schedulability_rta_evaluation_knapsack.log')

    generate_schedulability_improvement_graph(classic_results=classic_results, knapsack_results=knapsack_results)


if __name__ == '__main__':
    exit(1)