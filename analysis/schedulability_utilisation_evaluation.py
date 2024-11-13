# Imports 
import time
import multiprocessing
from multiprocessing import Pool
from multiprocessing.managers import ValueProxy
from multiprocessing.synchronize import Lock
from utils.generate_prem import interval, generate_prem_system, rescale_system
from utils.fixed_priority_sched import set_system_priority, rate_monotonic_scheduler
from fpmc_sched.rta_prem import get_response_time_system
from fpmc_sched.prem_inter_processor_interference import *
from utils.log_utils import *
import copy

# Constants
system_number = 550
cpu_number = 4
task_number_per_cpu = 4
period_interval = interval(10, 100)
period_distribution = 'logunif'
bandwidth_utilisation_intervals = [interval(0, 0), interval(0, 5), interval(5, 20), interval(20, 40), interval(40, 65)]
utilisations = [round(0.05 * i, 2) for i in range(1, 20)]
process_number = 16

interference_mode_classic = inter_processor_interference_mode(get_classic_inter_processor_interference)
interference_mode_knapsack = inter_processor_interference_mode(get_classic_inter_processor_interference, get_knapsack_inter_processor_interference)
interference_mode_greedy_knapsack = inter_processor_interference_mode(get_classic_inter_processor_interference, get_greedy_knapsack_inter_processor_interference)

log_classic_filename = 'schedulability_utilisation_evaluation_prem.log'
log_knapsack_filename = 'schedulability_utilisation_evaluation_knapsack.log'
log_greedy_knapsack_filename = 'schedulability_utilisation_evaluation_greedy_knapsack.log'

# Functions
def init_thread(system_index_value_local: ValueProxy,
                cpu_number_local: int,
                utilisation_local: float,
                bandwidth_utilisation_interval_local: interval,
                log_classic_filename_local: str,
                log_knapsack_filename_local: str,
                log_greedy_knapsack_filename_local: str,
                creation_lock_local: Lock,
                log_lock_local: Lock):
    global creation_lock
    creation_lock = creation_lock_local

    global log_lock
    log_lock = log_lock_local

    global cpu_number
    cpu_number = cpu_number_local

    global utilisation
    utilisation = utilisation_local

    global bandwidth_utilisation_interval
    bandwidth_utilisation_interval = bandwidth_utilisation_interval_local    

    global log_classic_file
    log_classic_file = log_file_class()
    log_classic_file.resume_log(log_classic_filename_local)

    global log_knapsack_file
    log_knapsack_file = log_file_class()
    log_knapsack_file.resume_log(log_knapsack_filename_local)

    global log_greedy_knapsack_file
    log_greedy_knapsack_file = log_file_class()
    log_greedy_knapsack_file.resume_log(log_greedy_knapsack_filename_local)

    global system_index_value
    system_index_value = system_index_value_local


def scale1000(time: int) -> int:
    return time * 1000


def factor10(time: int) -> int:
    return floor(time / 10)


def factor100(time: int) -> int:
    return floor(time // 100)


def system_analysis(_):
    global system_index_value
    # Generate system (uses a file so locking)

    minimum_cost = floor(100 / (1 - (bandwidth_utilisation_interval.max / 100)))

    creation_lock.acquire()
    prem_system_classic = generate_prem_system(processor_number=cpu_number,
                                               task_number=task_number_per_cpu, 
                                               period_interval=period_interval,
                                               period_distribution=period_distribution,
                                               utilisation=utilisation, 
                                               bandwidth_utilisation_interval=bandwidth_utilisation_interval,
                                               scale=scale1000,
                                               min_cost=minimum_cost)
    prem_system_knapsack = copy.deepcopy(prem_system_classic)
    prem_system_greedy_knapsack = copy.deepcopy(prem_system_classic)
    creation_lock.release()

    # Analyse system classic
    set_system_priority(system=prem_system_classic, fp_scheduler=rate_monotonic_scheduler)
    get_response_time_system(system=prem_system_classic, interference_mode=interference_mode_classic)
    
    # Analyse system with knapsack (rescale so calculations are not too long)
    set_system_priority(system=prem_system_knapsack, fp_scheduler=rate_monotonic_scheduler)
    factor = factor10 if utilisation < 0.3 else factor100
    rescale_system(system=prem_system_knapsack, factor=factor)        
    get_response_time_system(system=prem_system_knapsack, interference_mode=interference_mode_knapsack)

    # Analyse system with greedy knapsack
    set_system_priority(system=prem_system_greedy_knapsack, fp_scheduler=rate_monotonic_scheduler)
    get_response_time_system(system=prem_system_greedy_knapsack, interference_mode=interference_mode_greedy_knapsack)

    # Write in logs
    log_lock.acquire()
    log_classic_file.write_system(system=prem_system_classic)
    log_knapsack_file.write_system(system=prem_system_knapsack)
    log_greedy_knapsack_file.write_system(system=prem_system_greedy_knapsack)

    # Just an indicator to help to know where we are in generation
    system_index_value.value += 1
    if system_index_value.value % 100 == 0:
        print(f'Number of generated and analysed systems: {system_index_value.value:d}')
    log_lock.release()    


def main():
    # Tests from Fixed-Priority Memory-Centric scheduler for COTS based multiprocessor (Gero Schwäricke) p. 18
    # Generate tests with period between 10 and 100 ms, log uniform, memory stal varies, (0, 0), (0, 0.05), etc...
    # , scheduled with Rate Monotonic. We change the number of generated tasksets, here we generate 550 tasksets
    # with utilisation from 0.05 to 1 with a 0.05 step and 4 processors. There are 4 tasks per processor.

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

    # Generate systems
    start_time = time.time()
    for bandwidth_utilisation_interval in bandwidth_utilisation_intervals:
        print(f'Generating systems for memory stall={bandwidth_utilisation_interval.__str__():s}')
        for utilisation in utilisations:
            print(f'Generating systems for utilisation={utilisation:f}')
            creation_lock = multiprocessing.Lock()
            log_lock = multiprocessing.Lock()
            manager = multiprocessing.Manager()
            system_index_value = manager.Value('system_index', 0)
            with Pool(processes=process_number, initializer=init_thread, initargs=(system_index_value, cpu_number, utilisation, bandwidth_utilisation_interval, log_classic_filename, log_knapsack_filename, log_greedy_knapsack_filename, creation_lock, log_lock,)) as pool:
                pool.map(system_analysis, [*range(1, system_number + 1)])
                pool.close()
                pool.join()

        print()
        
    execution_time = time.time() - start_time
    print("--- {:.04f} seconds ({:.04f} minutes) ---".format(execution_time, execution_time / 60))


if __name__ == '__main__':
    main()