# Imports 
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
from results.generator.generator_utils import *
from utils.log_utils import *
from utils.generate_prem import interval

# Constants
task_sets_per_utilisation = 50
# bandwidth_utilisation_intervals = [interval(0, 0), interval(0, 5), interval(5, 20), interval(20, 40), interval(40, 65)]
bandwidth_utilisation_intervals = [interval(0, 0)]
utilisations = [round(0.05 * i, 2) for i in range(1, 20)]
markers = ['-o', '-s', '-x', '-*', '-d']

# Functions
def generate_schedulability_utilisation_graph(results: log_results, method: str) -> None:
    # For every interval, there are len(utilisations) * 550 tasks
    utilisations_results = []
    for _ in bandwidth_utilisation_intervals:
        # Analyse schedulability of each processor, according to its bandwith memory utilisation
        memory_utilisation_results = []
        for _ in utilisations:
            schedulable_tasks_number = 0
            total_task_number = 0

            for _ in range(0, task_sets_per_utilisation):
                system_result = results.read_entry()
                
                # We get the number of schedulable tasks and the total number of tasks
                schedulable_tasks_number += system_result.get_number_schedulable_tasks()
                total_task_number += system_result.get_total_number_of_tasks()
        
            # Add ratio to the memory utilisation list
            memory_utilisation_results.append(schedulable_tasks_number / total_task_number)

        utilisations_results.append(memory_utilisation_results)

    # Prepare for drawing graph
    plt.figure(figsize=(12, 12))

    marker_index = 0
    for utilisation_results in utilisations_results:
        plt.plot(utilisations, utilisation_results, markers[marker_index])
        marker_index += 1
    
    plt.title('Task schedulability per utilisation for N=4 and 4 task per processor')
    plt.xticks(utilisations)  
    plt.xlabel('Utilisation')  
    plt.ylabel('Schedulable tasks')
    plt.ylim(bottom=-0.05, top=1.05)
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    plt.savefig(results_directory + f'task_schedulability_utilisation_{method:s}.png')


def generate() -> None:
    # Read classic log
    classic_log = log_file_class()
    classic_results = classic_log.create_result_file('schedulability_utilisation_evaluation_prem.log')

    # Read knapsack log
    knapsack_log = log_file_class()
    knapsack_results = knapsack_log.create_result_file('schedulability_utilisation_evaluation_knapsack.log')

    generate_schedulability_utilisation_graph(results=classic_results, method='classic')
    generate_schedulability_utilisation_graph(results=knapsack_results, method='knapsack')


if __name__ == '__main__':
    exit(1)