# Imports
import sys
import importlib 
from analyse_utils import get_module_variables
import matplotlib.pyplot as plt
import numpy as np
from typing import Any

# Constants
frequency = 1000 # Hz
min_data_size = 20
max_data_size = 440
data_size_increment = 20

elapsed_time_array_varname_template = 'elapsed_time_array_{data_size:d}kB_{nop_number:d}nop'
min_varname_template = 'min_{data_size:d}kB_{nop_number:d}nop'
max_varname_template = 'max_{data_size:d}kB_{nop_number:d}nop'

# Functions
def get_best_min_nop_number(nop_log_varnames: dict[str,Any], data_size: int) -> np.intp:
    filtered_varnames = [v for k, v in nop_log_varnames.items() if k.startswith('min_' + str(data_size) + 'kB')]
    return np.argmin(filtered_varnames)


def get_best_max_nop_number(nop_log_varnames: dict[str,Any], data_size: int) -> np.intp:
    filtered_varnames = [v for k, v in nop_log_varnames.items() if k.startswith('max_' + str(data_size) + 'kB')]
    return np.argmin(filtered_varnames)


def get_best_avg_nop_number(nop_log_varnames: dict[str,Any], data_size: int) -> np.intp:
    filtered_varnames = [np.average(v) for k, v in nop_log_varnames.items() if k.startswith('elapsed_time_array_' + str(data_size) + 'kB')]
    return np.argmin(filtered_varnames)


def generate_colormesh(title: str, x: list[int], y: list[int], z: list[list[int]], cmap: str = 'viridis', vmax: int = None) -> None:
    # Set plot title
    plt.title(title)
    
    # Set X axis
    plt.xticks(x)
    plt.xlabel('Number of interfering core')
    
    # Set Y axis
    plt.yticks(y)
    plt.ylabel('Prefetch data size (kB)')
    
    # Create mesh
    c = plt.pcolormesh(x, y, z, cmap=cmap, vmax=vmax)
    plt.colorbar(c)
    

def generate_max_colormesh(no_interference_log_varname: dict[str,Any],
                           nop_max1_log_varnames: dict[str,Any],
                           nop_max2_log_varnames: dict[str,Any],
                           nop_max3_log_varnames: dict[str,Any]) -> None:    
    # Generate X range
    x = [*range(0, 4)]
    
    # Generate Y range
    y = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    # Get all values for min
    z = []
    for data_size in y:
        values = []
        
        # For no interference no search
        values.append(no_interference_log_varname[max_varname_template.format(data_size=data_size, nop_number=0)])
        
        # For other interferences, get the best nop value
        values.append(nop_max1_log_varnames[max_varname_template.format(data_size=data_size, nop_number=get_best_max_nop_number(nop_max1_log_varnames, data_size))])
        values.append(nop_max2_log_varnames[max_varname_template.format(data_size=data_size, nop_number=get_best_max_nop_number(nop_max2_log_varnames, data_size))])
        values.append(nop_max3_log_varnames[max_varname_template.format(data_size=data_size, nop_number=get_best_max_nop_number(nop_max3_log_varnames, data_size))])
        
        z.append(values)
    
    # Set plot title and generate plot
    title = 'Minimum of worst execution time (in µs) when increasing\nthe number of NOP during prefetch'
    generate_colormesh(title=title, x=x, y=y, z=z, cmap='terrain', vmax=550)
    
    
def generate_max_nop_colormesh(nop_max1_log_varnames: dict[str,Any],
                               nop_max2_log_varnames: dict[str,Any],
                               nop_max3_log_varnames: dict[str,Any]) -> None:
    # Generate X range
    x = [*range(1, 4)]
    
    # Generate Y range
    y = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    # Get all values for min
    z = []
    for data_size in y:
        values = []
        values.append(get_best_max_nop_number(nop_max1_log_varnames, data_size))
        values.append(get_best_max_nop_number(nop_max2_log_varnames, data_size))
        values.append(get_best_max_nop_number(nop_max3_log_varnames, data_size))
        
        z.append(values)
        
    # Set plot title and generate plot
    title = 'Optimal number of NOP to get minimal worst\nvalues during prefetch'
    generate_colormesh(title=title, x=x, y=y, z=z, cmap='Paired')
    

def generate_min_colormesh(no_interference_log_varname: dict[str,Any],
                           nop_min1_log_varnames: dict[str,Any],
                           nop_min2_log_varnames: dict[str,Any],
                           nop_min3_log_varnames: dict[str,Any],
                           nonop_min3_log_varnames: dict[str,Any]) -> None:
    # Merge no nop 3 to nop 3
    for no_nop_key in nonop_min3_log_varnames:
        nop_min3_log_varnames[no_nop_key] = nonop_min3_log_varnames[no_nop_key]
    
    # Generate X range
    x = [*range(0, 4)]
    
    # Generate Y range
    y = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    # Get all values for min
    z = []
    for data_size in y:
        values = []
        
        # For no interference no search
        values.append(no_interference_log_varname[min_varname_template.format(data_size=data_size, nop_number=0)])
        
        # For other interferences, get the best nop value
        values.append(nop_min1_log_varnames[min_varname_template.format(data_size=data_size, nop_number=get_best_min_nop_number(nop_min1_log_varnames, data_size))])
        values.append(nop_min2_log_varnames[min_varname_template.format(data_size=data_size, nop_number=get_best_min_nop_number(nop_min2_log_varnames, data_size))])
        values.append(nop_min3_log_varnames[min_varname_template.format(data_size=data_size, nop_number=get_best_min_nop_number(nop_min3_log_varnames, data_size))])
        
        z.append(values)
        
    # Set plot title and generate plot
    title = 'Minimum of best execution time (in µs) when increasing\nthe number of NOP during prefetch'
    generate_colormesh(title=title, x=x, y=y, z=z, cmap='terrain', vmax=550)
    
    
def generate_min_nop_colormesh(nop_min1_log_varnames: dict[str,Any],
                               nop_min2_log_varnames: dict[str,Any],
                               nop_min3_log_varnames: dict[str,Any],
                               nonop_min3_log_varnames: dict[str,Any]) -> None:
    # Merge no nop 3 to nop 3
    for no_nop_key in nonop_min3_log_varnames:
        nop_min3_log_varnames[no_nop_key] = nonop_min3_log_varnames[no_nop_key]
    
    # Generate X range
    x = [*range(1, 4)]
    
    # Generate Y range
    y = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    # Get all values for min
    z = []
    for data_size in y:
        values = []
        values.append(get_best_min_nop_number(nop_min1_log_varnames, data_size))
        values.append(get_best_min_nop_number(nop_min2_log_varnames, data_size))
        values.append(get_best_min_nop_number(nop_min3_log_varnames, data_size))
        
        z.append(values)
        
    # Set plot title and generate plot
    title = 'Optimal number of NOP to get minimal best\nvalues during prefetch'
    generate_colormesh(title=title, x=x, y=y, z=z, cmap='Paired')
    
    
def generate_avg_colormesh(no_interference_log_varname: dict[str,Any],
                           nop_min1_log_varnames: dict[str,Any],
                           nop_min2_log_varnames: dict[str,Any],
                           nop_min3_log_varnames: dict[str,Any],
                           nonop_min3_log_varnames: dict[str,Any]) -> None:
    # Merge no nop 3 to nop 3
    for no_nop_key in nonop_min3_log_varnames:
        nop_min3_log_varnames[no_nop_key] = nonop_min3_log_varnames[no_nop_key]
    
    # Generate X range
    x = [*range(0, 4)]
    
    # Generate Y range
    y = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    # Get all values for min
    z = []
    for data_size in y:
        values = []
        
        # For no interference no search
        values.append(np.average(no_interference_log_varname[elapsed_time_array_varname_template.format(data_size=data_size, nop_number=0)]))
        
        # For other interferences, get the best nop value
        values.append(np.average(nop_min1_log_varnames[elapsed_time_array_varname_template.format(data_size=data_size, nop_number=get_best_avg_nop_number(nop_min1_log_varnames, data_size))]))
        values.append(np.average(nop_min2_log_varnames[elapsed_time_array_varname_template.format(data_size=data_size, nop_number=get_best_avg_nop_number(nop_min2_log_varnames, data_size))]))
        values.append(np.average(nop_min3_log_varnames[elapsed_time_array_varname_template.format(data_size=data_size, nop_number=get_best_avg_nop_number(nop_min3_log_varnames, data_size))]))
        
        z.append(values)
        
    # Set plot title and generate plot
    title = 'Minimum of average execution time (in µs) when increasing\nthe number of NOP during prefetch'
    generate_colormesh(title=title, x=x, y=y, z=z, cmap='terrain', vmax=550)


def main():
    # Setting path to root folder
    sys.path.append('../')

    # Import extracted log files 
    no_interference_log = importlib.import_module('extract.bench_solo_legacy-execution-nop-24-05-07-1')
    nop_min1_log = importlib.import_module('extract.bench_interference1_nop-execution-nop-24-05-07-1')
    nop_min2_log = importlib.import_module('extract.bench_interference2_nop-execution-nop-24-05-06-1')
    nop_min3_log = importlib.import_module('extract.bench_interference3_nop-execution-nop-24-05-06-1')
    nonop_min3_log = importlib.import_module('extract.bench_interference3_nop-execution-nop-24-05-06-2')
    nop_max1_log = importlib.import_module('extract.bench_interference1_nop-execution-nop-24-05-13-1')
    nop_max2_log = importlib.import_module('extract.bench_interference2_nop-execution-nop-24-05-13-1')
    nop_max3_log = importlib.import_module('extract.bench_interference3_nop-execution-nop-24-05-07-1')
    
    # Extract variables
    no_interference_log_varname = get_module_variables(no_interference_log)
    nop_min1_log_varnames = get_module_variables(nop_min1_log)
    nop_min2_log_varnames = get_module_variables(nop_min2_log)
    nop_min3_log_varnames = get_module_variables(nop_min3_log)
    nonop_min3_log_varnames = get_module_variables(nonop_min3_log)
    nop_max1_log_varnames = get_module_variables(nop_max1_log)
    nop_max2_log_varnames = get_module_variables(nop_max2_log)
    nop_max3_log_varnames = get_module_variables(nop_max3_log)
    
    # Generate color mesh with max difference
    plt.figure('Max difference', figsize=(10, 11))
    generate_max_colormesh(no_interference_log_varname=no_interference_log_varname,
                           nop_max1_log_varnames=nop_max1_log_varnames,
                           nop_max2_log_varnames=nop_max2_log_varnames,
                           nop_max3_log_varnames=nop_max3_log_varnames)
    plt.savefig('../graphs/bench_max_nop_diff.png')
    
    # Generate color mesh with optimal number of nop
    plt.figure('Min NOP number for worst', figsize=(10, 11))
    generate_max_nop_colormesh(nop_max1_log_varnames=nop_max1_log_varnames,
                               nop_max2_log_varnames=nop_max2_log_varnames,
                               nop_max3_log_varnames=nop_max3_log_varnames)
    plt.savefig('../graphs/bench_max_nop_number.png')
    
    # Generate color mesh with min difference
    plt.figure('Min difference', figsize=(10, 11))
    generate_min_colormesh(no_interference_log_varname=no_interference_log_varname,
                           nop_min1_log_varnames=nop_min1_log_varnames,
                           nop_min2_log_varnames=nop_min2_log_varnames,
                           nop_min3_log_varnames=nop_min3_log_varnames,
                           nonop_min3_log_varnames=nonop_min3_log_varnames)
    plt.savefig('../graphs/bench_min_nop_diff.png')
    
    # Generate color mesh with optimal number of nop
    plt.figure('Min NOP number for best', figsize=(10, 11))
    generate_min_nop_colormesh(nop_min1_log_varnames=nop_min1_log_varnames,
                               nop_min2_log_varnames=nop_min2_log_varnames,
                               nop_min3_log_varnames=nop_min3_log_varnames,
                               nonop_min3_log_varnames=nonop_min3_log_varnames)
    plt.savefig('../graphs/bench_min_nop_number.png')
    
    # Generate color mesh with min difference
    plt.figure('Avg difference', figsize=(10, 11))
    generate_avg_colormesh(no_interference_log_varname=no_interference_log_varname,
                           nop_min1_log_varnames=nop_min1_log_varnames,
                           nop_min2_log_varnames=nop_min2_log_varnames,
                           nop_min3_log_varnames=nop_min3_log_varnames,
                           nonop_min3_log_varnames=nonop_min3_log_varnames)
    plt.savefig('../graphs/bench_avg_nop_diff.png')
    
    # plt.show()
    
    
if __name__ == '__main__':
    main()
