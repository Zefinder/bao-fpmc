# Imports
import sys
import importlib 
from analyse_utils import *
import matplotlib.pyplot as plt
import numpy as np
from typing import Any

# Constants
systick_freq = 3000
min_freq = 100
max_freq = 300
min_data_size = 40
max_data_size = 440
data_size_increment = 40

elapsed_time_array_varname_template = elapsed_time_array_varname_template_generator.format(template='{freq:d}Hz_{data_size:d}kB')
min_varname_template = min_varname_template_generator.format(template='{freq:d}Hz_{data_size:d}kB')
max_varname_template = max_varname_template_generator.format(template='{freq:d}Hz_{data_size:d}kB')

# Functions
def mesh_forward(x):
    return 3000/x


def mesh_inverse(x):
    return 3000/x


def generate_colormesh(title: str, x: list[int], y: list[int], z:list[list[int]]) -> None:
    # Set plot title
    plt.title(title)
    
    # Set X axis
    plt.xscale('function', functions=(mesh_forward, mesh_inverse))
    plt.gca().invert_xaxis()
    plt.xticks(x)
    plt.xlabel('Frequency (Hz)')
    
    # Set Y axis
    plt.yticks(y)
    plt.ylabel('Prefetch data size (kB)')
    
    # Create mesh
    c = plt.pcolormesh(x, y, z)
    plt.colorbar(c)


def generate_wcet_colormesh(varnames: dict[str,Any]) -> None:
    # Get values for X axis
    min_freq_ticks = systick_freq // min_freq
    max_freq_ticks = systick_freq // max_freq
    x = [systick_freq // tick for tick in range(min_freq_ticks, max_freq_ticks - 1, -1)]

    # Get values for Y axis
    y = [*range(min_data_size, max_data_size + 1, data_size_increment)]

    # Get all max values and put them into an array
    z = []
    for data_size in y:
        values_freq = []
        for freq in x:
            max_varname = max_varname_template.format(freq=freq, data_size=data_size)
            values_freq.append(varnames[max_varname])
        
        z.append(values_freq)

    # Set plot title and generate plot
    title = 'Worst case execution time for prefetching\nwith a 300Hz task and a variable task'
    generate_colormesh(title=title, x=x, y=y, z=z)
    
    
def generate_avg_colormesh(varnames: dict[str,Any]) -> None:
    # Get values for X axis
    min_freq_ticks = systick_freq // min_freq
    max_freq_ticks = systick_freq // max_freq
    x = [systick_freq // tick for tick in range(min_freq_ticks, max_freq_ticks - 1, -1)]

    # Get values for Y axis
    y = [*range(min_data_size, max_data_size + 1, data_size_increment)]

    # Get all max values and put them into an array
    z = []
    for data_size in y:
        values_freq = []
        for freq in x:
            elapsed_time_array_varname = elapsed_time_array_varname_template.format(freq=freq, data_size=data_size)
            elapsed_time_array = varnames[elapsed_time_array_varname]
            average = sum(elapsed_time_array) / len(elapsed_time_array)
            values_freq.append(average)
        
        z.append(values_freq)

    # Set plot title and generate plot
    title = 'Average execution time for prefetching\nwith a 300Hz task and a variable task'
    generate_colormesh(title=title, x=x, y=y, z=z)
    
    
def generate_diff_colormesh(varnames: dict[str,Any]) -> None:
    # Get values for X axis
    min_freq_ticks = systick_freq // min_freq
    max_freq_ticks = systick_freq // max_freq
    x = [systick_freq // tick for tick in range(min_freq_ticks, max_freq_ticks - 1, -1)]

    # Get values for Y axis
    y = [*range(min_data_size, max_data_size + 1, data_size_increment)]

    # Get all max values and put them into an array
    z = []
    for data_size in y:
        values_freq = []
        for freq in x:
            elapsed_time_array_varname = elapsed_time_array_varname_template.format(freq=freq, data_size=data_size)
            max_varname = max_varname_template.format(freq=freq, data_size=data_size)
            
            elapsed_time_array = varnames[elapsed_time_array_varname]
            average = sum(elapsed_time_array) / len(elapsed_time_array)
            max = varnames[max_varname]
            
            values_freq.append(max - average)
        
        z.append(values_freq)

    # Set plot title and generate plot
    title = 'Difference between worst and average execution time for prefetching\nwith a 300Hz task and a variable task'
    generate_colormesh(title=title, x=x, y=y, z=z)
    
    
def generate_std_colormesh(varnames: dict[str,Any]) -> None:
    # Get values for X axis
    min_freq_ticks = systick_freq // min_freq
    max_freq_ticks = systick_freq // max_freq
    x = [systick_freq // tick for tick in range(min_freq_ticks, max_freq_ticks - 1, -1)]

    # Get values for Y axis
    y = [*range(min_data_size, max_data_size + 1, data_size_increment)]

    # Get all max values and put them into an array
    z = []
    for data_size in y:
        values_freq = []
        for freq in x:
            elapsed_time_array_varname = elapsed_time_array_varname_template.format(freq=freq, data_size=data_size)
            elapsed_time_array = varnames[elapsed_time_array_varname]
            std = np.std(elapsed_time_array)
            
            values_freq.append(std)
        
        z.append(values_freq)

    # Set plot title and generate plot
    title = 'Standard variation of execution time\nwith a 300Hz task and a variable task'
    generate_colormesh(title=title, x=x, y=y, z=z)


def main():
    # Setting path to root folder
    sys.path.append('../')

    # Import extracted log file 
    extracted_log = importlib.import_module("extract.bench_2tasks_legacy-execution-2tasks-24-04-24-1")

    # Extract all variables 
    varnames = get_module_variables(extracted_log)

    # Generate worst case colormesh
    plt.figure('WCET', figsize=(12, 8))
    generate_wcet_colormesh(varnames=varnames)
    plt.savefig('../graphs/bench_2tasks_wcet.png')
    
    # Generate average colormesh
    plt.figure('AVG', figsize=(12, 8))
    generate_avg_colormesh(varnames=varnames)
    plt.savefig('../graphs/bench_2tasks_avg.png')
    
    # Generate worst - average colormesh
    plt.figure('WCET - AVG', figsize=(12, 8))
    generate_diff_colormesh(varnames=varnames)
    plt.savefig('../graphs/bench_2tasks_wcet-avg.png')
    
    # Generate standard deviation colormesh
    plt.figure('Standard deviation', figsize=(12, 8))
    generate_std_colormesh(varnames=varnames)
    plt.savefig('../graphs/bench_2tasks_stddev.png')

    
if __name__ == '__main__':
    main()