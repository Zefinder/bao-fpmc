from utils.generate_prem import interval, generate_prem_system
from utils.fixed_priority_sched import set_system_priority, rate_monotonic_scheduler
from memguard.rta import get_response_time_system

processor_number = 4
task_number = 4
period_interval = interval(5000, 10000)
period_distribution = 'logunif'
utilisation = 0.6
bandwidth_utilisation_interval = interval(5, 20)
scale = lambda x: x


def main():
    # Generate 10 systems and analyse them
    # Core budget will be the max core's M
    # Refill period will be the biggest computation phase
    system_number = 10
    for index in range(0, system_number):
        system = generate_prem_system(processor_number=processor_number,
                                      task_number=task_number,
                                      period_interval=period_interval,
                                      period_distribution=period_distribution,
                                      utilisation=utilisation,
                                      bandwidth_utilisation_interval=bandwidth_utilisation_interval,
                                      scale=scale,
                                      min_cost=20)
        
        budgets = [Px.M_max for Px in system.processors()]
        budget_period = max([Px.C_max for Px in system.processors()])
        
        set_system_priority(system=system, fp_scheduler=rate_monotonic_scheduler)
        response_times = get_response_time_system(system=system, budgets=budgets, budget_period=budget_period)
        
        # Display results
        print(f'System {index:d}: {response_times}')
        for cpu_index in range(0, processor_number):
            Px = system.processors()[cpu_index]
            print(f'\tP{cpu_index} ->', 'schedulable' if Px.is_schedulable() else 'not schedulable')
            for task_index in range(0, len(Px.tasks())):
                task = Px.tasks()[task_index]
                print(f'\t\ttask {task_index:d} (D={task.D}, R={task.R}) ->', 'schedulable' if task.is_schedulable() else 'not schedulable')
            


if __name__ == '__main__':
    main()