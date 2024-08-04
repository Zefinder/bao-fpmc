# Imports
import matplotlib.pyplot as plt
from math import ceil, floor
import numpy as np
from prem_utils import *
from fixed_priority_sched import *


# Functions
# Get the blocking time of a task with lower prio on the same CPU
def get_blocking_time(Px: processor, prio: int) -> int:
    # Remember that it is descending prio
    return min([ltask.e for ltask in Px.lower_tasks(prio)])


# Get the intra-processor interference time of a task with higher prio on the same CPU
# Also called I
def get_intra_processor_interference(Px: processor, delta: int, prio: int) -> int:
    # Remember that it is descending prio
    return sum([ceil(delta / htask.T) * htask.e for htask in Px.higher_tasks(prio)])


# Get the inter-processor interference, the paper version.
# Takes the number of time a task can start (considering jitter) and multiply by its memory time
# Also called alpha
def get_inter_processor_interference(system: PREM_system, cpu_prio: int, delta: int) -> int:
    interference = 0
    for Px in system.higher_processors(cpu_prio):
        for task in Px.tasks():
            interference += ceil((delta + task.R - task.e) / task.T) * task.M
            
    return interference


# Get the number of memory phases possible in delta
# Also called N
def get_number_memory_phase(Px: processor, task: PREM_task, delta: int) -> int:
    return sum([ceil(delta / htask.T) for htask in Px.higher_tasks(task.prio)]) + floor(delta / task.T) + (1 if Px.is_lowest_prio(task.prio) else 0)
    

# Get the max interference possible
# Also called epsilon
def get_max_interference(system: PREM_system, cpu_prio: int, Px: processor) -> int:
    # This is a value that doesn't change, so saved in the processor if already computed
    if Px.max_interference != -1:
        return Px.max_interference

    # Else we have eps = alpha(eps + M_max)
    # The base value of the recurrent equation is the greatest memory phase
    max_interference = Px.M_max
    prev_max_interference = -1
    while prev_max_interference != max_interference:
        prev_max_interference = max_interference
        max_interference = get_inter_processor_interference(system=system, cpu_prio=cpu_prio, delta=max_interference)
    
    # Save the value 
    Px.max_interference = max_interference
    return max_interference


# Get the total memory interference in an interval delta
# Also called beta
def get_total_memory_interference(system: PREM_system, cpu_prio: int, Px: processor, task: PREM_task, delta: int) -> int:
    return get_number_memory_phase(Px=Px, task=task, delta=delta) * get_max_interference(system=system, cpu_prio=cpu_prio, Px=Px)


# Get the memory phase start time for the k-th instance 
def get_memory_phase_start_time(system: PREM_system, cpu_prio: int, Px: processor, task: PREM_task, delta: int, k: int):
    #
    pass


tau_1 = PREM_task(2, 1, 24)
tau_2 = PREM_task(4, 6, 40)
tau_3 = PREM_task(14, 10, 50)
tau_4 = PREM_task(2, 6, 10)

P0 = processor([tau_1, tau_2, tau_3])
P1 = processor([tau_4])

system = PREM_system([P0, P1])

rate_monotonic_scheduler(Px=P0)
rate_monotonic_scheduler(Px=P1)

print(system)

