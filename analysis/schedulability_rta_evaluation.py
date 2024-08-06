# Imports 
from utils.generate_prem import interval, generate_prem_systems
from utils.rta_prem import is_system_schedulable_per_processor

# Constants
system_number = 1
utilisation = 0.6


# Functions
def main():
    # Tests from Fixed-Priority Memory-Centric scheduler for COTS based multiprocessor (Gero Schwäricke) p. 17 
    # Generate tests with period between 10 and 100 ms, log uniform, memory stal between 0.05 and 0.20, scheduled with
    # Rate Monotonic. There is 10000 task sets generated with utilisation 0.6, and 4, 8, 16 processors. There are 8 tasks
    # per processor.
    
    # Generate systems
    prem_systems = generate_prem_systems(system_number=system_number, 
                          processor_number=4, 
                          task_numbers=[8] * 4, 
                          period_intervals=[interval(10, 100)] * 4,
                          period_distributions=['logunif']*4,
                          utilisation=utilisation, 
                          bandwidth_utilisation_interval=interval(5, 20))
    
    for system in prem_systems:
        print(system)
        
    print('Is system schedulable?')
    system_index = 0
    for system in prem_systems:
        are_schedulable = is_system_schedulable_per_processor(system=system)
        system_schedulable = True
        for answer in are_schedulable:
            system_schedulable &= answer
        
        print(f'System {system_index:d}: {system_schedulable.__str__():s}')
        cpu = 0
        for answer in are_schedulable:
            print(f'\tP{cpu:d}: {answer.__str__():s}')
            cpu += 1
        
        system_index += 1
        print()
        

if __name__ == '__main__':
    main()