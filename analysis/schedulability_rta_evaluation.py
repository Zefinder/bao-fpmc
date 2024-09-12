# Imports 
import time
import multiprocessing
from multiprocessing import Pool
from multiprocessing.managers import ValueProxy
from multiprocessing.synchronize import Lock
from utils.generate_prem import interval, generate_prem_system
from utils.fixed_priority_sched import set_system_priority, rate_monotonic_scheduler
from utils.rta_prem import get_response_time_system
from utils.prem_inter_processor_interference import *
from utils.log_utils import *
import copy

# Constants
system_number = 5000
cpu_numbers = [4, 8, 16]
task_number_per_cpu = 8
period_interval = interval(10, 100)
period_distribution = 'logunif'
bandwidth_utilisation_interval = interval(5, 20)
utilisation = 0.6
process_number = 16

interference_mode_classic = inter_processor_interference_mode(get_classic_inter_processor_interference)
interference_mode_knapsack = inter_processor_interference_mode(get_knapsack_inter_processor_interference, interference_max_computation=200)

log_classic_filename = 'schedulability_rta_evaluation_prem.log'
log_knapsack_filename = 'schedulability_rta_evaluation_knapsack.log'

# Functions
def init_thread(system_index_value_local: ValueProxy,
                cpu_number_local: int,
                log_classic_filename_local: str,
                log_knapsack_filename_local: str,
                creation_lock_local: Lock,
                log_lock_local: Lock):
    global creation_lock
    creation_lock = creation_lock_local

    global log_lock
    log_lock = log_lock_local

    global cpu_number
    cpu_number = cpu_number_local

    global log_classic_file
    log_classic_file = log_file_class()
    log_classic_file.resume_log(log_classic_filename_local)

    global log_knapsack_file
    log_knapsack_file = log_file_class()
    log_knapsack_file.resume_log(log_knapsack_filename_local)

    global system_index_value
    system_index_value = system_index_value_local


def system_analysis(_):
    global system_index_value
    # Generate system (uses a file so locking)

    creation_lock.acquire()
    prem_system_classic = generate_prem_system(processor_number=cpu_number,
                                               task_number=task_number_per_cpu, 
                                               period_interval=period_interval,
                                               period_distribution=period_distribution,
                                               utilisation=utilisation, 
                                               bandwidth_utilisation_interval=bandwidth_utilisation_interval)
    prem_system_knapsack = copy.deepcopy(prem_system_classic)
    creation_lock.release()

    # Analyse system classic
    set_system_priority(system=prem_system_classic, fp_scheduler=rate_monotonic_scheduler)
    get_response_time_system(system=prem_system_classic, interference_mode=interference_mode_classic)
    
    # Analyse system with knapsack
    set_system_priority(system=prem_system_knapsack, fp_scheduler=rate_monotonic_scheduler)
    get_response_time_system(system=prem_system_knapsack, interference_mode=interference_mode_knapsack)

    # Write in logs
    log_lock.acquire()
    log_classic_file.write(system=prem_system_classic)
    log_knapsack_file.write(system=prem_system_knapsack)
    
    # Just an indicator to help to know where we are in generation
    system_index_value.value += 1
    if system_index_value.value % 100 == 0:
        print(f'Number of generated and analysed systems: {system_index_value.value:d}')
    log_lock.release()    


def main():
    # Tests from Fixed-Priority Memory-Centric scheduler for COTS based multiprocessor (Gero Schwäricke) p. 17 
    # Generate tests with period between 10 and 100 ms, log uniform, memory stal between 0.05 and 0.20, scheduled with
    # Rate Monotonic. We change the number of generated tasksets, here we generate 5000 tasksets with utilisation 0.6, 
    # and 4, 8, 16 processors. There are 8 tasks per processor.

    # Reset log files
    log_classic_file = log_file_class()
    log_classic_file.create(log_classic_filename)
    log_classic_file.close()

    log_knapsack_file = log_file_class()
    log_knapsack_file.create(log_knapsack_filename)
    log_knapsack_file.close()

    # Generate systems
    start_time = time.time()
    for cpu_number in cpu_numbers:
        print(f'Generating systems for N={cpu_number:d}')
        
        creation_lock = multiprocessing.Lock()
        log_lock = multiprocessing.Lock()
        manager = multiprocessing.Manager()
        system_index_value = manager.Value('system_index', 0)
        with Pool(processes=process_number, initializer=init_thread, initargs=(system_index_value, cpu_number, log_classic_filename, log_knapsack_filename, creation_lock, log_lock,)) as pool:
            pool.map(system_analysis, [*range(1, system_number + 1)])
            pool.close()
            pool.join()

        print()
        
    execution_time = time.time() - start_time
    print("--- {:.04f} seconds ({:.04f} minutes) ---".format(execution_time, execution_time / 60))


if __name__ == '__main__':
    main()
