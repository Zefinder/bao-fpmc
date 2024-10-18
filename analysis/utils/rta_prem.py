# Imports
from __future__ import annotations
from math import ceil, floor
from utils.prem_utils import *
from utils.fixed_priority_sched import *
from utils.prem_inter_processor_interference import inter_processor_interference_mode, get_classic_inter_processor_interference

# Functions
# ----------------------------------------------------
# -------------- Intermediate functions --------------
# ----------------------------------------------------
def get_blocking_time(Px: processor, prio: int) -> int:
    """
    Computes the blocking time for a specified priority. Also called B<sub>prio</sub>.
    
    Args:
        Px (processor): Processor on which the task to analyse is
        prio (int): Task priority
        
    Returns:
        int: Blocking time  
    """
    
    lower_priority_executions = [ltask.e for ltask in Px.lower_tasks(prio)]
    return max(lower_priority_executions) if lower_priority_executions else 0


def get_intra_processor_interference(Px: processor, delta: int, prio: int) -> int:
    """
    Computes the intra-processor interference for a specified priority. Also called I<sub>prio</sub>(Δ).
    
    Args:
        Px (processor): Processor on which the task to analyse is
        delta (int): Task execution time
        prio (int): Task priority
        
    Returns:
        int: Intra-processor interference  
    """
    higher_priority_interference = [ceil(delta / htask.T) * htask.e for htask in Px.higher_tasks(prio)]
    return sum(higher_priority_interference) if higher_priority_interference else 0


def get_number_memory_phase(Px: processor, task: PREM_task, delta: int) -> int:
    """
    Computes the number of memory phases released on a processor during the busy period of a task with length
    Δ > 0, such that there is a pending instance of that task. Also called N<sub>task</sub>(Δ).
    
    Args:
        Px (processor): Processor on which the task to analyse is
        task (PREM_task): Task to analyse 
        delta (int): Length of the busy period of the task
        
    Returns:
        int: Number of memory phases released
    """
    return sum([ceil(delta / htask.T) for htask in Px.higher_tasks(task.prio)]) + floor(delta / task.T) + (1 if not Px.is_lowest_prio(task.prio) else 0)
    

def get_max_interference(system: PREM_system, interference_mode: inter_processor_interference_mode, cpu_prio: int, Px: processor) -> int:
    """
    Computes the maximum interference that can affect a processor. It is described by a recurrent equation. 
    Also called ε<sub>P</sub>.

    Args:
        system (PREM_system): System to analyse
        interference_mode (inter_processor_interference_mode): Inter-processor interference chosen mode
        cpu_prio (int): Priority of the processor to analyse
        Px (processor): Processor to analyse

    Returns:
        int: Value of the maximum interference
    """
    # This is a value that doesn't change, so saved in the processor if already computed
    if Px.max_interference != -1:
        return Px.max_interference
    
    # Else we have eps = alpha(eps + M_max)
    # The base value of the recurrent equation is the greatest memory phase
    max_interference = Px.M_max
    prev_max_interference = -1
    while prev_max_interference != max_interference:
        prev_max_interference = max_interference
        max_interference = interference_mode.get_inter_processor_interference(system=system, cpu_prio=cpu_prio, delta=max_interference + Px.M_max, task=PREM_task(M=0, C=0, T=1))
        # If a problem occurs in max interference, return -1 (computed in busy period check)
        if max_interference == -1:
            return -1

    # Save the value 
    Px.max_interference = max_interference

    interference_mode.reset_count()
    return max_interference


def get_total_memory_interference(system: PREM_system, interference_mode: inter_processor_interference_mode, cpu_prio: int, Px: processor, task: PREM_task, delta: int) -> int:
    """
    Comutes the total memory interference during the busy period of a task with length Δ > 0. Also called 
    β<sub>task</sub>(Δ).

    Args:
        system (PREM_system): System to analyse
        interference_mode (inter_processor_interference_mode): Inter-processor interference chosen mode
        cpu_prio (int): Priority of the processor to analyse
        Px (processor): Processor to analyse
        task (PREM_task): Task to analyse
        delta (int): Length of the busy period of the task

    Returns:
        int: The total memory interference
    """
    return get_number_memory_phase(Px=Px, task=task, delta=delta) * get_max_interference(system=system, cpu_prio=cpu_prio, Px=Px, interference_mode=interference_mode)


def get_memory_phase_start_time(system: PREM_system, interference_mode: inter_processor_interference_mode, cpu_prio: int, Px: processor, task: PREM_task, k: int) -> int:
    """
    The latest start time of the memory phase of the k-th instance of the task. It is represented by a recurrent
    equation. Also called s<sup>mem</sup><sub>task, k</sub>.

    Args:
        system (PREM_system): System to analyse
        interference_mode (inter_processor_interference_mode): Inter-processor interference chosen mode
        cpu_prio (int): Priority of the processor to analyse
        Px (processor): Processor to analyse
        task (PREM_task): Task to analyse
        k (int): Instance of the task

    Returns:
        int: Latest memory phase start time for the k-th instance of the task
    """
    # This is a recurrent equation where the initial start time is the blocking time B + all tasks that can all start before it
    B = get_blocking_time(Px=Px, prio=task.prio)
    
    # Base values
    memory_start_time = B + sum(htask.e for htask in Px.higher_tasks(task.prio)) + (k - 1) * task.e
    prev_start_time = -1
    
    # As long as the solution is not stable, we repeat
    while prev_start_time != memory_start_time:
        prev_start_time = memory_start_time

        intra_processor_interference = get_intra_processor_interference(Px=Px, 
                                                                        delta=memory_start_time, 
                                                                        prio=task.prio)
        
        interference_alpha = interference_mode.get_inter_processor_interference(system=system,
                                                                                cpu_prio=cpu_prio, 
                                                                                delta=memory_start_time,
                                                                                task=task)
        interference_beta = get_total_memory_interference(system=system, 
                                                          interference_mode=interference_mode,
                                                          cpu_prio=cpu_prio,
                                                          Px=Px, 
                                                          task=task,
                                                          delta=memory_start_time)

        inter_processor_interference = min(interference_alpha, interference_beta)

        # If inter-processor interference returned -1, then it means that it can't be determined with this policy (e.g. no stable solution)
        if inter_processor_interference == -1:
            return -1

        memory_start_time = B + intra_processor_interference + (k - 1) * task.e + inter_processor_interference
    
    interference_mode.reset_count()
    return memory_start_time


def get_computation_phase_start_time(system: PREM_system, interference_mode: inter_processor_interference_mode, cpu_prio: int, Px: processor, task: PREM_task, k: int) -> int:
    """
    Latest start time of the computation phase of the k-th instance of the task. It is represented by a recurrent 
    equation. Also called s<sub>cmp</sup><sub>task, k</sub>.

    Args:
        system (PREM_system): System to analyse
        interference_mode (inter_processor_interference_mode): Inter-processor interference chosen mode
        cpu_prio (int): Priority of the processor to analyse
        Px (processor): Processor to analyse
        task (PREM_task): Task to analyse 
        k (int): Instance of the task

    Returns:
        int: Latest computation phase start time for the k-th instance of the task
    """
    # First step is to get the memory phase start time
    memory_start_time = get_memory_phase_start_time(system=system, interference_mode=interference_mode, cpu_prio=cpu_prio, Px=Px, task=task, k=k)

    if memory_start_time == -1:
        return -1
    
    # Save blocking time to go faster
    B = get_blocking_time(Px=Px, prio=task.prio)
    
    # Same for intra-processor interference since memory start is a constant now
    I = get_intra_processor_interference(Px=Px, delta=memory_start_time, prio=task.prio)
    
    # Same total memory interference (beta)
    interference_beta = get_total_memory_interference(system=system, interference_mode=interference_mode, cpu_prio=cpu_prio, Px=Px, task=task, delta=memory_start_time)
    
    # Constant part that does not change
    constant_blocking = B + I + task.M + (k - 1) * task.e
    
    # Base values (start memory plus memory phase)
    computation_start_time = task.M + memory_start_time
    prev_start_time = -1

    # As long as the solution is not stable we repeat
    while prev_start_time != computation_start_time:
        prev_start_time = computation_start_time

        interference_alpha1 = interference_mode.get_inter_processor_interference(system=system, 
                                                                                 cpu_prio=cpu_prio, 
                                                                                 delta=computation_start_time,
                                                                                 task=task)
        
        interference_alpha2 = interference_mode.get_inter_processor_interference(system=system, 
                                                                                 cpu_prio=cpu_prio, 
                                                                                 delta=computation_start_time - memory_start_time,
                                                                                 task=task)
        
        
        # If one of them returns -1, it means that no solution have been found
        if interference_alpha1 == -1 or interference_alpha2 == -1:
            return -1

        computation_start_time = constant_blocking + min(interference_alpha1, interference_beta + interference_alpha2)
    
    interference_mode.reset_count()
    return computation_start_time


def is_busy_period_equation_convergent(system: PREM_system, interference_mode: inter_processor_interference_mode, Px: processor, cpu_prio: int) -> bool:
    """
    Checks whether the recurrent equation to compute the longest busy period of the task converges.

    Args:
        system (PREM_system): System to analyse
        interference_mode (inter_processor_interference_mode): Inter-processor interference chosen mode
        Px (processor): Processor to analyse
        cpu_prio (int): Priority of the processor to analyse

    Returns:
        bool: True if the equation converges, else False
    """
    # Compute max interference
    max_interference = get_max_interference(system=system, interference_mode=interference_mode, cpu_prio=cpu_prio, Px=Px)
    if max_interference == -1:
        return False
    
    higher_cpu_memory_utilisation = sum([Ph.get_memory_utilisation() for Ph in system.higher_processors(prio=cpu_prio)])
    max_interference_on_period = sum([max_interference / task.T for task in Px.tasks()])
    
    return Px.get_utilisation() + min(higher_cpu_memory_utilisation, max_interference_on_period) < 1


def get_longest_busy_period(system: PREM_system, interference_mode: inter_processor_interference_mode, cpu_prio: int, Px: processor, task: PREM_task) -> int:
    """
    Computes the longest busy period of the task that can be executed by its processor. It is represented by a
    recurrent equation. Also called L<sub>task</sub>.

    Args:
        system (PREM_system): System to analyse
        interference_mode (inter_processor_interference_mode): Inter-processor interference chosen mode
        cpu_prio (int): Priority of the processor to analyse
        Px (processor): Processor to analyse
        task (PREM_task): Task to analyse

    Returns:
        int: The longest byusy-period of the task
    """
    # If equation not converging... What do we do? Not schedulable? 
    # TODO Move to response time per cpu since the converging test is for the processor
    if not is_busy_period_equation_convergent(system=system, interference_mode=interference_mode, Px=Px, cpu_prio=cpu_prio):
        return -1
    
    # Once again it is a recurrent equation... start point is the blocking time B + all tasks that can all start before it + itself
    # Save blocking time to go faster
    B = get_blocking_time(Px=Px, prio=task.prio)
    
    # Base values
    busy_period = B + sum(htask.e for htask in Px.higher_tasks(task.prio)) + task.e
    prev_busy_period = -1
        
    # As long as the solution is not stable we repeat
    while prev_busy_period != busy_period:
        prev_busy_period = busy_period

        intra_processor_interference = get_intra_processor_interference(Px=Px,
                                                                        delta=busy_period, 
                                                                        prio=task.prio + 1)

        # We take into account this task, so we do as if we computed the interference for a lower priority task
        interference_alpha = interference_mode.get_inter_processor_interference(system=system,
                                                                                cpu_prio=cpu_prio,
                                                                                delta=busy_period,
                                                                                task=task)
        interference_beta = get_total_memory_interference(system=system,
                                                          interference_mode=interference_mode,
                                                          cpu_prio=cpu_prio,
                                                          Px=Px,
                                                          task=task,
                                                          delta=busy_period)
 
        inter_processor_interference = min(interference_alpha, interference_beta + Px.M_max)

        # If it returns -1, then so solution found at all so unlimited busy period
        if inter_processor_interference == -1:
            return -1

        busy_period = B + intra_processor_interference + inter_processor_interference
    
    interference_mode.reset_count()

    return busy_period


def get_response_time_k_occurence(system: PREM_system, interference_mode: inter_processor_interference_mode, cpu_prio: int, Px: processor, task: PREM_task, k: int) -> int:
    """
    Computes the response time for the k-th instance of the task. Also called R<sub>task, k</sub>.

    Args:
        system (PREM_system): System to analyse
        interference_mode (inter_processor_interference_mode): Inter-processor interference chosen mode
        cpu_prio (int): Priority of the processor to analyse
        Px (processor): Processor to analyse
        task (PREM_task): Task to analyse
        k (int): Instance of the task

    Returns:
        int: The response time of the k-th instance of the task
    """
    # R_i,k = cmp_start + C - (k - 1).T
    computation_start_time = get_computation_phase_start_time(system=system, interference_mode=interference_mode, cpu_prio=cpu_prio, Px=Px, task=task, k = k)
    return computation_start_time + task.C - (k - 1) * task.T


# ----------------------------------------------------
# ----------------- Usable functions -----------------
# ----------------------------------------------------
def get_response_time(system: PREM_system, interference_mode: inter_processor_interference_mode, cpu_prio: int, Px: processor, task: PREM_task) -> int:
    """
    Computes the response time of the task. It will compute the longest busy period and check for 
    all instances of the task during its busy period. Also called R<sub>task</sub>.

    Args:
        system (PREM_system): System to analyse
        interference_mode (inter_processor_interference_mode): Inter-processor interference chosen mode
        cpu_prio (int): Priority of the processor to analyse
        Px (processor): Processor to analyse
        task (PREM_task): Task to analyse

    Returns:
        int: The response time of the task
    """
    # It is the max of the kth response time, k between 1 and ceil(L/T)
    busy_period = get_longest_busy_period(system=system, interference_mode=interference_mode, cpu_prio=cpu_prio, Px=Px, task=task)
    # If busy period non workable, notify that it is not possible
    if busy_period == -1:
        return -1
    
    response_time = 0

    for k in range(1, ceil(busy_period / task.T) + 1):
        new_response_time = get_response_time_k_occurence(system=system, interference_mode=interference_mode, cpu_prio=cpu_prio, Px=Px, task=task, k=k)
        if (response_time < new_response_time):
            response_time = new_response_time
    
    # Also adds the response time to the task to save its value
    task.R = response_time
    
    return response_time


def get_response_time_system(system: PREM_system, interference_mode: inter_processor_interference_mode = inter_processor_interference_mode(get_classic_inter_processor_interference)) -> list[list[int]]:
    """
    Computes the response time of the system.

    Args:
        system (PREM_system): System to analyse
        interference_mode (inter_processor_interference_mode, optional): Inter-processor interference chosen mode. Defaults to inter_processor_interference_mode(get_classic_inter_processor_interference).

    Returns:
        list[list[int]]: Response time of processors all gathered in a list
    """
    # Get processors from system
    processors = system.processors()
    response_time_system = []

    for cpu_prio in range(0, len(processors)):
        response_time_processor = []
        Px = processors[cpu_prio]
        
        for task in Px.tasks():
            response_time = get_response_time(system=system, interference_mode=interference_mode, cpu_prio=cpu_prio, Px=Px, task=task)
            # If response time is invalid, then return empty
            if response_time == -1:
                return []
            
            response_time_processor.append(response_time)
        
        response_time_system.append(response_time_processor)
    
    system.system_analysed = True
    return response_time_system


# Returns if system schedulable per processor
def is_system_schedulable_per_processor(system: PREM_system, interference_mode: inter_processor_interference_mode = inter_processor_interference_mode(get_classic_inter_processor_interference)) -> list[bool]:
    """
    Checks whether the system is schedulable per procesor

    Args:
        system (PREM_system): System to analyse
        interference_mode (inter_processor_interference_mode, optional): Inter-processor interference chosen mode. Defaults to inter_processor_interference_mode(get_classic_inter_processor_interference).

    Returns:
        list[bool]: Schedulability per processor (True if processor is schedulable else False)
    """
    if not system.system_analysed:
        get_response_time_system(system=system, interference_mode=interference_mode)
    
    processors = system.processors()
    schedulability = []
    for cpu_prio in range(0, len(processors)):
        Px = processors[cpu_prio]
        schedulable = True
        for task in Px.tasks():
            schedulable &= task.is_schedulable()
        
        schedulability.append(schedulable)
    
    return schedulability
