# Everything that can be useful to PREM will be in here!

# Represents the PREM object
class PREM_task:
    def __init__(self, M: int, C: int, T: int, D: int = -1, prio: int = -1) -> None:
        # Add tests to see if values are greater than 0?
        self.M = M # Memory phase
        self.C = C # Computation phase
        self.T = T # Period
        if D <= 0:
            self.D = self.T
        else:
            self.D = D        

        self.e = M + C # Execution time
        self.prio = prio # Priority
        self.R = -1 # Response time


    def set_response_time(self, response_time: int) -> None:
        self.R = response_time


    def is_schedulable(self) -> bool:
        return self.R != -1 and self.R <= self.D
    

    def __str__(self) -> str:
        return f'M={self.M:d},C={self.C:d},T={self.T:d},prio={self.prio:d}'
    

# Represents a CPU
class processor:
    # Class attributes
    M_max = -1
    C_min = -1
    max_interference = -1
    global_task = PREM_task(M=-1, C=-1, T=-1)
    

    # Inits the processor with a task list (or not) 
    def __init__(self, tasks: list[PREM_task] = []) -> None:
        self._tasks = []
        for task in tasks:
            self._tasks.append(task)
            
            # Keep the max value to fasten things
            if task.M > self.M_max:
                self.M_max = task.M
            
            # Keep the min computation value to fasten things
            if self.C_min == -1 or self.C_min > task.C:
                self.C_min = task.C

    
    # Adds a task to the processor
    def add_task(self, task: PREM_task) -> None:
        self._tasks.append(task)
        if task.M > self.M_max:
            self.M_max = task.M
            
        if self.C_min == -1 or self.C_min > task.C:
            self.C_min = task.C
            
    
    # Sets the global task for this processor (only used when useing global tasks)
    def set_global_task(self, T: int) -> None:
        self.global_task = PREM_task(M=self.M_max, C=self.C_min, T=T)

    
    # Gets the saved global task
    def get_global_task(self) -> PREM_task:
        return self.global_task
    
    
    # Returns the tasks with higher priority
    def higher_tasks(self, prio: int) -> list[PREM_task]:
        return [task for task in self._tasks if task.prio < prio]
    

    # Returns the tasks with lower priority
    def lower_tasks(self, prio: int) -> list[PREM_task]:
        return [task for task in self._tasks if task.prio > prio]


    # Returns the task set of the CPU
    def tasks(self) -> list[PREM_task]:
        return self._tasks
    

    # Returns the lowest prio of that CPU
    def get_lowest_prio(self) -> int:
        return max([task.prio for task in self._tasks])
    

    # Returns true if the priority is the lowest priority
    def is_lowest_prio(self, prio: int) -> bool:
        return prio == self.get_lowest_prio()
    
    
    # Returns the memory utilisation of all tasks in the processor
    def get_memory_utilisation(self) -> float:
        utilisation = 0
        for task in self._tasks:
            utilisation += task.M / task.T
            
        return utilisation
    
    
    # Returns the utilisation of all tasks in the processor
    def get_utilisation(self) -> float:
        utilisation = 0
        for task in self._tasks:
            utilisation += task.e / task.T
            
        return utilisation

    
    # Returns the number of tasks in the processor
    def length(self) -> int:
        return len(self._tasks)
    

    # Resets the processor and all its tasks
    def reset(self) -> None:
        # Reset persistant values
        self.max_interference = -1
        self.global_task = PREM_task(M=-1, C=-1, T=-1)
        
        # Reset tasks' priority and response time
        for task in self._tasks:
            task.prio = -1
            task.R = -1

    
    def __str__(self) -> str:
        string_result = ''
        for task in self._tasks:
            string_result += f'({task.__str__():s}),'
        
        return f'[{string_result:s}]'
    
    
# Represents a PREM system, that means CPU with tasks
class PREM_system:
    # Variable to remember if tasks were analysed
    system_analysed = False
    
    # Inits the system with a CPU list (or not)
    # The first CPU to enter has higher priority 
    def __init__(self, processors: list[processor] = []) -> None:
        self._processors = [cpu for cpu in processors]
        
    
    # Adds a processor
    def add_processor(self, cpu: processor) -> None:
        self._processors.append(cpu)
     
        
    # Returns processors in the system
    def processors(self) -> list[processor]:
        return self._processors    
    
    
    # Returns all CPU that has a lower priority than the argument
    def lower_processors(self, prio: int) -> list[processor]:
        return self._processors[prio + 1:]
    
    
    # Returns all CPU that has a higher priority than the argument
    def higher_processors(self, prio: int) -> list[processor]:
        return self._processors[:prio]
    
    
    # Returns the number of processors in the system
    def length(self) -> int:
        return len(self._processors)
    
    
    # Resets the system
    def reset(self) -> None:
        self.system_analysed = False
        for Px in self._processors:
            Px.reset()


    def __str__(self) -> str:
        string_result = ''
        index = 0
        for cpu in self._processors:
            string_result += f'P{index:d}: {cpu.__str__():s},\n'
            index += 1
        
        return f'{string_result:s}'