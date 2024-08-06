# Imports 
import os
from math import ceil, floor
from random import uniform
from typing import Callable
from utils.prem_utils import *

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


# Generates a PREM taskset with a specified task number, period interval and distribution (for random), CPU utilisation and memory bandwidth utilisation.
# Returns a processor!
def generate_prem_taskset(task_number: int, period_interval: interval, period_distribution: str, utilisation: float, bandwidth_utilisation_interval: interval, taskset_number: int = 1) -> list[processor]:
    # Call python 2.7 to generate a taskset with schedcat, result in schedcat_log.log
    os.system(f'python2.7 {schedcat_mediator:s} {taskset_number:d} {period_interval.min:d} {period_interval.max:d} {period_distribution:s} {task_number:d} {utilisation:.04f}')
    
    # Get result in file and create a processor object for it
    schedcat_log = open(taskset_file, 'r')
    
    # We create the CPU list
    processor_list = []
    
    # For each taskset we create a processor and we read the right amount of lines
    for _ in range(0, taskset_number):
        # Prepare processor
        Px = processor()

        for _ in range(0, task_number):
            # We read the line
            line = schedcat_log.readline()
            
            # We read the task and split wcet and period
            task_data = line.replace('\n', '').split(',')
            wcet = int(task_data[0])
            period = int(task_data[1])
            
            # Compute memory phase and computation phase
            bandwidth_utilisation = bandwidth_utilisation_interval.choose_random(uniform) / 100 # Interval is only int, so need to divide by 100 to get a percentage
            mem_phase = ceil(wcet * bandwidth_utilisation)
            comp_phase = wcet - mem_phase
            
            # Create PREM task
            task = PREM_task(M=mem_phase, C=comp_phase, T=period)
            Px.add_task(task=task)
        
        processor_list.append(Px)
        
    return processor_list


# Generates a PREM system with a specified processor number, task numbers, period intervals and distributions (for random), CPU utilisation and memory bandwidth utilisation.
# You can choose a different task number for each CPU with different period intervals and distributions. However utilisations will be the same for all of them
# Returns a PREM system!
def generate_prem_system(processor_number: int, task_number: int, period_interval: interval, period_distribution: str, utilisation: float, bandwidth_utilisation_interval: interval) -> PREM_system:
    # We generate processor_number tasksets and we assemble them to make a system!
    system = PREM_system(processors=generate_prem_taskset(taskset_number=processor_number,
                                                          task_number=task_number,
                                                          period_interval=period_interval,
                                                          period_distribution=period_distribution,
                                                          utilisation=utilisation,
                                                          bandwidth_utilisation_interval=bandwidth_utilisation_interval))
        
    return system