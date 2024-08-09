# This is written in Python2.7 for Python2.7! 
# It will generate a file called "schedcat_log.log" that will contain informations about generated tasks
# Informations are wcet and period/deadline

# Imports (schedcat!)
from schedcat.generator.generator_emstada import gen_taskset
import sys

# Constants
taskset_file = './utils/schedcat_log.log'

# Functions
def times_ten(ms):
    return ms*10


def times_hundred(ms):
    return ms*100


def main():
    # First argument is the number of sets to generate
    taskset_number = int(sys.argv[1])
    
    # Second argument is period_min
    period_min = int(sys.argv[2])
    
    # Third argument is period_max
    period_max = int(sys.argv[3])
    
    # Fourth argument is period_distribution
    period_distribution = sys.argv[4]
    
    # Fifth argument is num_task
    num_task = int(sys.argv[5])
    
    # Sixth argument is utilisation
    utilisation = float(sys.argv[6])
    
    if utilisation < 0.3:
        scale = times_hundred
    else:
        scale = times_ten

    taskset = []
    # Generate task sets
    for _ in range(0, taskset_number):
        cost = 0        
        while cost < 10:
            tmp_task = gen_taskset(periods=(period_min, period_max),
                               period_distribution=period_distribution, 
                               tasks_n=num_task, 
                               utilization=utilisation,
                               scale=scale)
            
            cost = tmp_task.min_cost()
        
        taskset += tmp_task
    
    # Write taskset in file
    file = open(taskset_file, "w")
    for task in taskset:
        file.write(str(task.cost) + ',')
        file.write(str(task.period) + '\n')
    

if __name__ == '__main__':
    main()