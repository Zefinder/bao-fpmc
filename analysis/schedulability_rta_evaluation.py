# Imports 
import time
import multiprocessing
from utils.generate_prem import interval, generate_prem_system
from utils.fixed_priority_sched import set_system_priority, rate_monotonic_scheduler
from utils.rta_prem import get_response_time_system
from utils.prem_inter_processor_interference import *
from utils.log_utils import *

# Constants
system_number = 5000
cpu_numbers = [4, 8, 16]
task_number_per_cpu = 8
period_interval = interval(10, 100)
period_distribution = 'logunif'
bandwidth_utilisation_interval = interval(5, 20)
utilisation = 0.6
process_number = 8

interference_mode_classic = inter_processor_interference_mode(get_classic_inter_processor_interference)
interference_mode_knapsack = inter_processor_interference_mode(get_knapsack_inter_processor_interference)

log_classic_filename = 'schedulability_rta_evaluation_prem.log'
log_knapsack_filename = 'schedulability_rta_evaluation_knapsack.log'

knapsack_problem_accesses = 0

# Functions
def init_thread(creation_lock_local, log_lock_local):
    global creation_lock
    creation_lock = creation_lock_local

    global log_lock
    log_lock = log_lock_local


def system_analysis():
    pass


def main():
    # Tests from Fixed-Priority Memory-Centric scheduler for COTS based multiprocessor (Gero Schwäricke) p. 17 
    # Generate tests with period between 10 and 100 ms, log uniform, memory stal between 0.05 and 0.20, scheduled with
    # Rate Monotonic. We change the number of generated tasksets, here we generate 5000 tasksets with utilisation 0.6, 
    # and 4, 8, 16 processors. There are 8 tasks per processor.
    
    log_classic_file = log_file_class()
    log_classic_file.create(log_classic_filename)
    
    log_knapsack_file = log_file_class()
    log_knapsack_file.create(log_knapsack_filename)
    
    # Generate systems
    start_time = time.time()
    for cpu_number in cpu_numbers:
        print(f'Generating systems for N={cpu_number:d}')
        
        with Pool(processes=process_number) as pool:
            pass

        # Generate and analyse system_number systems
        for system_index in range(0, system_number):
            prem_system = generate_prem_system(processor_number=cpu_number,
                                               task_number=task_number_per_cpu, 
                                               period_interval=period_interval,
                                               period_distribution=period_distribution,
                                               utilisation=utilisation, 
                                               bandwidth_utilisation_interval=bandwidth_utilisation_interval)
            
            # Analyse system classic
            set_system_priority(system=prem_system, fp_scheduler=rate_monotonic_scheduler)
            get_response_time_system(system=prem_system, interference_mode=interference_mode_classic)
            log_classic_file.write(system=prem_system)
            
            # Analyse system with knapsack (but first reset system)
            prem_system.reset()
            set_system_priority(system=prem_system, fp_scheduler=rate_monotonic_scheduler)
            get_response_time_system(system=prem_system, interference_mode=interference_mode_knapsack)
            log_knapsack_file.write(system=prem_system)
            
            # Just an indicator to help to know where we are in generation
            if (system_index + 1) % 100 == 0:
                print(f'Number of generated and analysed systems: {system_index + 1:d}')
            
        print()
        
    execution_time = time.time() - start_time
    print("--- {:.04f} seconds ({:.04f} minutes) ---".format(execution_time, execution_time / 60))


if __name__ == '__main__':
    main()