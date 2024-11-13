# Imports 
import multiprocessing
from time import time
from multiprocessing import Pool
from multiprocessing.managers import ValueProxy
from multiprocessing.synchronize import Lock
from utils.generate_prem import interval, generate_prem_system, rescale_system
from utils.fixed_priority_sched import set_system_priority, rate_monotonic_scheduler
from fpmc_sched.rta import get_response_time_system
from fpmc_sched.prem_inter_processor_interference import *
from utils.log_utils import *
import copy

# Constants
system_number = 100 # Per CPU number
cpu_numbers = [4, 8, 16]
task_number_per_cpu = 8
period_interval = interval(10, 100)
period_distribution = 'logunif'
bandwidth_utilisation_interval = interval(5, 20)
utilisation = 0.6
prem_process_number = 2
knapsack_process_number = 14
greedy_knapsack_process_number = 4
minimum_cost = floor(100 / (1 - (bandwidth_utilisation_interval.max / 100)))

interference_mode_classic = inter_processor_interference_mode(get_classic_inter_processor_interference)
interference_mode_knapsack = inter_processor_interference_mode(get_classic_inter_processor_interference, get_knapsack_inter_processor_interference)
interference_mode_greedy_knapsack = inter_processor_interference_mode(get_classic_inter_processor_interference, get_greedy_knapsack_inter_processor_interference)

log_classic_filename = 'schedulability_rta_evaluation_prem.log'
log_knapsack_filename = 'schedulability_rta_evaluation_knapsack.log'
log_greedy_knapsack_filename = 'schedulability_rta_evaluation_greedy_knapsack.log'

# Store all systems in a variable (Ugly but it works...)
prem_systems: list[PREM_system] = []

# Functions
def scale1000(time: int) -> int:
    return time * 1000


def factor100(time: int) -> int:
    return floor(time // 100)


def prem_init_thread(log_classic_filename_local: str,
                     system_index_local: ValueProxy[int],
                     prem_system_lock_local: Lock):
    global prem_system_lock
    prem_system_lock = prem_system_lock_local

    global log_classic_file
    log_classic_file = log_file_class()
    log_classic_file.resume_log(log_classic_filename_local)
    
    global classic_system_index
    classic_system_index = system_index_local


def knapsack_init_thread(log_knapsack_filename_local: str,
                         system_index_local: ValueProxy[int],
                         knapsack_system_lock_local: Lock):
    global knapsack_system_lock
    knapsack_system_lock = knapsack_system_lock_local
    
    global log_knapsack_file
    log_knapsack_file = log_file_class()
    log_knapsack_file.resume_log(log_knapsack_filename_local)
    
    global knapsack_system_index
    knapsack_system_index = system_index_local
    

def greedy_init_thread(log_greedy_knapsack_filename_local: str,
                       system_index_local: ValueProxy[int],
                       greedy_system_lock_local: Lock):
    global greedy_system_lock
    greedy_system_lock = greedy_system_lock_local
    
    global log_greedy_knapsack_file
    log_greedy_knapsack_file = log_file_class()
    log_greedy_knapsack_file.resume_log(log_greedy_knapsack_filename_local)
    
    global greedy_system_index
    greedy_system_index = system_index_local


def prem_system_analysis(_):
    # Read system from array
    with prem_system_lock:
        print('Classic:', classic_system_index.get())
        prem_system_classic = copy.deepcopy(prem_systems[classic_system_index.get()])
        classic_system_index.set(classic_system_index.get() + 1)
        
    # Analyse system classic
    set_system_priority(system=prem_system_classic, fp_scheduler=rate_monotonic_scheduler)
    get_response_time_system(system=prem_system_classic, interference_mode=interference_mode_classic)

    # Write in logs (thread-safe)
    log_classic_file.write_system(system=prem_system_classic)
    
def knapsack_system_analysis(_):
    # Read system from file (locking since threads)
    with knapsack_system_lock:
        prem_system_knapsack = copy.deepcopy(prem_systems[knapsack_system_index.get()])
        knapsack_system_index.set(knapsack_system_index.get() + 1)

    # Analyse system classic
    rescale_system(system=prem_system_knapsack, factor=factor100)
    set_system_priority(system=prem_system_knapsack, fp_scheduler=rate_monotonic_scheduler)
    get_response_time_system(system=prem_system_knapsack, interference_mode=interference_mode_knapsack)

    # Write in logs (thread-safe)
    log_knapsack_file.write_system(system=prem_system_knapsack)
    
    
def greedy_system_analysis(_):
    # Read system from file (locking since threads)
    with greedy_system_lock:
        print('Greedy:', greedy_system_index.get())
        greedy_system_knapsack = copy.deepcopy(prem_systems[greedy_system_index.get()])
        greedy_system_index.set(greedy_system_index.get() + 1)

    # Analyse system classic
    set_system_priority(system=greedy_system_knapsack, fp_scheduler=rate_monotonic_scheduler)
    get_response_time_system(system=greedy_system_knapsack, interference_mode=interference_mode_greedy_knapsack)

    # Write in logs (thread-safe)
    log_greedy_knapsack_file.write_system(system=greedy_system_knapsack)


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

    log_greedy_knapsack_file = log_file_class()
    log_greedy_knapsack_file.create(log_greedy_knapsack_filename)
    log_greedy_knapsack_file.close()

    # Generate ALL systems
    for cpu_number in cpu_numbers:
        for _ in range(0, system_number):
            system = generate_prem_system(processor_number=cpu_number,
                                          task_number=task_number_per_cpu, 
                                          period_interval=period_interval,
                                          period_distribution=period_distribution,
                                          utilisation=utilisation, 
                                          bandwidth_utilisation_interval=bandwidth_utilisation_interval,
                                          scale=scale1000,
                                          min_cost=minimum_cost)
            prem_systems.append(system)
    
    # Start pools
    start_time = time()
    
    manager = multiprocessing.Manager()
    # Start PREM pool
    prem_system_lock = multiprocessing.Lock()
    classic_system_index = manager.Value('i', 0)
    with Pool(processes=prem_process_number, initializer=prem_init_thread, initargs=(log_classic_filename, classic_system_index, prem_system_lock,)) as pool:
        pool.map(prem_system_analysis, [*range(0, len(cpu_numbers) * system_number)])
        # pool.close()
        # pool.join()
        
    # # Start knapsack pool        
    # knapsack_system_lock = multiprocessing.Lock()
    # knapsack_system_index = manager.Value('i', 0)
    # with Pool(processes=knapsack_process_number, initializer=knapsack_init_thread, initargs=(log_knapsack_filename, knapsack_system_index, knapsack_system_lock,)) as pool:
    #     pool.map(knapsack_system_analysis, [*range(0, len(cpu_numbers) * system_number)])
    #     pool.close()
    #     pool.join()
        
    # Start greedy pool        
    greedy_system_lock = multiprocessing.Lock()
    greedy_system_index = manager.Value('i', 0)
    with Pool(processes=greedy_knapsack_process_number, initializer=greedy_init_thread, initargs=(log_greedy_knapsack_filename, greedy_system_index, greedy_system_lock,)) as pool:
        pool.map(greedy_system_analysis, [*range(0, len(cpu_numbers) * system_number)])
        # pool.close()
        # pool.join()
        
    execution_time = time() - start_time
    print("--- {:.04f} seconds ({:.04f} minutes) ---".format(execution_time, execution_time / 60))
    

if __name__ == '__main__':
    main()
