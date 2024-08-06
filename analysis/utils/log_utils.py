# This is a util file to generate logs to be analysed
# It also provides the tools to read logs and to parse them
# A log file will contain a lot of information: 
# - CPU number
# - Task number for CPU i
# - Response time for task j on CPU i and if schedulable (int representation of boolean)
# For example, 2 CPUs and 2 tasks per CPU will give the following log:
# 2, 2, 2, 20, 1, 34, 1, 50, 1, 83, 0

# Imports 
from io import TextIOWrapper
import os
from utils.prem_utils import *

# Constants
log_dir = './results/'

# Classes
class log_file_class():
    log_file: TextIOWrapper
    
    
    def __init__(self) -> None:
        # Create the result dir if doesn't exist
        if (not os.path.isdir(log_dir)):        
            os.mkdir(log_dir)
    
    
    # Creates a new log file 
    def create(self, log_name: str) -> None:
        self.log_file = open(log_dir + log_name, 'w')
        
        
    # Writes to the log file
    def write(self, system: PREM_system) -> None:
        log_line = []

        # CPU number
        log_line.append(system.length())

        # Task number per CPU
        log_line += [Px.length() for Px in system.processors()]

        # For each task in each CPU, response time and schedulable
        for Px in system.processors():
            for task in Px.tasks():
                log_line.append(task.R)
                log_line.append(int(task.is_schedulable()))

        # Write string representation of array but without []
        self.log_file.write(log_line.__str__()[1:-1] + '\n')
    

    # Closes the log file
    def close(self) -> None:
        self.log_file.close()


class log_results():
    pass


