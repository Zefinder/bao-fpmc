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

interference_mode_classic = inter_processor_interference_mode(get_classic_inter_processor_interference)

system = PREM_system([processor([PREM_task(4, 5, 20), PREM_task(4, 5, 20)]), processor([PREM_task(4, 5, 16)])])
set_system_priority(system, rate_monotonic_scheduler)
result = get_response_time_system(system, interference_mode_classic)

print(result)