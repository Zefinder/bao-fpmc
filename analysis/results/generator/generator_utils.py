# Imports
from abc import abstractmethod
import os

# Constants
logs_directory = './results/'
results_directory = logs_directory + 'graphs/'


# class result_generator(object):
    
    
#     @classmethod
#     def from_module(cls, module):
#         pass
    
    
#     def __init__(self) -> None:
#         pass
    
    
#     @abstractmethod
#     def generate(self) -> None:
#         pass
    
    
#     def generate_results(self) -> None:
#         pass
    

def assert_existing_result_files(*filenames: str) -> bool:
    """
    Verifies that all log files that will be processed by the result generator exist.

    Args:
        *filenames (str): File name to verify, must be in the results directory

    Returns:
        bool: True if all files exist, False otherwise
    """ 
    result = True
        
    for filename in filenames:
        file = os.path.join(logs_directory, filename)
        result &= os.path.exists(file)
        
        if not result:
            break
        
    return result