# Everything that can be useful to PREM will be in here!

# Represents the PREM object
class PREM_task:
  def __init__(self, M: int, C: int, T: int, D: int = -1, prio: int = 0) -> None:
    # Add tests to see if values are greater than 0
    self.M = M # Memory phase
    self.C = C # Computation phase
    self.T = T # Period
    if D <= 0:
        self.D = self.T
    else:
        self.D = D        
    
    self.e = M + C # Execution time
    self.prio = prio # Priority
    self.R = 0 # Response time


  def set_response_time(self, response_time: int) -> None:
    self.R = response_time


  def __str__(self) -> str:
    return f'M={self.M:d},C={self.C:d},T={self.T:d},prio={self.prio:d}'
    

# Represents a CPU
class processor:
    # Inits the processor with a task list (or not) 
    def __init__(self, tasks: list[PREM_task] = []) -> None:
        self._tasks = [task for task in tasks]
        
        
    def add_task(self, task: PREM_task) -> None:
        self._tasks.append(task)
        
    
    def tasks(self) -> list[PREM_task]:
        return self._tasks
    
    def __str__(self) -> str:
        string_result = ''
        for task in self._tasks:
            string_result += f'({task.__str__():s}),'
        
        return f'[{string_result:s}]'
    
    
# Represents a PREM system, that means CPU with tasks
class PREM_system:
    # Inits the system with a CPU list (or not)
    # The first CPU to enter has higher priority 
    def __init__(self, processors: list[processor] = []) -> None:
        self._processor = [cpu for cpu in processors]
        
    
    def add_processor(self, cpu: processor) -> None:
        self._processor.append(cpu)
        
    
    # Returns all CPU that has a lower priority than the argument
    def lower_processors(self, prio: int) -> list[processor]:
        return self._processor[prio + 1:]
    
    
    # Returns all CPU that has a higher priority than the argument
    def higher_processors(self, prio: int) -> list[processor]:
        return self._processor[:prio]
    
    
    def __str__(self) -> str:
        string_result = ''
        index = 0
        for cpu in self._processor:
            string_result += f'P{index:d}: {cpu.__str__():s},\n'
            index += 1
        
        return f'{string_result:s}'