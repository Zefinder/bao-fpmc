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
    return min([ltask.e for ltask in Px.tasks() if ltask.prio > prio])


# Get the intra-processor interference time of a task with higher prio on the same CPU
def get_intra_processor_interference(Px: processor, delta: int, prio: int) -> int:
    # Remember that it is descending prio
    return sum([ceil(delta / htask.T) * htask.e for htask in Px.tasks() if htask.prio < prio])


# Get the inter-processor interference, the paper version.
# Takes the number of time a task can start (considering jitter) and multiply by its memory time
def get_inter_processor_interference(system: PREM_system, cpu_prio: int, delta: int) -> int:
    interference = 0
    for Px in system.higher_processors(cpu_prio):
        for task in Px.tasks():
            interference += ceil((delta + task.R - task.e) / task.T) * task.M
            
    return 0


tau_1 = PREM_task(2, 1, 24)
tau_2 = PREM_task(4, 6, 40)
tau_3 = PREM_task(14, 10, 50)
tau_4 = PREM_task(2, 6, 10)

P0 = processor([tau_1, tau_2, tau_3])
P1 = processor([tau_1, tau_2, tau_3])
P2 = processor([tau_1, tau_2, tau_3])
P3 = processor([tau_1, tau_2, tau_3])
P4 = processor([tau_1, tau_2, tau_3])
P5 = processor([tau_4])

system = PREM_system([P0, P1, P2, P3, P4, P5])

rate_monotonic_scheduler(Px=P0)
rate_monotonic_scheduler(Px=P5)

print(system)

print('According to P2, lower priority CPUs are:')
for cpu in system.lower_processors(2):
    print(cpu)

print('According to P2, higher priority CPUs are:')
for cpu in system.higher_processors(2):
    print(cpu)

