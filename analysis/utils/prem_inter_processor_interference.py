# This is the file where there are all functions to compute interprocessor interferences
# There are 3 functions for now: 
# - Classic
# - Global task
# - Knapsack
# Use the class to choose which ones you want for your computations

# Imports
from typing import Callable
from math import ceil
from multiprocessing import Pool
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
# When you will want to solve the knapsack, you can specify the number of processors
# you want to mix. 
# The best solution is when batch_number = system.length(), but this takes quite some time...
# (1 min for 4 processors, around 20 min for 16 processors)
class knapsack_object:
    def __init__(self, task: PREM_task) -> None:
        self.v = task.M
        self.w = task.e


    def __str__(self) -> str:
        return f'v={self.v:d},w={self.w:d}'
  

class knapsack_problem:
    _problem_solution: int
    _problem_solution_path: list[knapsack_object]
    _shift: int = 0
    _W : int

    def __init__(self, W) -> None:
        self._objects: list[knapsack_object] = []
        self._W = W


    def add_object(self, obj: knapsack_object, n: int = 1) -> None:
        # Add n times the object
        [self._objects.append(obj) for _ in range(0, n)]


    def solve(self) -> None:
        # Create matrix, add one row of 0!
        m = [[0] * (self._W + 1) for _ in range(0, len(self._objects) + 1)]

        # Begin algorithm
        for i in range(0, len(self._objects)):
            # Get object to not call it for array each time
            obj = self._objects[i]

            for j in range(1, self._W + 1):
                if obj.w > j:
                    m[i + 1][j] = max(m[i][j], min(obj.v, j))
                else:
                    m[i + 1][j] = max(m[i][j], m[i][j - obj.w] + obj.v)

        # Set temporary problem solution (probably needs shift)
        self._problem_solution = m[len(self._objects)][self._W]

        # Set solution path
        W = self._W
        i = len(self._objects) - 1
        previous_value = self._problem_solution
        self._problem_solution_path = []
        while W > 0 and i >= 0:
            current_value = m[i][W]
            # If result different then item in knapsack, modify W
            if current_value != previous_value:
                obj = self._objects[i]
                W = W - obj.w

                # If W < 0 then it is a cut object! If current value is not the object value, a shift is needed!
                # The shift is greater if it's the maximal object
                if W < 0 and current_value != obj.v: # If equal, then cut in computation phase
                    object_value = obj.v
                    self._shift = object_value - previous_value

                if W > 0:
                    previous_value = m[i][W]
    
                self._problem_solution_path.append(obj)
            i -= 1
        
        # We know that items are sorted by decreasing value, so before last item is the greatest non cut item
        # If shift greater than value of second last item value, then we add to the solution, else 0
        # If there is more than one task in the knapsack of course
        if len(self._problem_solution_path) > 1:
            self._problem_solution += max(0, self._shift - self._problem_solution_path[-2].v)


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


def solve_problem(problem: knapsack_problem) -> int:
    problem.solve()
    return problem.get_solution()


def get_knapsack_inter_processor_interference(system: PREM_system, cpu_prio: int, delta: int, task: PREM_task) -> int:
    # If delta is 0, no memory interference since no memory time
    if delta == 0:
        return 0

    # Prepare the problem
    problem = prepare_knapsack_problem(system=system, cpu_prio=cpu_prio, delta=delta)

    # Solve the problem
    problem.solve()
        
    # Return the problem solution
    return problem.get_solution()