# Imports
from __future__ import annotations
from typing import Callable
from utils.prem_utils import PREM_task

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