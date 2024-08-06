# This is the file where there are all functions to compute interprocessor interferences
# There are 3 functions for now: 
# - Classic
# - Global task
# - Knapsack
# Use the class to choose which ones you want for your computations

# Imports
from typing import Callable
from math import ceil
from utils.prem_utils import *

# Classes
# Just give this object with the desired modes in it
class inter_processor_interference_mode():
    _interference_functions: tuple[Callable[[PREM_system, int, int], int], ...]
    
    
    def __init__(self, *interference_functions: Callable[[PREM_system, int, int], int]) -> None:
        self._interference_functions = interference_functions
    
    
    # Returns the inter-processor interference, which is the minimum of all functions
    def get_inter_processor_interference(self, system: PREM_system, cpu_prio: int, delta: int) -> int:
        interference = []
        for interference_function in self._interference_functions:
            interference.append(interference_function(system, cpu_prio, delta))
            
        return min(interference)
    
    
# Functions
# Get the inter-processor interference, the paper version.
# Takes the number of time a task can start (considering jitter) and multiply by its memory time
# Also called alpha
def get_classic_inter_processor_interference(system: PREM_system, cpu_prio: int, delta: int) -> int:
    interference = 0
    for Px in system.higher_processors(cpu_prio):
        for task in Px.tasks():
            interference += ceil((delta + task.R - task.e) / task.T) * task.M
            
    return interference


# Global task interference
# Get the global task, if global task is None, then it means that you need to compute it from the 
# previous CPUs. If it is the first CPU, then there is no CPU...
def get_global_task(system: PREM_system, cpu_prio: int, delta: int) -> PREM_task:
    Px = system.processors()[cpu_prio]
    global_task = Px.get_global_task()
    
    # If M is not -1, then global task has been initialised
    if global_task.M != -1:
        return global_task
    
    # All previous global tasks should be calculated
    global_tasks = [P.get_global_task() for P in system.higher_processors(prio=cpu_prio)]
    
    # This is a recurrent equation to determine the smallest response time with only global tasks
    # T = M_max + C_min + I(T - C_min)
    # We can separate it in Tm = M_max + I(Tm) and then T = Tm + C_min
    # Base value of T is M_max and C_min
    Tm = Px.M_max
    prev_Tm = -1
    while prev_Tm != Tm:
        prev_Tm = Tm
        Tm = Px.M_max + sum([ceil(delta / gtask.T) * gtask.M for gtask in global_tasks])
    
    T = Tm + Px.C_min
    
    # Save global task
    Px.set_global_task(T=T)
    
    return Px.get_global_task()


# This is the v1 of the improvement of the classic PREM. You take the worst task possible (M_max and C_min),
# you search for it's max response time and it'll be it's period
# The idea behind it is to approximate the multi-core system to a single-core with preemptive fixed-priority scheduling. 
# However the policy is arbitrary, P1 will have the highest global task priority. 
# To remember things, global tasks' periods are stored in processors when computed.
def get_global_task_inter_processor_interference(system: PREM_system, cpu_prio: int, delta: int) -> int:
    interference = 0
    
    # For all higher CPU, we ask (or create) a global task and compute interference with it
    for _ in system.higher_processors(cpu_prio):
        global_task = get_global_task(system=system, cpu_prio=cpu_prio, delta=delta)
        interference += ceil(delta / global_task.T) * global_task.M
            
    return interference


def get_knapsack_inter_processor_interference(system: PREM_system, cpu_prio: int, delta: int) -> int:
    return 0