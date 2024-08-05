# This is written in Python2.7 for Python2.7! 
# It will generate a file called "schedcat_log.log" that will contain informations about generated tasks
# Informations are wcet and period/deadline

# Imports (schedcat!)
from schedcat.generator.generator_emstada import gen_taskset
import sys

# Constants
taskset_file = './schedcat_log.log'

# Functions
def main():    
    # First argument is period_min
    period_min = int(sys.argv[1])
    
    # Second argument is period_max
    period_max = int(sys.argv[2])
    
    # Third argument is period_distribution
    period_distribution = sys.argv[3]
    
    # Fourth argument is num_task
    num_task = int(sys.argv[4])
    
    # Fifth argument is utilisation
    utilisation = float(sys.argv[5])

    # Generate task set
    taskset = gen_taskset(periods=(period_min, period_max),
                          period_distribution=period_distribution, 
                          tasks_n=num_task, 
                          utilization=utilisation)
    
    # Write taskset in file
    file = open(taskset_file, "w")
    for task in taskset:
        file.write(str(task.cost) + ',')
        file.write(str(task.period) + '\n')
    

if __name__ == '__main__':
    main()