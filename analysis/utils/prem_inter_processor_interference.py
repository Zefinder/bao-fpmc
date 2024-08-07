# This is the file where there are all functions to compute interprocessor interferences
# There are 3 functions for now: 
# - Classic
# - Global task
# - Knapsack
# Use the class to choose which ones you want for your computations

# Imports
from typing import Callable
from math import ceil
from utils.priority_queue import PriorityTaskQueue
from utils.prem_utils import *

# Classes
# Just give this object with the desired modes in it
class inter_processor_interference_mode():
    _interference_functions: tuple[Callable[[PREM_system, int, int, PREM_task], int], ...]
    
    
    def __init__(self, *interference_functions: Callable[[PREM_system, int, int, PREM_task], int]) -> None:
        self._interference_functions = interference_functions
    
    
    # Returns the inter-processor interference, which is the minimum of all functions
    def get_inter_processor_interference(self, system: PREM_system, cpu_prio: int, delta: int, task: PREM_task) -> int:
        interferences = []
        for interference_function in self._interference_functions:
            interference = interference_function(system, cpu_prio, delta, task)
            
            if interference != -1:
                interferences.append(interference)
            
        return min(interferences) if len(interferences) != 0 else -1
    
    
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
        for task in Px.tasks():
            interference += ceil((delta + task.R - task.e) / task.T) * task.M
            
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
            # print('delta:', delta)
            interference += ceil(delta / global_task.T) * global_task.M

    except:
        # TODO Find why utilisation <= 1 and still impossible
        # print(global_utilisation + (task.M / task.T))
        interference = -1
    
    return interference


# ----------------------------------------------------
# ----------------- Knapsack version -----------------
# ----------------------------------------------------
class knapsack_object:
    def __init__(self, task: PREM_task) -> None:
        self.v = task.M
        self.w = task.e


    def __str__(self) -> str:
        return f'v={self.v:d},w={self.w:d}'
  

class knapsack_problem:
    _problem_solution: int


    def __init__(self) -> None:
        self._objects = []


    def add_object(self, obj: knapsack_object, n: int = 1) -> None:
        # Add n times the object
        [self._objects.append(obj) for _ in range(0, n)]


    def solve(self, W: int) -> None:
        # Create matrix, add one row of 0!
        m = [[0] * (W + 1) for _ in range(0, len(self._objects) + 1)]

        # Begin algorithm
        for i in range(0, len(self._objects)):
            # Get object to not call it for array each time
            obj = self._objects[i]

            for j in range(1, W + 1):
                if obj.w > j:
                    m[i + 1][j] = max(m[i][j], min(obj.v, j))
                else:
                    m[i + 1][j] = max(m[i][j], m[i][j - obj.w] + obj.v)

        # Set problem solution
        # print(len(self._objects), W, len(m), len(m[0]))
        self._problem_solution = m[len(self._objects)][W]


    def get_solution(self) -> int:
        return self._problem_solution


    def __str__(self):
        res = ''
        for obj in self._objects:
            res += f'({obj.__str__():s}),'

        return res[:-1]
  

def prepare_knapsack_problem(system: PREM_system, cpu_prio: int, delta: int):
    problem = knapsack_problem()

    # Create the queue and sort it by memory impact (M/e)
    queue = PriorityTaskQueue(lambda task1, task2: 1 if (task1.M / task1.e) > (task2.M / task2.e) else 0)

    # Add all tasks of higher priority processors to the priority queue
    for Px in system.higher_processors(prio=cpu_prio):
        for htask in Px.tasks():
            queue.insert(htask)

    # For each popped task, add knapsack objects to the problem
    while not queue.isEmpty():
        htask = queue.delete()
        
        # Number of possible jobs: (delta + R - e) / T rounded up
        n = ceil((delta + htask.R + htask.e) / htask.T)
        problem.add_object(obj=knapsack_object(task=htask), n=n)

    # Return the problem
    return problem


def get_knapsack_inter_processor_interference(system: PREM_system, cpu_prio: int, delta: int, task: PREM_task) -> int:
    # Prepare the knapsack problem
    problem = prepare_knapsack_problem(system=system, cpu_prio=cpu_prio, delta=delta)

    # Solve the problem with weight being delta
    problem.solve(W=delta)

    # print(problem.get_solution())

    # Return the solution
    return problem.get_solution()