# Imports 
from __future__ import annotations
from math import floor
from random import uniform
from typing import Callable
from utils.prem_utils import *
from utils.task_generation.generator_emstada import gen_taskset

# Constants
schedcat_mediator = './utils/schedcat_mediator.py'
taskset_file = './utils/schedcat_log.log'

# Interval class
class interval():    
    def __init__(self, interval_min: int, interval_max: int) -> None:
        self.min = interval_min
        self.max = interval_max
        
    
    def interval_size(self) -> int:
        return self.max - self.min + 1
    
    
    def get_interval(self) -> tuple[int, int]:
        return (self.min, self.max)
    
    
    def choose_random(self, random_function: Callable[[int, int], float]) -> float:
        return floor(random_function(self.min, self.max + 1))
    
    def __str__(self) -> str:
        return f'[{self.min:d};{self.max:d}]'
    

def times100(time):
    return time * 100


# Generates a PREM taskset with a specified task number, period interval and distribution (for random), CPU utilisation and memory bandwidth utilisation.
# Returns a processor!
def generate_prem_taskset(task_number: int,
                          period_interval: interval,
                          period_distribution: str,
                          utilisation: float,
                          bandwidth_utilisation_interval: interval,
                          scale: Callable[[int], int],
                          min_cost: int) -> processor:

    # Regenerate if cost is 0 (means that the task has no execution)
    curr_min_cost = 0
    while curr_min_cost < min_cost:
        taskset = gen_taskset(periods=(period_interval.min, period_interval.max),
                            period_distribution=period_distribution, 
                            tasks_n=task_number, 
                            utilization=utilisation,
                            scale=scale)
        curr_min_cost = taskset.min_cost()
    
    # Prepare processor
    Px = processor()

    for generated_task in taskset:
        # Compute memory phase and computation phase
        bandwidth_utilisation = bandwidth_utilisation_interval.choose_random(uniform) / 100 # Interval is only int, so need to divide by 100 to get a percentage
        
        # Memory phase can be 0, computation phase cannot
        mem_phase = floor(generated_task.cost * bandwidth_utilisation)
        comp_phase = generated_task.cost - mem_phase
        
        # Create PREM task
        task = PREM_task(M=mem_phase, C=comp_phase, T=generated_task.period)
        Px.add_task(task=task)
        
    return Px


# Generates a PREM system with a specified processor number, task numbers, period intervals and distributions (for random), CPU utilisation and memory bandwidth utilisation.
# You can choose a different task number for each CPU with different period intervals and distributions. However utilisations will be the same for all of them
# Returns a PREM system!
def generate_prem_system(processor_number: int, 
                         task_number: int, 
                         period_interval: interval, 
                         period_distribution: str, 
                         utilisation: float, 
                         bandwidth_utilisation_interval: interval,
                         scale: Callable[[int], int],
                         min_cost: int) -> PREM_system:
    # We generate processor_number tasksets and we assemble them to make a system!
    Px_list: list[processor] = []
    for _ in range(0, processor_number):
        Px = generate_prem_taskset(task_number=task_number,
                                   period_interval=period_interval,
                                   period_distribution=period_distribution,
                                   utilisation=utilisation,
                                   bandwidth_utilisation_interval=bandwidth_utilisation_interval,
                                   scale=scale,
                                   min_cost=min_cost)
        Px_list.append(Px)
    
    system = PREM_system(processors=Px_list, utilisation=utilisation)
    return system


# Rescales a PREM system with the specified scale factor function.
def rescale_system(system: PREM_system, factor: Callable[[int], int]):
    # Reset the system
    system.reset()
    
    # For each task of the system, scale the memory phase and the computation phase.
    for Px in system.processors():
        for task in Px.tasks():
            task.M = factor(task.M)
            task.C = factor(task.C)
            task.e = task.M + task.C
            task.T = factor(task.T)
            task.D = factor(task.D)