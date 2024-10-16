# This is the file where there are all functions to compute interprocessor interferences
# There are 3 functions for now: 
# - Classic
# - Global task
# - Knapsack
# Use the class to choose which ones you want for your computations

# Imports
from __future__ import annotations
from typing import Callable
from math import ceil, floor
from utils.priority_queue import PriorityTaskQueue
from utils.prem_utils import *
import copy

# Classes
# Just give this object with the desired modes in it
class inter_processor_interference_mode():
    _interference_functions: tuple[Callable[[PREM_system, int, int, PREM_task], int], ...]
    _interference_max_computation : int
    _interference_calculated: int
    _interference_results: list[int]
    _max_value: int
    
    
    def __init__(self, *interference_functions: Callable[[PREM_system, int, int, PREM_task], int], interference_max_computation: int = -1) -> None:
        self._interference_functions = interference_functions
        self._interference_max_computation = interference_max_computation
        self._interference_calculated = -1
        self._interference_results = []
        self._max_value = 0
    

    def reset_count(self):
        self._interference_results = []
        self._max_value = 0
        self._interference_calculated = 0
    
    
    # Returns the inter-processor interference, which is the minimum of all functions
    def get_inter_processor_interference(self, system: PREM_system, cpu_prio: int, delta: int, task: PREM_task) -> int:
        interferences = []
        for interference_function in self._interference_functions:
            interference = interference_function(system, cpu_prio, delta, task)
            
            if interference != -1:
                interferences.append(interference)
        
        result = min(interferences) if len(interferences) != 0 else -1
        
        # Save max to not have to search
        if result > self._max_value:
            self._max_value = result
        
        # If result has already appeared, then take max of interferences 
        if result in self._interference_results:
            result = self._max_value
        
        # If calculated interference is greater than the max computed, return -1
        if self._interference_max_computation != -1 and self._interference_calculated > self._interference_max_computation:
            result = -1

        self._interference_calculated += 1

        return result
    
    
# Functions

# ----------------------------------------------------
# ------------------- Paper version ------------------
# ----------------------------------------------------
# Get the inter-processor interference, the paper version.
# Takes the number of time a task can start (considering jitter) and multiply by its memory time
# Also called alpha
def get_classic_inter_processor_interference(system: PREM_system, cpu_prio: int, delta: int, task: PREM_task) -> int:
    interference = 0
    for Px in system.higher_processors(cpu_prio):
        for htask in Px.tasks():
            interference += ceil((delta + htask.R - htask.e) / htask.T) * htask.M
            
    return interference


# ----------------------------------------------------
# ---------------- Global task version ---------------
# ----------------------------------------------------
# Get the global task, if global task is None, then it means that you need to compute it from the 
# previous CPUs. If it is the first CPU, then there is no CPU...
def get_global_task(system: PREM_system, cpu_prio: int) -> PREM_task:
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
    # And I(x) = ceil(x/Tj) * Mj for tau_j in global tasks
    # Base value of T is M_max and C_min
    Tm = Px.M_max
    prev_Tm = -1
    while prev_Tm != Tm:
        prev_Tm = Tm
        Tm = Px.M_max + sum([ceil(Tm / gtask.T) * gtask.M for gtask in global_tasks])
    
    T = Tm + Px.C_min
    
    # Save global task
    Px.set_global_task(T=T)
    
    return Px.get_global_task()


# This is the v1 of the improvement of the classic PREM. You take the worst task possible (M_max and C_min),
# you search for it's max response time and it'll be it's period
# The idea behind it is to approximate the multi-task multi-core system to a single-task multi-core with preemptive fixed-priority scheduling. 
# To remember things, global tasks' periods are stored in processors when computed.
# This is pessimistic when there is a task with a big M and one with a small C
def get_global_task_inter_processor_interference(system: PREM_system, cpu_prio: int, delta: int, task: PREM_task) -> int:
    # This equation has a stable solution if the utilisation of global tasks + of this task <= 1
    global_tasks = [get_global_task(system=system, cpu_prio=prio) for prio in range(0, cpu_prio)]
    global_utilisation = sum([gtask.M / gtask.T for gtask in global_tasks])

    if global_utilisation + (task.M / task.T) > 1:
        # The utilisation is over 1, it is impossible to schedule it!
        return -1

    # For all higher CPU, we ask (or create) a global task and compute interference with it
    interference = 0
    try:
        for prio in range(0, cpu_prio):
            global_task = get_global_task(system=system, cpu_prio=prio)
            interference += ceil(delta / global_task.T) * global_task.M

    except:
        # TODO Find why utilisation <= 1 and still impossible
        interference = -1
    
    return interference


# ----------------------------------------------------
# ----------------- Knapsack version -----------------
# ----------------------------------------------------
# This one is used to transform the problem into a knapsack problem and then
# Solve the knapsack which gives the interference!
# This is really long to get a good result with all processors.
class knapsack_object:
    def __init__(self, task: PREM_task) -> None:
        self.v = task.M
        self.w = task.e


    def __str__(self) -> str:
        return f'v={self.v:d},w={self.w:d}'
    
    
    def __deepcopy__(self, memo) -> "knapsack_object":
        # Need to create a dummy task with the object values
        new_object = knapsack_object(PREM_task(M=self.v,
                                               C=self.w - self.v,
                                               T=0))
        return new_object
  

class knapsack_problem:
    _objects: list[knapsack_object]
    _unique_objects: list[tuple[knapsack_object, int]]
    _problem_solution: int
    _W : int

    def __init__(self, W) -> None:
        self._objects = []
        self._unique_objects = []
        self._problem_solution = -1
        self._W = W


    def add_object(self, obj: knapsack_object, n: int = 1) -> None:
        # Add n times the object to the list
        [self._objects.append(obj) for _ in range(0, n)]
        
        # Add to the unique list with index of the last item in the object list
        if len(self._unique_objects) == 0:
            index = -1
        else:
            index = self._unique_objects[-1][1]
            
        self._unique_objects.append((obj, index + n))


    def solve(self) -> None:
        # Save maximum interference
        max_interference = 0
        
        # The knapsack is solved n times, where n is the number of unique objects
        # For each iteration, we remove one object that is in the unique object list
        for unique_index in range(0, len(self._unique_objects)):
            # Get the value of the object to remove
            cut_object_value = self._unique_objects[unique_index][0].v
            
            # Get the index of the object to remove
            cut_objet_index = self._unique_objects[unique_index][1]
            
            # Copy the list so no data loss
            object_list = copy.deepcopy(self._objects)
            
            # Remove the object from the copied list
            del object_list[cut_objet_index]
        
            # Create matrix, add one row of 0!
            m = [[0] * (self._W + 1) for _ in range(0, len(object_list) + 1)]
            
            # Begin algorithm
            for i in range(0, len(object_list)):
                # Get object to not call it for array each time
                obj = object_list[i]

                for j in range(1, self._W + 1):
                    # Normal knapsack problem
                    if obj.w > j:
                        m[i + 1][j] = m[i][j]
                    else:
                        m[i + 1][j] = max(m[i][j], m[i][j - obj.w] + obj.v)
                        
                    # If last object placed, then compute max interference for this j placing the cut object
                    if i == len(object_list) - 1:
                        # Backtrack solution to see free space
                        index = i
                        W = j
                        
                        # While still in objects with a positive weight and if there is something left in the knapsack
                        while W > 0 and index >= 0 and m[index + 1][W] != 0:
                            current_value = m[index + 1][W]
                            previous_value = m[index][W]
                            
                            # If different values, then object is placed
                            if current_value != previous_value:
                                W = W - object_list[index].w
                            
                            # Change object
                            index = index - 1
                        
                        # W contains the free space left in the knapsack of weight j
                        # To get the total free space, add the difference between j and the final weight
                        W += self._W - j
                        
                        # The cut object has a max value of the original object
                        interference_value = m[i + 1][j] + min(W, cut_object_value)
                        if interference_value > max_interference:
                            max_interference = interference_value

        # Solution is the maximum of the interference values computed
        self._problem_solution = max_interference


    def get_solution(self) -> int:
        return self._problem_solution
    

    def __str__(self):
        res = ''
        for obj in self._objects:
            res += f'({obj.__str__():s}),'

        return res[:-1]
  

def prepare_knapsack_problem(system: PREM_system, cpu_prio: int, delta: int) -> knapsack_problem:
    # Create the problem
    problem = knapsack_problem(W=delta)

    # Create the queue and sort it by memory impact (M/e)
    queue = PriorityTaskQueue(lambda task1, task2: 1 if (task1.M) > (task2.M) else (1 if (task1.M) == (task2.M) and (task1.T) < (task2.T) else 0))

    # Add all tasks of higher priority processors to the priority queue
    for Px in system.higher_processors(prio=cpu_prio):
        for htask in Px.tasks():
            if htask.M != 0:
                queue.insert(htask)

    # For each popped task, add knapsack objects to the problem
    while not queue.isEmpty():
        htask = queue.delete()
        
        # Number of possible jobs: (delta + R - e) / T rounded up
        n = ceil((delta + htask.R + htask.e) / htask.T)
        problem.add_object(obj=knapsack_object(task=htask), n=n)

    # Return the problem
    return problem


def get_knapsack_inter_processor_interference(system: PREM_system, cpu_prio: int, delta: int, _: PREM_task) -> int:
    # If delta is 0, no memory interference since no memory time
    if delta == 0:
        return 0

    # Prepare the problem
    problem = prepare_knapsack_problem(system=system, cpu_prio=cpu_prio, delta=delta)

    # Solve the problem
    problem.solve()

    if problem.get_solution() == -2:
        print(system)
        
    # Return the problem solution
    return problem.get_solution()


class greedy_knapsack_problem(knapsack_problem):
    _max_M: int
    _density_dict: dict[float, list[int]]

    def __init__(self, W) -> None:
        super().__init__(W=W)
        self._max_M = 0
        self._density_dict = {}
        

    # Add the sum increment in the add_object method
    def add_object(self, obj: knapsack_object, n: int = 1) -> None:
        density = obj.v / obj.w
        if density in self._density_dict:
            self._density_dict[density][0] += n * obj.v
            self._density_dict[density][1] += n * obj.w
        else:
            self._density_dict[density] = [n * obj.v, n * obj.w]

        if (self._max_M < obj.v):
            self._max_M = obj.v


    def __prepare_solving(self):
        queue = PriorityTaskQueue(lambda task1, task2: 1 if (task1.M / task1.e) > (task2.M / task2.e) else 0)

        # Add all tasks of higher priority processors to the priority queue
        for (M, e) in self._density_dict.values():
            htask = PREM_task(M=M, C=e-M, T=0)
            queue.insert(htask)

        # For each popped task, add knapsack objects to the problem
        while not queue.isEmpty():
            htask = queue.delete()
            super().add_object(obj=knapsack_object(task=htask), n=1)
        

    # Redefine the solve method
    def solve(self) -> None:
        # Sort items and add objects to list 
        self.__prepare_solving()
        
        m1 = 0
        m2 = 0
        w = 0
        obj_index = 0
        
        # Put objects greedily in the bag
        for obj in self._objects:
            if w + obj.w <= self._W:
                m1 += obj.v
                w += obj.w
                obj_index += 1 
            else:
                # When the item can't fit in the bag, then it's the critical item 
                # If it is the last item: Dantzig bound!
                if obj is self._objects[-1] or obj is self._objects[0]:
                    m2 = floor(((self._W - w) / obj.w) * obj.v)
                
                # Else it is the Martello and Toth bound
                else:
                    obj_before = self._objects[obj_index - 1]
                    obj_after = self._objects[obj_index + 1]
                    m2 = max(floor(((self._W - w) / obj_after.w) * obj_after.v), obj.v - floor(((obj.w + w - self._W) / obj_before.w) * obj_before.v))
                break

        # Approximated solution and adding the cut object
        knapsack_solution = min(m1 + m2, 2 * max(m1, m2)) + self._max_M

        self._problem_solution = min(self._W, knapsack_solution)


def prepare_greedy_knapsack(system: PREM_system, cpu_prio: int, delta: int) -> greedy_knapsack_problem:
    # Create the problem
    problem = greedy_knapsack_problem(W=delta)
    
    for Px in system.higher_processors(prio=cpu_prio):
        for htask in Px.tasks():
            if htask.M != 0:
                n = ceil((delta + htask.R - htask.e) / htask.T)
                problem.add_object(obj=knapsack_object(task=htask), n=n)

    # Return the problem
    return problem


def get_greedy_knapsack_inter_processor_interference(system: PREM_system, cpu_prio: int, delta: int, _: PREM_task) -> int:
    # If delta is 0, no memory interference since no memory time
    if delta == 0:
        return 0

    # Prepare the problem
    problem = prepare_greedy_knapsack(system=system, cpu_prio=cpu_prio, delta=delta)
    

    # Solve the problem
    problem.solve()

    # Return the problem solution
    return problem.get_solution()