# Imports 
import os
from math import ceil
from prem_utils import *

# Constants
taskset_file = './schedcat_log.log'

# Interval class
class interval():    
    def __init__(self, interval_min: int, interval_max: int) -> None:
        self.min = interval_min
        self.max = interval_max
        
    def interval_size(self) -> int:
        return self.max - self.min + 1
    
    def get_interval(self) -> tuple[int, int]:
        return (self.min, self.max)

# TODO generate tasks with interval memory utilisation!

# Generates a PREM taskset with a specified task number, period interval and distribution (for random), CPU utilisation and memory bandwidth utilisation.
# Returns a processor!
def generate_prem_taskset(task_number: int, period_interval: interval, period_distribution: str, utilisation: float, bandwidth_utilisation: float) -> processor:
    # Call python 2.7 to generate a taskset with schedcat, result in schedcat_log.log
    os.system(f'python2.7 schedcat_mediator.py {period_interval.min:d} {period_interval.max:d} {period_distribution:s} {task_number:d} {utilisation:.04f}')
    
    # Prepare processor
    Px = processor()
    
    # Get result in file and create a processor object for it
    schedcat_log = open(taskset_file, 'r')
    line = schedcat_log.readline()
    while line:
        # We read the task and split wcet and period
        task_data = line.replace('\n', '').split(',')
        wcet = int(task_data[0])
        period = int(task_data[1])
        
        # Compute memory phase and computation phase
        mem_phase = ceil(wcet * bandwidth_utilisation)
        comp_phase = wcet - mem_phase
        
        # Create PREM task
        task = PREM_task(M=mem_phase, C=comp_phase, T=period)
        Px.add_task(task=task)
        
        # Read next line
        line = schedcat_log.readline()
        
    return Px

# Generates a PREM system with a specified processor number, task numbers, period intervals and distributions (for random), CPU utilisation and memory bandwidth utilisation.
# You can choose a different task number for each CPU with different period intervals and distributions. However utilisations will be the same for all of them
# Returns a PREM system!
def generate_prem_system(processor_number: int, task_numbers: list[int], period_intervals: list[interval], period_distributions: list[str], utilisation: float, bandwidth_utilisation: float) -> PREM_system:
    # We generate processor_number tasksets and we assemble them to make a system!
    system = PREM_system()
    for cpu_prio in range(0, processor_number):
        system.add_processor(cpu=generate_prem_taskset(task_number=task_numbers[cpu_prio],
                                                       period_interval=period_intervals[cpu_prio],
                                                       period_distribution=period_distributions[cpu_prio],
                                                       utilisation=utilisation,
                                                       bandwidth_utilisation=bandwidth_utilisation)) # For this I don't really understand the "scale down"
        
    return system

# Generates system_number times a system with the specified parameters. It's just a for loop of generate_prem_system but with the same parameters (so less messy code in the experimentations)
def generate_prem_systems(system_number: int, processor_number: int, task_numbers: list[int], period_intervals: list[interval], period_distributions: list[str], utilisation: float, bandwidth_utilisation: float) -> list[PREM_system]:
    system_list = []
    for _ in range(0, system_number):
        system_list.append(generate_prem_system(processor_number=processor_number,
                                                task_numbers=task_numbers,
                                                period_intervals=period_intervals,
                                                period_distributions=period_distributions,
                                                utilisation=utilisation,
                                                bandwidth_utilisation=bandwidth_utilisation))
        
    return system_list