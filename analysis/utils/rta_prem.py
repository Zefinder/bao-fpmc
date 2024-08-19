# Imports
import matplotlib.pyplot as plt
from math import ceil, floor
import numpy as np
from typing import Callable
from utils.prem_utils import *
from utils.fixed_priority_sched import *
from utils.prem_inter_processor_interference import inter_processor_interference_mode, get_classic_inter_processor_interference

# Functions
# ----------------------------------------------------
# -------------- Intermediate functions --------------
# ----------------------------------------------------
# Get the blocking time of a task with lower prio on the same CPU
def get_blocking_time(Px: processor, prio: int) -> int:
    lower_priority_executions = [ltask.e for ltask in Px.lower_tasks(prio)]
    return min(lower_priority_executions) if lower_priority_executions else 0


# Get the intra-processor interference time of a task with higher prio on the same CPU
# Also called I
def get_intra_processor_interference(Px: processor, delta: int, prio: int) -> int:    
    higher_priority_interference = [ceil(delta / htask.T) * htask.e for htask in Px.higher_tasks(prio)]
    return sum(higher_priority_interference) if higher_priority_interference else 0


# Get the number of memory phases possible in delta
# Also called N
def get_number_memory_phase(Px: processor, task: PREM_task, delta: int) -> int:
    return sum([ceil(delta / htask.T) for htask in Px.higher_tasks(task.prio)]) + floor(delta / task.T) + (1 if Px.is_lowest_prio(task.prio) else 0)
    

# Get the max interference possible
# Also called epsilon
def get_max_interference(system: PREM_system, interference_mode: inter_processor_interference_mode, cpu_prio: int, Px: processor) -> int:
    # This is a value that doesn't change, so saved in the processor if already computed
    if Px.max_interference != -1:
        return Px.max_interference

    # Else we have eps = alpha(eps + M_max)
    # The base value of the recurrent equation is the greatest memory phase
    max_interference = Px.M_max
    prev_max_interference = -1
    while prev_max_interference != max_interference:
        prev_max_interference = max_interference
        max_interference = interference_mode.get_inter_processor_interference(system=system, cpu_prio=cpu_prio, delta=max_interference, task=PREM_task(M=0, C=0, T=1))
    
    # Save the value 
    Px.max_interference = max_interference
    return max_interference


# Get the total memory interference in an interval delta
# Also called beta
def get_total_memory_interference(system: PREM_system, interference_mode: inter_processor_interference_mode, cpu_prio: int, Px: processor, task: PREM_task, delta: int) -> int:
    return get_number_memory_phase(Px=Px, task=task, delta=delta) * get_max_interference(system=system, cpu_prio=cpu_prio, Px=Px, interference_mode=interference_mode)


# Get the memory phase start time for the k-th instance 
def get_memory_phase_start_time(system: PREM_system, interference_mode: inter_processor_interference_mode, cpu_prio: int, Px: processor, task: PREM_task, k: int) -> int:
    # This is a recurrent equation where the initial start time is the blocking time B + all tasks that can all start before it
    B = get_blocking_time(Px=Px, prio=task.prio)
    
    # Base values
    start_time = B + sum(htask.e for htask in Px.higher_tasks(task.prio)) + (k - 1) * task.e
    prev_start_time = -1
    
    # As long as the solution is not stable, we repeat
    while prev_start_time != start_time:
        prev_start_time = start_time

        intra_processor_interference = get_intra_processor_interference(Px=Px, 
                                                                                delta=start_time, 
                                                                                prio=task.prio)

        inter_processor_interference = min(interference_mode.get_inter_processor_interference(system=system,
                                                                                              cpu_prio=cpu_prio, 
                                                                                              delta=start_time,
                                                                                              task=task),
                                                                                              get_total_memory_interference(system=system, 
                                                                                                                            interference_mode=interference_mode,
                                                                                                                            cpu_prio=cpu_prio,
                                                                                                                            Px=Px, 
                                                                                                                            task=task,
                                                                                                                            delta=start_time))

        # If inter-processor interference returned -1, then it means that it can't be determined with this policy (e.g. no stable solution)
        if inter_processor_interference == -1:
            return -1

        start_time = B + intra_processor_interference + (k - 1) * task.e + inter_processor_interference
        
    return start_time


# Get the computation phase start time for the k-th instance
def get_computation_phase_start_time(system: PREM_system, interference_mode: inter_processor_interference_mode, cpu_prio: int, Px: processor, task: PREM_task, k: int) -> int:
    # First step is to get the memory phase start time
    memory_start_time = get_memory_phase_start_time(system=system, interference_mode=interference_mode, cpu_prio=cpu_prio, Px=Px, task=task, k=k)

    if memory_start_time == -1:
        return -1
    
    # Save blocking time to go faster
    B = get_blocking_time(Px=Px, prio=task.prio)
    
    # Same for intra-processor interference since memory start is a constant now
    I = get_intra_processor_interference(Px=Px, delta=memory_start_time, prio=task.prio)
    
    # Same total memory interference (beta)
    beta_memory_phase = get_total_memory_interference(system=system, interference_mode=interference_mode, cpu_prio=cpu_prio, Px=Px, task=task, delta=memory_start_time)
    
    # Constant part that does not change
    constant_blocking = B + I + task.M + (k - 1) * task.e
    
    # Base values (start memory plus memory phase)
    start_time = task.M + memory_start_time
    prev_start_time = -1
    
    # As long as the solution is not stable we repeat
    while prev_start_time != start_time:
        prev_start_time = start_time

        inter_processor_interference = interference_mode.get_inter_processor_interference(system=system, 
                                                                                          cpu_prio=cpu_prio, 
                                                                                          delta=start_time,
                                                                                          task=task)
        
        inter_processor_interference_mid = interference_mode.get_inter_processor_interference(system=system, 
                                                                                              cpu_prio=cpu_prio, 
                                                                                              delta=start_time - memory_start_time,
                                                                                              task=task)
        
        # If one of them returns -1, it means that no solution have been found
        if inter_processor_interference == -1 or inter_processor_interference_mid == -1:
            return -1

        start_time = constant_blocking + min(inter_processor_interference,
                                             beta_memory_phase + inter_processor_interference_mid)
    
    return start_time


# Indicate whether the busy period recurrent equation converges (true if it converges)
def is_busy_period_equation_convergent(system: PREM_system, interference_mode: inter_processor_interference_mode, Px: processor, cpu_prio: int) -> bool:
    # Compute max interference
    max_interference = get_max_interference(system=system, interference_mode=interference_mode, cpu_prio=cpu_prio, Px=Px)
    
    higher_cpu_memory_utilisation = sum([Ph.get_memory_utilisation() for Ph in system.higher_processors(prio=cpu_prio)])
    max_interference_on_period = sum([max_interference / task.T for task in Px.tasks()])
    
    return Px.get_utilisation() + min(higher_cpu_memory_utilisation, max_interference_on_period) < 1


# Get the longest busy period of a processor, i.e. the longest time Px will execute tasks with priority higher or equal to the task (including itself)
# Also called L
def get_longest_busy_period(system: PREM_system, interference_mode: inter_processor_interference_mode, cpu_prio: int, Px: processor, task: PREM_task) -> int:
    # If equation not converging... What do we do? Not schedulable? 
    if not is_busy_period_equation_convergent(system=system, interference_mode=interference_mode, Px=Px, cpu_prio=cpu_prio):
        return -1
    
    # Once again it is a recurrent equation... start point is the blocking time B + all tasks that can all start before it + itself
    # Save blocking time to go faster
    B = get_blocking_time(Px=Px, prio=task.prio)
    
    # Base values
    busy_period = B + sum(htask.e for htask in Px.higher_tasks(task.prio)) + task.e
    prev_busy_period = -1
        
    # As long as the solution is not stable we repeat
    while prev_busy_period != busy_period:
        prev_busy_period = busy_period

        # We take into account this task, so we do as if we computed the interference for a lower priority task
        inter_processor_interference = min(interference_mode.get_inter_processor_interference(system=system,
                                                                                              cpu_prio=cpu_prio,
                                                                                              delta=busy_period,
                                                                                              task=task), 
                                           get_total_memory_interference(system=system,
                                                                         interference_mode=interference_mode,
                                                                         cpu_prio=cpu_prio,
                                                                         Px=Px,
                                                                         task=task,
                                                                         delta=busy_period) + Px.M_max)

        # If it returns -1, then so solution found at all so unlimited busy period
        if inter_processor_interference == -1:
            return -1

        busy_period = B + get_intra_processor_interference(Px=Px,
                                                           delta=busy_period, 
                                                           prio=task.prio + 1) + inter_processor_interference
    
    return busy_period


# Get the response time for the k-th instance
def get_response_time_k_occurence(system: PREM_system, interference_mode: inter_processor_interference_mode, cpu_prio: int, Px: processor, task: PREM_task, k: int) -> int:
    # R_i,k = cmp_start + C - (k - 1).T
    computation_start_time = get_computation_phase_start_time(system=system, interference_mode=interference_mode, cpu_prio=cpu_prio, Px=Px, task=task, k = k)
    return computation_start_time + task.C - (k - 1) * task.T


# ----------------------------------------------------
# ----------------- Usable functions -----------------
# ----------------------------------------------------
# Get the response time of a task 
def get_response_time(system: PREM_system, interference_mode: inter_processor_interference_mode, cpu_prio: int, Px: processor, task: PREM_task) -> int:
    # It is the max of the kth response time, k between 1 and ceil(L/T)
    busy_period = get_longest_busy_period(system=system, interference_mode=interference_mode, cpu_prio=cpu_prio, Px=Px, task=task)
    # If busy period non workable, notify that it is not possible
    if busy_period == -1:
        return -1
    
    response_times = []

    for k in range(1, ceil(busy_period / task.T) + 1):
        response_times.append(get_response_time_k_occurence(system=system, interference_mode=interference_mode, cpu_prio=cpu_prio, Px=Px, task=task, k=k))
    
    response_time = max(response_times)
    
    # Also adds the response time to the task to save its value
    task.R = response_time
    
    return response_time


# Get the response time of all tasks in a system
def get_response_time_system(system: PREM_system, interference_mode: inter_processor_interference_mode = inter_processor_interference_mode(get_classic_inter_processor_interference)) -> list[list[int]]:
    # Get processors from system
    processors = system.processors()
    response_time_system = []

    for cpu_prio in range(0, len(processors)):
        response_time_processor = []
        Px = processors[cpu_prio]
        
        for task in Px.tasks():
            response_time = get_response_time(system=system, interference_mode=interference_mode, cpu_prio=cpu_prio, Px=Px, task=task)
            # If response time is invalid, then return empty
            if response_time == -1:
                return []
            
            response_time_processor.append(response_time)
        
        response_time_system.append(response_time_processor)
    
    system.system_analysed = True
    return response_time_system


# Returns if system schedulable per processor
def is_system_schedulable_per_processor(system: PREM_system, interference_mode: inter_processor_interference_mode = inter_processor_interference_mode(get_classic_inter_processor_interference)) -> list[bool]:
    if not system.system_analysed:
        get_response_time_system(system=system, interference_mode=interference_mode)
    
    processors = system.processors()
    schedulability = []
    for cpu_prio in range(0, len(processors)):
        Px = processors[cpu_prio]
        schedulable = True
        for task in Px.tasks():
            schedulable &= task.is_schedulable()
        
        schedulability.append(schedulable)
    
    return schedulability
