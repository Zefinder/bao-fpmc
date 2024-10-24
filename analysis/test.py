# Imports 
# from os import system
import time
import multiprocessing
from multiprocessing.managers import ValueProxy
import copy
from multiprocessing.synchronize import Lock
from utils.generate_prem import interval, generate_prem_system
from utils.fixed_priority_sched import set_system_priority, rate_monotonic_scheduler
from utils.rta_prem import get_response_time_system
from utils.prem_inter_processor_interference import *
from utils.log_utils import *

interference_mode_classic = inter_processor_interference_mode(get_classic_inter_processor_interference, measure_time=True)
interference_mode_knapsack = inter_processor_interference_mode(get_knapsack_inter_processor_interference, measure_time=True)
interference_mode_knapsackv2 = inter_processor_interference_mode(get_knapsackv2_inter_processor_interference, measure_time=True)
interference_mode_knapsackv3 = inter_processor_interference_mode(get_knapsackv3_inter_processor_interference, measure_time=True)
interference_mode_greedy = inter_processor_interference_mode(get_greedy_knapsack_inter_processor_interference, measure_time=True)

system = PREM_system([processor([PREM_task(4, 5, 20), PREM_task(4, 5, 20)]), processor([PREM_task(4, 5, 16)]), processor([PREM_task(4, 5, 30)])])

set_system_priority(system, rate_monotonic_scheduler)
result = get_response_time_system(system, interference_mode_classic)
print('Classical PREM:', result)
print('Measured time:', interference_mode_classic.measured_time_dict)
print()

system.reset()
set_system_priority(system, rate_monotonic_scheduler)
result = get_response_time_system(system, interference_mode_knapsack)
print('Knapsack:', result)
print('Measured time:', interference_mode_knapsack.measured_time_dict)
print()

system.reset()
set_system_priority(system, rate_monotonic_scheduler)
result = get_response_time_system(system, interference_mode_knapsackv2)
print('Knapsackv2:', result)
print('Measured time:', interference_mode_knapsackv2.measured_time_dict)
print()

system.reset()
set_system_priority(system, rate_monotonic_scheduler)
result = get_response_time_system(system, interference_mode_knapsackv3)
print('Knapsackv3:', result)
print('Measured time:', interference_mode_knapsackv3.measured_time_dict)
print()

# system.reset()
# set_system_priority(system, rate_monotonic_scheduler)
# result = get_response_time_system(system, interference_mode_greedy)
# print('Greedy:', result)
# print('Measured time:', interference_mode_greedy.measured_time_dict)

