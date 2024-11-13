# Imports 
from __future__ import annotations # For > 3.10 compatibility
from math import ceil, floor
from utils.prem_utils import *


# Functions
def stall(cpu_number: int, M_hat: int, C_hat: int, budget: int, budget_period: int) -> int:
    if (budget / budget_period) < (1 / cpu_number):
        if (M_hat % budget) == 0:
            stall = int(M_hat / budget) * (budget_period - budget) + (cpu_number - 1) * budget
        else:
            stall = ceil(M_hat / budget) * (budget_period - budget) + (cpu_number - 1) * (M_hat % budget)
    else:
        b = budget / budget_period
        if (M_hat / (M_hat + C_hat)) <= ((1 - b) / (b * (cpu_number - 1))):
            stall = (budget_period - budget) + M_hat * (cpu_number - 1)
        else:
            RBS = (budget_period - budget) / (cpu_number - 1)
            K = floor(C_hat / (budget - RBS))
            
            if (M_hat + C_hat) < (1 + K) * budget:
                r = min(budget_period - budget, int((cpu_number - 1) * (M_hat - (K * RBS))))
                stall = (1 + K) * (budget_period - budget) + r
            else:
                r = min(budget_period - budget, (cpu_number - 1) * ((M_hat + C_hat) % budget))
                stall = (1 + floor((M_hat + C_hat) / budget)) * (budget_period - budget) + r
            
    return stall


def compute_synthesized_task(R_hat: int, higher_equal_tasks: list[PREM_task]) -> tuple[int, int]:
    M_hat = sum(ceil(R_hat / htask.T) * htask.M for htask in higher_equal_tasks)
    C_hat = sum(ceil(R_hat / htask.T) * htask.C for htask in higher_equal_tasks)
    
    return (M_hat, C_hat)


def get_stalled_response_time(cpu_number: int, R0: int, task: PREM_task, higher_tasks: list[PREM_task], higher_equal_tasks: list[PREM_task], budget: int, budget_period: int) -> int:
    R_hat = R0
    previous_R_hat = 0
    
    # If the equation diverges, then set to -1
    try:
        while previous_R_hat != R_hat:
            previous_R_hat = R_hat
            (M_hat, C_hat) = compute_synthesized_task(R_hat=previous_R_hat, higher_equal_tasks=higher_equal_tasks)
            R_hat = task.e + sum([ceil(previous_R_hat / htask.T) * htask.e for htask in higher_tasks]) + stall(cpu_number, M_hat, C_hat, budget, budget_period)
            
            # If the response time is greater than 1000 times the deadline, we say that it does not converge
            if R_hat != previous_R_hat and R_hat > 1000 * task.D:
                R_hat = -1
                break
    except:
        R_hat = -1
        
    return R_hat


def get_response_time_task(task: PREM_task, higher_tasks: list[PREM_task]) -> int:
    R = task.e
    previous_R = 0
    while previous_R != R:
        previous_R = R
        R = task.e + sum([ceil(previous_R / htask.T) * htask.e for htask in higher_tasks])
    return R


def get_response_time(cpu_number: int, cpu_prio: int, Px: processor, task: PREM_task, budgets: list[int], budget_period: int) -> int:
    R = get_response_time_task(task=task, higher_tasks=Px.higher_tasks(task.prio))
    R_hat = get_stalled_response_time(cpu_number=cpu_number,
                                      R0=R,
                                      task=task,
                                      higher_tasks=Px.higher_tasks(task.prio),
                                      higher_equal_tasks=Px.higher_tasks(task.prio + 1),
                                      budget=budgets[cpu_prio],
                                      budget_period=budget_period)
    
    task.R = R_hat    
    return R_hat


def get_response_time_system(system: PREM_system, budgets: list[int], budget_period: int) -> list[list[int]]:
    processors = system.processors()
    response_time_system = []
    cpu_number = len(processors)

    for cpu_prio in range(0, cpu_number):
        response_time_processor = []
        Px = processors[cpu_prio]
        
        for task in Px.tasks():
            response_time = get_response_time(cpu_number=cpu_number, cpu_prio=cpu_prio, Px=Px, task=task, budgets=budgets, budget_period=budget_period)
            response_time_processor.append(response_time)
        
        response_time_system.append(response_time_processor)
    
    system.system_analysed = True
    return response_time_system
