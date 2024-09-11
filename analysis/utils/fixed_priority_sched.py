# This file will contain schedulers to assign a fixed priority to tasks
# Functions of that file will have the following format:
# def sched(Px: processor) -> None
# That means that functions will modify the PREM objects that are in the CPU 

# Imports
from __future__ import annotations
from typing import Callable
from utils.priority_queue import PriorityTaskQueue
from utils.prem_utils import *


# Functions
# Empty queue and put priority
def set_prio(queue: PriorityTaskQueue, tasks: list[PREM_task]) -> None:
    # In the queue tasks are in T order!
    for task in tasks:
        queue.insert(task=task)
    
    # Just empty the queue
    priority = 1
    while not queue.isEmpty():
        task = queue.delete()
        task.prio = priority
        priority += 1


# Rate monotonic scheduler, prio goes to the one with the smallest T
def rate_monotonic_scheduler(Px: processor) -> None:
    queue = PriorityTaskQueue(lambda task1, task2: 1 if task1.T < task2.T else 0)
    set_prio(queue=queue, tasks=Px.tasks())
      
        
# Deadline monotonic scheduler, prio goes to the one with the smallest D
def deadline_monotonic_scheduler(Px: processor) -> None:
    queue = PriorityTaskQueue(lambda task1, task2: 1 if task1.D < task2.D else 0)
    set_prio(queue=queue, tasks=Px.tasks())


# Shortest job first scheduler, prio goes to the one with the smallest execution time
def shortest_job_first_scheduler(Px: processor) -> None:
    queue = PriorityTaskQueue(lambda task1, task2: 1 if task1.e < task2.e else 0)
    set_prio(queue=queue, tasks=Px.tasks())
    

# Sets all processors' priority according to a fixed priority policy
def set_system_priority(system: PREM_system, fp_scheduler: Callable[[processor], None]) -> None:
    for Px in system.processors():
        fp_scheduler(Px)