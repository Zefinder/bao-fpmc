# This is a util file to generate logs to be analysed
# It also provides the tools to read logs and to parse them
# A log file will contain a lot of information: 
# - System's utilisation
# - CPU number
# - Task number for CPU i
# - Memory phase, Computation phase, Period, Response time for task j on CPU i

# Imports 
from __future__ import annotations
from io import TextIOWrapper
import os
from utils.prem_utils import *
import multiprocessing
from multiprocessing.synchronize import Lock

# Constants
log_dir = './results/'

# Classes
class log_results():
    _log_file: TextIOWrapper

    
    def __init__(self, log_name: str) -> None:
        if (not os.path.isfile(log_dir + log_name)):        
            raise Exception(f"Log file doesn't exist: {log_name:s}")
        
        # Keep the file open to read it when asked...
        self._log_file = open(log_dir + log_name, 'r')
    
    
    def read_system_entry(self) -> PREM_system:
        # Read line with lock to be sure nothing is writing
        line = self._log_file.readline()
            
        if not line: 
            # Close file and return an empty system if no more lines
            self._log_file.close()
            return PREM_system()
        
        system_components = line.strip().split(',')
        
        # Get system utilisation
        utilisation = float(system_components[0])
        
        # Get CPU number
        cpu_number = int(system_components[1])
        
        # Get number of tasks per CPU
        task_number_per_cpu = []
        for index in range(2, cpu_number + 2):
            task_number_per_cpu.append(int(system_components[index]))

        # Create each processor object and add it to the system
        offset = 2 + cpu_number
        system = PREM_system(utilisation=utilisation)
        for task_number in task_number_per_cpu:
            Px = processor()
            for _ in range(0, task_number):
                task = PREM_task(M=int(system_components[offset]), C=int(system_components[offset + 1]), T=int(system_components[offset + 2]))
                task.R = int(system_components[offset + 3])
                offset += 4
                Px.add_task(task=task)
            system.add_processor(cpu=Px)
            
        return system
    
    
    def read_line(self) -> str:
        return self._log_file.readline()
    

    def close(self) -> None:
        self._log_file.close()


class log_file_class():
    _log_file: TextIOWrapper
    write_lock: Lock = multiprocessing.Lock()
    
    def __init__(self) -> None:
        # Create the result dir if doesn't exist
        if (not os.path.isdir(log_dir)):        
            os.mkdir(log_dir)
    
    
    # Creates a new log file 
    def create(self, log_name: str) -> None:
        self._log_file = open(log_dir + log_name, 'w')


    def resume_log(self, log_name: str) -> None:
        self._log_file = open(log_dir + log_name, 'a')
        
        
    def create_result_file(self, log_name: str) -> log_results:
        results = log_results(log_name=log_name)
        return results
        
        
    # Writes to the log file
    def write_system(self, system: PREM_system) -> None:
        log_line = []
        
        log_line.append(system.utilisation())

        # CPU number
        log_line.append(system.length())

        # Task number per CPU
        log_line += [Px.length() for Px in system.processors()]

        # For each task in each CPU, response time and schedulable
        for Px in system.processors():
            for task in Px.tasks():
                log_line.append(task.M)
                log_line.append(task.C)
                log_line.append(task.T)
                log_line.append(task.R)

        # Write log line (Thread-safe)
        with self.write_lock:
            self._log_file.write(', '.join(str(element) for element in log_line) + '\n')
            self._log_file.flush()
            
    
    # Will end the line with '\n'
    def write(self, line: str) -> None:
        with self.write_lock:
            self._log_file.write(line + '\n')
            self._log_file.flush()
    

    # Closes the log file
    def close(self) -> None:
        self._log_file.close()


