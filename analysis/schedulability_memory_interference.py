# Imports 
import time
from utils.generate_prem import interval, generate_prem_system
from utils.fixed_priority_sched import set_system_priority, rate_monotonic_scheduler
from utils.rta_prem import get_response_time_system
from utils.prem_inter_processor_interference import *
from utils.log_utils import *

# Constants
system_number = 550
cpu_number = 4
task_number_per_cpu = 4
period_interval = interval(10, 100)
period_distribution = 'logunif'
bandwidth_utilisation_intervals = [interval(0, 5), interval(5, 20), interval(20, 40), interval(40, 65)]
utilisations = [round(0.90 + 0.05 * i, 2) for i in range(1, 3)]

interference_mode_classic = inter_processor_interference_mode(get_classic_inter_processor_interference)
interference_mode_knapsack = inter_processor_interference_mode(get_knapsack_inter_processor_interference)

log_classic_filename = 'schedulability_memory_evaluation_prem.log'
log_knapsack_filename = 'schedulability_memory_evaluation_knapsack.log'

knapsack_problem_accesses = 0
# Functions
def main():
    # Tests from Fixed-Priority Memory-Centric scheduler for COTS based multiprocessor (Gero Schwäricke) p. 18
    # Generate tests with period between 10 and 100 ms, log uniform, memory stal varies between 0, 0 to 0.05, 0.05 to 
    # 0.2, 0.2 to 0.4 and 0.4 to 0.65, scheduled with Rate Monotonic, 4 CPU and 4 tasks. Utilisation varies from 0.05 to 1
    # With a 0.05 step. We generate 550 tests per utilisation per memory bandwidth 
    
    log_classic_file = log_file_class()
    log_classic_file.create(log_classic_filename)
    
    log_knapsack_file = log_file_class()
    log_knapsack_file.create(log_knapsack_filename)
    
    # Generate systems
    start_time = time.time()
    for bandwidth_utilisation_interval in bandwidth_utilisation_intervals:
        print(f'Generating systems for memory stall={bandwidth_utilisation_interval.__str__():s}')
        for utilisation in utilisations:
            print(f'Generating systems for utilisation={utilisation:f}')
            # Generate and analyse system_number systems
            for system_index in range(0, system_number):
                prem_system = generate_prem_system(processor_number=cpu_number,
                                                   task_number=task_number_per_cpu, 
                                                   period_interval=period_interval,
                                                   period_distribution=period_distribution,
                                                   utilisation=utilisation, 
                                                   bandwidth_utilisation_interval=bandwidth_utilisation_interval)
                
                print(prem_system)
                            
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