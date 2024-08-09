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
    P0 = processor([PREM_task(1, 49, 500), PREM_task(2, 27, 800), PREM_task(5, 100, 400), PREM_task(6, 105, 200)])
    P1 = processor([PREM_task(2, 34, 500), PREM_task(5, 87, 600), PREM_task(0, 105, 200), PREM_task(3, 78, 400)])
    P2 = processor([PREM_task(2, 37, 200), PREM_task(1, 13, 100), PREM_task(2, 144, 1000), PREM_task(2, 190, 400)])
    P3 = processor([PREM_task(1, 19, 400), PREM_task(0, 273, 600), PREM_task(2, 43, 200), PREM_task(5, 86, 400)])
    system = PREM_system(processors=[P0, P1, P2, P3], utilisation=0.95)
    set_system_priority(system=system, fp_scheduler=rate_monotonic_scheduler)
    get_response_time_system(system=system, interference_mode=interference_mode_knapsack)

if __name__ == '__main__':
    main()