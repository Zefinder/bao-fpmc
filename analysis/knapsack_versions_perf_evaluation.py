import multiprocessing
from multiprocessing import Pool
from multiprocessing.managers import ValueProxy
from multiprocessing.synchronize import Lock
import random

from numpy import number
from utils.generate_prem import interval, generate_prem_system, rescale_system
from utils.fixed_priority_sched import set_system_priority, rate_monotonic_scheduler
from utils.rta_prem import get_response_time_system
from utils.prem_inter_processor_interference import *
from utils.log_utils import *

system_number = 10000
processor_number = 1
tasks_per_processor = [4, 8]
period_interval = interval(100, 1000)
period_distribution = 'logunif'
utilisation = 0.6
scale = lambda x: x
bandwidth_utilisation_interval = interval(5, 20)
min_cost = 20
random_delta_number = 5

interference_mode_knapsack = inter_processor_interference_mode(get_knapsack_inter_processor_interference, measure_time=True)
interference_mode_knapsackv2 = inter_processor_interference_mode(get_knapsackv2_inter_processor_interference, measure_time=True)

log_knapsack_filename = 'knapsack_perf_evaluation.log'
log_knapsackv2_filename = 'knapsackv2_perf_evaluation.log'


def compare_knapsack_perf(name: str, log_name: str, mode: inter_processor_interference_mode):
    system_analysed = 0
    
    # Create the log file
    log_file = log_file_class()
    log_file.create(log_name=log_name)
    
    for _ in range(0, system_number):
        for task_number in tasks_per_processor:
            # Create a system with one processor and analyse it
            system = generate_prem_system(processor_number=processor_number,
                                        task_number=task_number,
                                        period_interval=period_interval,
                                        period_distribution=period_distribution,
                                        utilisation=utilisation,
                                        bandwidth_utilisation_interval=bandwidth_utilisation_interval,
                                        scale=scale,
                                        min_cost=min_cost)
            set_system_priority(system=system, fp_scheduler=rate_monotonic_scheduler)
            get_response_time_system(system=system, interference_mode=mode)
            
            for _ in range(0, random_delta_number):
                # Generate a random delta between 100 and 2000 (because...)
                delta = random.randint(100, 2000)
                
                # Compute the number of items that will be put in the knapsack
                number_items = 0
                for htask in system.processors()[0].tasks():
                    number_items += ceil((delta + htask.R + htask.e) / htask.T)
                
                # Compute the interference
                mode.measured_time_dict = {}
                mode.get_inter_processor_interference(system=system,
                                                    cpu_prio=1,
                                                    delta=delta,
                                                    task=PREM_task(M=0, C=0, T=0))
                
                # Write the result
                log_file.write_system(system=system)
                log_file.write(f'{number_items:d}, {delta:d}, {mode.measured_time_dict[delta][0]:f}')
    
        system_analysed += 1
        if system_analysed % 100 == 0:
            print(f'({name:s}) Number of analysed systems: {system_analysed:d}')
            
    # Close log file
    log_file.close()
    

def main():
    # Create processes
    knapsack_process = multiprocessing.Process(target=compare_knapsack_perf, args=('knapsack', log_knapsack_filename, interference_mode_knapsack,))
    knapsackv2_process = multiprocessing.Process(target=compare_knapsack_perf, args=('knaspackv2', log_knapsackv2_filename, interference_mode_knapsackv2,))
    
    # Start!
    knapsack_process.start()
    knapsackv2_process.start()
    
    # And wait for both of them
    knapsack_process.join()
    knapsackv2_process.join()
    

if __name__ == '__main__':
    main()