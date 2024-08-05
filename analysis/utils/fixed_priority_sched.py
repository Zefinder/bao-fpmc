# This file will contain schedulers to assign a fixed priority to tasks
# Functions of that file will have the following format:
# def sched(Px: processor) -> None
# That means that functions will modify the PREM objects that are in the CPU 

# Imports
from prem_utils import *
from typing import Callable

# Classes
# Priority queue for tasks (base from https://www.geeksforgeeks.org/priority-queue-in-python/)
# Compare function is (task1, task2) -> 1 if condition else 0, 1 if higher prio of course
class PriorityTaskQueue(object):
    # Creates a queue with a lambda to compare objects
    def __init__(self, compare: Callable[[PREM_task, PREM_task], int] = lambda task1, task2: 0):
        self._queue = []
        self._compare = compare
 
 
    def __str__(self):
        return ' '.join([str(i) for i in self._queue])
 
 
    # for checking if the queue is empty
    def isEmpty(self) -> bool:
        return len(self._queue) == 0
 
 
    # for inserting an element in the queue
    def insert(self, task: PREM_task) -> None:
        self._queue.append(task)
 
 
    # for popping an element based on Priority
    def delete(self) -> PREM_task:
        try:
            max_val = 0
            for i in range(len(self._queue)):
                if self._compare(self._queue[i], self._queue[max_val]) == 1:
                    max_val = i
            item = self._queue[max_val]
            del self._queue[max_val]
            return item
        except IndexError:
            print()
            exit()


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
        

def deadline_monotonic_scheduler(Px: processor) -> None:
    queue = PriorityTaskQueue(lambda task1, task2: 1 if task1.D < task2.D else 0)
    set_prio(queue=queue, tasks=Px.tasks())


def shortest_job_first_scheduler(Px: processor) -> None:
    queue = PriorityTaskQueue(lambda task1, task2: 1 if task1.e < task2.e else 0)
    set_prio(queue=queue, tasks=Px.tasks())
    